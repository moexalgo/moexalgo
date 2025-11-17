from typing import Iterable, Any

from moexalgo.features.algopack import AlgopackTickerMixin, AlgopackMarketMixin
from moexalgo.features.common import CommonMarket, CommonTicker
from moexalgo.features.extramarket import ExtraMarketMixin
from moexalgo.features.futoi import FutOIMarketMixin, FutOITickerMixin
from moexalgo.utils import DataFrame

FORTS_TICKERS_DEFAULT_FIELDS = (
    "sectype",
    "assetcode",
    "shortname",  # Краткое наименование
    "lotvolume",  # Размер лота
    "decimals",  # Количество знаков после запятой
    "minstep",  # Минимальный шаг цены
    "initialmargin",
    "lasttradedate",
)

FORTS_MARKET_DEFAULT_FIELDS = (
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


class Market(CommonMarket, ExtraMarketMixin, AlgopackMarketMixin, FutOIMarketMixin):
    """
    Обобщенный класс `Market` для срочного рынка.
    """

    def __init__(self, *args, **kwargs):
        super().__init__("futures", *args, **kwargs)

    def tickers(self, *fields: str, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        match self.market:
            case "forts":
                fields = () if "*" in fields else (fields or FORTS_TICKERS_DEFAULT_FIELDS)
            case _:
                fields = () if "*" in fields else fields
        return super().tickers(*fields, native=native)

    def marketdata(self, *fields: str, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        match self.market:
            case "forts":
                fields = () if "*" in fields else (fields or FORTS_MARKET_DEFAULT_FIELDS)
            case _:
                fields = () if "*" in fields else fields
        return super().marketdata(*fields, native=native)

    def trades(
        self: CommonMarket,
        recno: int | None = None,
        *,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает последние сделки в обратной сортировке если `recno` не заданно.
        Если заданно сделки возвращаются от заданного `recno`.

        Parameters
        ----------
        recno :
            Номер порядка заключения сделок, если не задано.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        return super().trades(recno, native=native)


class Ticker(CommonTicker, AlgopackTickerMixin, FutOITickerMixin):
    """
    Обобщенный класс `Ticker` для срочного рынка.
    """

    def trades(
        self,
        recno: int | None = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает сделки за последний день или начиная с заданного `recno`.

        Parameters
        ----------
        recno :
            Номер порядка заключения сделок, если не задано.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        return super().trades(recno, offset=offset, latest=latest, native=native)
