from datetime import date
from typing import Any, Iterable

from moexalgo.session import Session
from moexalgo.tools import resample
from moexalgo.utils import (
    DataFrame,
    result_adapter,
    normalize_data,
    CandlePeriod,
    normalize_period,
    prepare_from_till_dates,
    calc_offset_limit,
)


class CommonMarket:
    """
    Обобщенный класс `Market`

    Notes
    -----
    При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
    Используйте в методах флаг `native` что бы отменить такое поведение.
    """

    def __init__(self, engine: str, market: str, boardid: str, features: dict[str, str]):
        self.features = features
        self.market = market
        self.boardid = boardid
        self.engine = engine

    def _get_path_for(self, feature):
        if path := self.features.get(feature):
            return path
        raise NotImplementedError(f"Methods of `{feature}` is not implemented for this endpoint.")

    def tickers(
        self,
        *fields: str,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает информация о всех инструментах рынка.

        Parameters
        ----------
        fields :
            Поля для отображения; "*" все поля
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        fields = () if "*" in fields else fields
        return result_adapter(
            normalize_data(fetch_securities(self.engine, self.market, self.boardid), *fields), native
        )

    def marketdata(
        self,
        *fields: str,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает статистическую информацию о всех инструментах рынка.

        Parameters
        ----------
        fields :
            Поля для отображения; "*" все поля
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        fields = () if "*" in fields else fields
        return result_adapter(
            normalize_data(fetch_securities(self.engine, self.market, self.boardid, "marketdata"), *fields), native
        )

    def __getattr__(self, name: str):
        if name in ("candles", "trades"):
            raise NotImplementedError(f"Method `{name}` not implemented for `{self.market}`")
        return self.__getattribute__(name)


def fetch_securities(engine, market: str, boardid: str, section: str = "securities") -> Iterable[dict[str, Any]]:
    with Session() as client:
        return client.get_objects(
            f"engines/{engine}/markets/{market}/boards/{boardid}/securities",
            lambda data: data[section],
        )


INFO_DEFAULT_FIELDS = (
    "title",
    "is_primary",
    "decimals",
    "is_traded",
    "market",
    "engine",
    "listed_from",
    "listed_till",
    "unit",
)


class CommonTicker:
    """
    Обобщенный класс `Ticker`

    Notes
    -----
    При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
    Используйте в методах флаг `native` что бы отменить такое поведение.
    """

    def __init__(self, market: CommonMarket, boardid: str, secid: str, decimals: int, delisted: bool):
        self.market = market
        self.boardid = boardid
        self.secid = secid
        self.decimals = decimals
        self.delisted = delisted

    def info(
        self,
        *fields: str,
        native: bool = False,
    ) -> dict[str, Any] | DataFrame:
        """
        Информация об инструменте.

        Parameters
        ----------
        fields :
            Поля для отображения; "*" все поля
        native :
            Если флаг выставлен в `True` всегда возвращается словарь.
        """

        fields = (() if "*" in fields else fields) or INFO_DEFAULT_FIELDS

        def fetch():
            with Session() as client:
                data = normalize_data(client.get_objects(f"securities/{self.secid}", lambda data: data["boards"]))
                return [item for item in data if item["ticker"] == self.secid]

        return result_adapter(normalize_data(fetch(), *fields), native)

    def candles(
        self,
        start: str | date,
        end: str | date,
        period: str | int | CandlePeriod | None = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает свечи инструмента по заданным параметрам.

        Parameters
        ----------
        start:
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        period:
            Период свечи, возможны следующие строковые значения: '1min', '5min', '10min', '15min', '20min',
            '30min', '1h', '2h', '3h', '6h', '12h', '1D', '5D', '10D', '1W', '2W', '4W', '1M'; и числовые:
            1 (1 минута), 10 (10 минут), 60 (1 час), 24 (1 день), 7 (1 неделя), 31 (1 месяц).
        offset :
            Начальная позиция в последовательности записей, by default 0.
        latest :
            Включает режим выдачи последних `latest` записей в наборе, by default False.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        resample_to = None
        try:
            interval = normalize_period(period)
        except (ValueError, TypeError):
            interval, resample_to, period = resample.normalize_period(period)
        from_date, till_date = prepare_from_till_dates(start, end)
        options = {"from": from_date, "till": till_date, "interval": interval}
        offset, limit = calc_offset_limit(offset, 10_000)
        if latest:
            options["iss.reverse"] = True
            limit = 1
        options = dict(options, offset=offset, limit=limit)
        candles = fetch_section(
            self.market.engine,
            self.market.market,
            self.boardid,
            self.secid,
            "candles",
            **options,
        )
        return result_adapter(resample.candles(candles, resample_to) if resample_to is not None else candles, native)

    def trades(
        self,
        tradeno: int = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает сделки за последний день или начиная с заданного `tradeno`.

        Parameters
        ----------
        tradeno :
            Номер сделки с которого выдаются данные, если не задано, то с начала дня.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        key = "recno" if self.market in ("forts", "options") else "tradeno"
        options = {key: tradeno}
        offset, limit = calc_offset_limit(offset, 10_000)
        if latest:
            options["reversed"] = 1
            limit = 1
        options = dict(options, offset=offset, limit=limit)
        return result_adapter(
            fetch_section(self.market.engine, self.market.market, self.boardid, self.secid, "trades", **options),
            native,
        )

    def orderbook(self, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает текущий стакан лучших цен.

        Parameters
        ----------
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        options = dict(offset=0, limit=-1)
        return result_adapter(
            fetch_section(self.market.engine, self.market.market, self.boardid, self.secid, "orderbook", **options),
            native,
        )


def fetch_section(
    engine: str,
    market: str,
    boardid: str,
    secid: str,
    section: str,
    *,
    limit: int,
    offset: int = 0,
    **options: Any,
) -> Iterable[dict[str, Any]]:
    start = offset
    with Session() as client:
        while True:
            options["start"] = start
            if data := normalize_data(
                client.get_objects(
                    f"engines/{engine}/markets/{market}/boards/{boardid}/securities/{secid}/{section}",
                    lambda data: data[section],
                    **options,
                )
            ):
                for item in data:
                    yield item
                    start += 1
                if (start - offset) < limit and limit > 0:
                    continue
            break
