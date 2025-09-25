import typing as t
from datetime import date

from pandas import DataFrame

from moexalgo.next import protocols
from moexalgo.next.protocols import CandlePeriod
from ._common import Market as CommonMarket, Ticker as CommonTicker


class Market(CommonMarket, protocols.Market):
    """
    Обобщенный класс `Market` для 'stock'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__("stock", *args, **kwargs)

    def tickers(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        SHARES_DEFAULT_FIELDS = (
            "shortname",  # Краткое наименование
            "lotsize",  # Размер лота
            "decimals",  # Количество знаков после запятой
            "minstep",  # Минимальный шаг цены
            "issuesize",  # Объем выпуска
            "isin",  # Стандартное наименование
            "regnumber",  # Регистрационный номер
            "listlevel",  # Уровень листинга
        )
        match self.market:
            case "shares":
                fields = fields or SHARES_DEFAULT_FIELDS if not all_fields else ()
        return super()._tickers(*fields, all_fields=all_fields, native=native)

    def marketdata(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        SHARES_DEFAULT_FIELDS = (
            "bid",  # Лучшая цена покупки
            "offer",  # Лучшая цена продажи
            "biddeptht",  # Глубина стакана покупки
            "offerdeptht",  # Глубина стакана продажи
            "open",  # Цена открытия
            "high",  # Максимальная цена
            "low",  # Минимальная цена
            "last",  # Цена последней сделки
            "waprice",  # Средневзвешенная цена
            "lasttoprevprice",  # Изменение цены последней сделки к предыдущей
            "numtrades",  # Количество сделок
            "voltoday",  # Объем сделок за день
            "valtoday",  # Объем сделок за день в валюте
            "valtoday_usd",  # Объем сделок за день в долларах
            "openperiodprice",  # Цена открытия периода
            "closingauctionprice",  # Цена закрытия аукциона
            "closingauctionvolume",  # Объем закрытия аукциона
            "issuecapitalization",  # Капитализация
            "updatetime",  # Время обновления
            "systime",  # Время системы
        )
        match self.market:
            case "shares":
                fields = fields or SHARES_DEFAULT_FIELDS if not all_fields else ()
        return super()._marketdata(*fields, all_fields=all_fields, native=native)


class Ticker(CommonTicker, protocols.Ticker):
    """
    Обобщенный класс `Ticker` для 'stock'.
    """

    def info(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> dict[str, t.Any] | DataFrame:
        return super()._info(*fields, all_fields=all_fields, native=native)

    def candles(
        self,
        start: str | date,
        end: str | date,
        period: int | str | CandlePeriod = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        return super()._candles(start, end, period, offset=offset, latest=latest, native=native)

    def trades(
        self,
        tradeno: int = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        return super()._trades(tradeno, offset=offset, latest=latest, native=native)

    def orderbook(self, native: bool = False) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        return super()._orderbook(native)
