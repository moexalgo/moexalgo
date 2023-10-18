from dataclasses import dataclass
from datetime import datetime, date, time
from decimal import Decimal


@dataclass
class Securities:
    """ Элемент блока данных `securities`

    Attributes
    ----------
    name: str
        Наименоваание
    decimals: int
        Точность, знаков после запятой
    shortname: str
        Наименование индекса
    annualhigh: Decimal
        Максимальное значение индекса за год
    annuallow: Decimal
        Минимальное значение индекса за год
    currencyid: str
        Валюта расчета
    calcmode: str
        Принцип расчета
    """
    name: str
    decimals: int
    shortname: str
    annualhigh: Decimal
    annuallow: Decimal
    currencyid: str
    calcmode: str


@dataclass
class MarketData:
    """ Элемент блока данных `marketdata`

    Attributes
    ----------
    lastvalue: Decimal
        Последнее значение индекса предыдущего торгового дня
    openvalue: Decimal
        Открытие текущего торгового дня, пунктов
    currentvalue: Decimal
        Текущее значение
    lastchange: Decimal
        Изменение текущего значения к значению предыдущего торгового дня, пунктов
    lastchangetoopenprc: Decimal
        Изменение к открытию текущего торгового дня, %
    lastchangetoopen: Decimal
        Изменение к открытию текущего торгового дня, пунктов
    updatetime: time
        Время последнего обновления
    lastchangeprc: Decimal
        Изменение текущего значения к значению предыдущего торгового дня, %
    valtoday: Decimal
        Объем торгов по бумагам из базы расчета за день, руб
    monthchangeprc: Decimal
        Изменение с начала календарного месяца, %
    yearchangeprc: Decimal
        Изменение с начала календарного года
    seqnum: int
        номер обновления (служебное поле
    systime: datetime
        Время загрузки данных системой
    time: time
        Время
    valtoday_usd: Decimal
        Объем торгов по бумагам из базы расчета за день, дол. США
    lastchangebp: Decimal
        Изменение текущего значения к значению предыдущего торгового дня, базисных пунктов
    monthchangebp: Decimal
        Изменение с начала календарного месяца, базисных пунктов
    yearchangebp: Decimal
        Изменение с начала календарного года, базисных пунктов
    capitalization: Decimal
        Капитализация бумаг, входящих в индекс, руб
    capitalization_usd: Decimal
        Капитализация бумаг, входящих в индекс, в дол. США
    high: Decimal
        Максимальное значение индекса за сессию
    low: Decimal
        Минимальное значение индекса за сессию
    tradedate: date
        Дата торгов
    tradingsession: str
        Торговая сессия
    voltoday: Decimal
        Объем сделок. Для товарных индексов – в тоннах
    """
    lastvalue: Decimal
    openvalue: Decimal
    currentvalue: Decimal
    lastchange: Decimal
    lastchangetoopenprc: Decimal
    lastchangetoopen: Decimal
    updatetime: time
    lastchangeprc: Decimal
    valtoday: Decimal
    monthchangeprc: Decimal
    yearchangeprc: Decimal
    seqnum: int
    systime: datetime
    time: time
    valtoday_usd: Decimal
    lastchangebp: Decimal
    monthchangebp: Decimal
    yearchangebp: Decimal
    capitalization: Decimal
    capitalization_usd: Decimal
    high: Decimal
    low: Decimal
    tradedate: date
    tradingsession: str
    voltoday: Decimal
