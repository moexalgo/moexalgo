from typing import Iterable, Any

from moexalgo.features.algopack import AlgopackMarketMixin, AlgopackTickerMixin
from moexalgo.features.common import CommonMarket, CommonTicker
from moexalgo.features.extramarket import ExtraMarketMixin
from moexalgo.utils import DataFrame

SHARES_TICKERS_DEFAULT_FIELDS = (
    "shortname",  # Краткое наименование
    "lotsize",  # Размер лота
    "decimals",  # Количество знаков после запятой
    "minstep",  # Минимальный шаг цены
    "issuesize",  # Объем выпуска
    "isin",  # Стандартное наименование
    "regnumber",  # Регистрационный номер
    "listlevel",  # Уровень листинга
)

SHARES_MARKETS_DEFAULT_FIELDS = (
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


class Market(CommonMarket, ExtraMarketMixin, AlgopackMarketMixin):
    """
    Обобщенный класс `Market` для рынка ценных бумаг.
    """

    def __init__(self, *args, **kwargs):
        super().__init__("stock", *args, **kwargs)

    def tickers(self, *fields: str, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        match self.market:
            case "shares":
                fields = () if "*" in fields else (fields or SHARES_TICKERS_DEFAULT_FIELDS)
            case _:
                fields = () if "*" in fields else fields
        return super().tickers(*fields, native=native)

    def marketdata(self, *fields: str, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        match self.market:
            case "shares":
                fields = () if "*" in fields else (fields or SHARES_MARKETS_DEFAULT_FIELDS)
            case _:
                fields = () if "*" in fields else fields
        return super().marketdata(*fields, native=native)


class Ticker(CommonTicker, AlgopackTickerMixin):
    """
    Обобщенный класс `Ticker` для 'stock'.
    """
