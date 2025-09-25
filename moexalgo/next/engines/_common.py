import typing as t
from collections.abc import Iterable
from datetime import date

from moexalgo.candles import normalize_period
from moexalgo.metrics import prepare_from_till_dates, calc_offset_limit
from moexalgo.next.protocols import DataFrame, CandlePeriod
from moexalgo.session import Session

pd = None
if not isinstance(DataFrame, t.TypeAliasType):
    import pandas as pd


class Market:
    """
    Обобщенный класс `Market`
    """

    def __init__(self, engine: str, market: str, boardid: str):
        self.market = market
        self.boardid = boardid
        self.engine = engine

    def _tickers(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
        default_fields: list[str] = None,
    ) -> Iterable[dict[str, t.Any]] | DataFrame:
        if not fields:
            if default_fields:
                fields = default_fields
            else:
                all_fields = True

        def fetch():
            with Session() as client:
                data = client.get_objects(
                    f"engines/{self.engine}/markets/{self.market}/boards/{self.boardid}/securities",
                    lambda data: [dict(zip(data["securities"]["columns"], row)) for row in data["securities"]["data"]],
                )
                for item in data:
                    yield normalize_item(item, *fields)

        return result_adapter(fetch(), native)

    def _marketdata(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
        default_fields: list[str] = None,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        if not fields:
            if default_fields:
                fields = default_fields
            else:
                all_fields = True

        def fetch():
            with Session() as client:
                data = client.get_objects(
                    f"engines/{self.engine}/markets/{self.market}/boards/{self.boardid}/securities",
                    lambda data: [dict(zip(data["marketdata"]["columns"], row)) for row in data["marketdata"]["data"]],
                )
                for item in data:
                    yield normalize_item(item, *fields)

        return result_adapter(fetch(), native)


class Ticker:
    """
    Обобщенный класс `Ticker`
    """

    def __init__(self, market: Market, boardid: str, secid: str, decimals: int, delisted: bool):
        self.market = market
        self.boardid = boardid
        self.secid = secid
        self.decimals = decimals
        self.delisted = delisted

    def _info(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
        default_fields: list[str] = None,
    ) -> dict[str, t.Any] | DataFrame:
        if not fields:
            if default_fields:
                fields = default_fields
            else:
                all_fields = True

        def fetch():
            with Session() as client:
                data = client.get_objects(
                    f"securities/{self.secid}",
                    lambda data: [dict(zip(data["boards"]["columns"], row)) for row in data["boards"]["data"]],
                )
                for item in data:
                    if item["secid"] == self.secid:
                        yield normalize_item(item, *fields)

        return result_adapter(fetch(), native)

    def _candles(
        self,
        start: str | date,
        end: str | date,
        period: int | str | CandlePeriod = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        interval_seconds = normalize_period(period)
        from_date, till_date = prepare_from_till_dates(start, end)
        options = {"from": from_date, "till": till_date, "interval": interval_seconds}
        offset, limit = calc_offset_limit(offset, None)
        if latest:
            options["iss.reverse"] = True
            limit = 1
        options = dict(options, offset=offset, limit=limit)

        def fetch():
            for item in fetch_section(
                self.market.engine,
                self.market.market,
                self.boardid,
                self.secid,
                "candles",
                **options,
            ):
                yield normalize_item(item)

        return result_adapter(fetch(), native)

    def _trades(
        self,
        tradeno: int = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        options = {"tradeno": tradeno}
        offset, limit = calc_offset_limit(offset, None)
        if latest:
            options["iss.reverse"] = True
            limit = 1
        options = dict(options, offset=offset, limit=limit)

        def fetch():
            for item in fetch_section(
                self.market.engine,
                self.market.market,
                self.boardid,
                self.secid,
                "trades",
                **options,
            ):
                yield normalize_item(item)

        return result_adapter(fetch(), native)

    def _orderbook(self, native: bool = False) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        options = dict(offset=0, limit=-1)

        def fetch():
            for item in fetch_section(
                self.market.engine,
                self.market.market,
                self.boardid,
                self.secid,
                "orderbook",
                **options,
            ):
                yield normalize_item(item)

        return result_adapter(fetch(), native)


def normalize_item(item: dict[str, t.Any], *fields: tuple[str | tuple[str, str]]) -> dict[str, t.Any]:
    names = {"secid": "ticker", "boardid": "board"}
    if fields:
        names.update(dict(((item, item) if isinstance(item, str) else item) for item in fields))

    def normalize_name(name: str) -> str:
        name = name.lower()
        return names.get(name, name)

    pre_result = [(normalize_name(k), v) for k, v in item.items()]
    names = tuple(names.values())
    return dict((k, v) for k, v in pre_result if len(fields) == 0 or k in names)


def fetch_section(
    engine: str,
    market: str,
    boardid: str,
    secid: str,
    section: str,
    *,
    limit: int,
    offset: int = 0,
    **options: t.Any,
) -> t.Iterable[dict[str, t.Any]]:
    start = offset
    with Session() as client:
        while True:
            options["start"] = start
            if data := client.get_objects(
                f"engines/{engine}/markets/{market}/boards/{boardid}/securities/{secid}/{section}",
                lambda data: [dict(zip(data[section]["columns"], row)) for row in data[section]["data"]],
                **options,
            ):
                for item in data:
                    yield item
                    start += 1
                if (start - offset) < limit and limit > 0:
                    continue
            break


def result_adapter(result: dict | t.Iterable[dict], native: bool) -> dict | t.Iterable[dict] | DataFrame | None:
    """Преобразует результат в `pandas.DataFrame` если применимо."""
    use_dataframe = not native and pd is not None
    if use_dataframe:
        if result is None:
            return None
        result = pd.DataFrame([result] if isinstance(result, dict) else list(result))
    return result
