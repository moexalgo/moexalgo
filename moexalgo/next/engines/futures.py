import typing as t
from datetime import date

from pandas import DataFrame

from moexalgo.next import protocols
from moexalgo.next.protocols import CandlePeriod
from ._common import Market as CommonMarket, Ticker as CommonTicker


class Market(CommonMarket, protocols.Market):
    """
    Обобщенный класс `Market` для 'futures'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__("futures", *args, **kwargs)

    def tickers(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        return super()._tickers(*fields, all_fields=all_fields, native=native)

    def marketdata(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        return super()._marketdata(*fields, all_fields=all_fields, native=native)


class Ticker(CommonTicker, protocols.Ticker):
    """
    Обобщенный класс `Ticker` для 'futures'.
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
