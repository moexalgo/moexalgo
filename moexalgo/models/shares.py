from dataclasses import dataclass
from datetime import datetime, date, time
from decimal import Decimal


@dataclass
class Securities:
    """ Элемент блока данных `securities`

    Attributes
    ----------
    shortname: str
        Краткое наименование ценной бумаги
    prevprice: Decimal
        Цена последней сделки нормального периода предыдущего торгового дня
    lotsize: int
        Количество ценных бумаг в одном стандартном лоте
    facevalue: Decimal
        Номинальная стоимость одной ценной бумаги, в валюте инструмента
    status: str
        Индикатор "торговые операции разрешены/запрещены"
    boardname: str
        Режим торгов
    decimals: int
        Точность, знаков после запятой
    secname: Decimal
        Наименование финансового инструмента
    remarks: str
        Примечание
    marketcode: str
        Идентификатор рынка на котором торгуется финансовый инструмент
    instrid: str
        Группа инструментов
    sectorid: str
        Сектор (Устарело)
    minstep: Decimal
        Минимально возможная разница между ценами, указанными в заявках на покупку/продажу ценных бумаг
    prevwaprice: Decimal
        Значение оценки (WAPRICE) предыдущего торгового дня
    faceunit: str
        Код валюты, в которой выражен номинал ценной бумаги
    prevdate: date
        Дата предыдущего торгового дня
    issuesize: int
        Объем выпуска
    isin: str
        Международный идентификационный код ценной бумаги
    latname: str
        Наименование финансового инструмента на английском языке
    regnumber: str
        Номер государственной регистрации
    prevlegalcloseprice: Decimal
        Официальная цена закрытия предыдущего дня, рассчитываемая по методике ФСФР
    currencyid: str
        Валюта расчетов
    sectype: str
        Тип ценной бумаги
    listlevel: int
        Уровень листинга
    settledate: date
        Дата расчетов сделки
    """
    shortname: str
    prevprice: Decimal
    lotsize: int
    facevalue: Decimal
    status: str
    boardname: str
    decimals: int
    secname: Decimal
    remarks: str
    marketcode: str
    instrid: str
    sectorid: str
    minstep: Decimal
    prevwaprice: Decimal
    faceunit: str
    prevdate: date
    issuesize: int
    isin: str
    latname: str
    regnumber: str
    prevlegalcloseprice: Decimal
    currencyid: str
    sectype: str
    listlevel: int
    settledate: date


@dataclass
class MarketData:
    """ Элемент блока данных `marketdata`

    Parameters
    ----------
    bid: Decimal
        Лучшая котировка на покупку (Спрос)
    biddepth: int
        Объем заявок на покупку по лучшей котировке, выраженный в лотах
    offer: Decimal
        Лучшая котировка на продажу (Предложение)
    offerdepth: int
        Объем заявок на продажу по лучшей котировке, выраженный в лотах
    spread: Decimal
        Разница между лучшей котировкой на продажу и покупку (спред), руб.
    biddeptht: int
        Объем всех заявок на покупку в очереди Торговой Системы, выраженный в лотах
    offerdeptht: int
        Объем всех заявок на продажу в очереди Торговой Системы, выраженный в лотах
    open: Decimal
        Цена первой сделки
    low: Decimal
    	Минимальная цена сделки
    high: Decimal
        Максимальная цена сделки
    last: Decimal
        Цена последней сделки
    lastchange: Decimal
        Изменение цены последней сделки к цене предыдущей сделки, рублей
    lastchangeprcnt: Decimal
        Изменение цены последней сделки к цене предыдущей сделки, %
    qty: int
        Объем последней сделки, в лотах
    value: Decimal
        Объем последней сделки, в руб.
    value_usd: Decimal
        Объем последней сделки, дол. США
    waprice: Decimal
        	Средневзвешенная цена
    lastcngtolastwaprice: Decimal
        Изменение цены последней сделки к средневзвешенной цене, рублей
    waptoprevwapriceprcnt: Decimal
        Изменение средневзвешенной цены относительно средневзвешенной цены предыдущего торгового дня, %
    waptoprevwaprice: Decimal
        Изменение средневзвешенной цены к средневзвешенной цене предыдущего торгового дня, рублей
    closeprice: Decimal
        Цена послеторгового периода
    marketpricetoday: Decimal
        Рыночная цена по результатам торгов сегодняшнего дня, за одну ценную бумагу
    marketprice: Decimal
        Рыночная цена ценной бумаги по результатам торгов предыдущего дня, за одну ценную бумагу
    lasttoprevprice: Decimal
        Изменение цены последней сделки к последней цене предыдущего дня, %
    numtrades: int
        Количество сделок за торговый день
    voltoday: int
        Объем совершенных сделок, выраженный в единицах ценных бумаг
    valtoday: int
        Объем совершенных сделок, в валюте расчетов
    valtoday_usd: int
        Объем заключенных сделок, дол. США
    etfsettleprice: Decimal
        Расчетная стоимость акции/пая иностранного биржевого инвестиционного фонда
    tradingstatus: str
        Индикатор состояния торговой сессии по инструменту
    updatetime: time
        Время последнего обновления
    lastbid: Decimal
        Лучшая котировка на покупку на момент завершения нормального периода торгов
    lastoffer: Decimal
        Лучшая котировка на продажу на момент завершения нормального периода торгов
    lcloseprice: Decimal
        Официальная цена закрытия, рассчитываемая по методике ФСФР как средневзвешенная цена сделок за последние 10 минут торговой сессии, включая сделки послеторгового периода
    lcurrentprice: Decimal
        Официальная текущая цена, рассчитываемая как средневзвешенная цена сделок заключенных за последние 10 минут
    marketprice2: Decimal
        Рыночная цена 2, рассчитываемая в соответствии с методикой ФСФР
    numbids: int
        Количество заявок на покупку в очереди Торговой системы
    numoffers: int
        Количество заявок на продажу в очереди Торговой системы
    change: Decimal
        Изменение цены последней сделки по отношению к цене последней сделки предыдущего торгового дня
    time: time
        Время заключения последней сделки
    highbid: Decimal
        Наибольшая цена спроса в течение торговой сессии
    lowoffer: Decimal
        Наименьшая цена предложения в течение торговой сессии
    priceminusprevwaprice: Decimal
        Цена последней сделки к оценке предыдущего дня
    openperiodprice: Decimal
        Цена предторгового периода
    seqnum: int
        номер обновления (служебное поле)
    systime: datetime
        Время загрузки данных системой
    closingauctionprice: Decimal
        Цена послеторгового аукциона.
        В течение аукциона отображает ожидаемую цену аукциона с учетом всех зарегистрированных на текущий момент заявок.
        После завершения аукциона отображает цену состоявшегося аукциона.
    closingauctionvolume: Decimal
        Количество в сделках послеторгового аукциона.
        Ожидаемое (состоявшееся) количество лотов в сделках по указанной цене послеторгового аукциона.
    issuecapitalization: Decimal
        Текущая капитализация акции
    issuecapitalization_updatetime: time
        Время обновления капитализации
    etfsettlecurrency: str
        Валюта расчетной стоимости акции/пая иностранного биржевого инвестиционного фонда
    valtoday_rur:
        Объем совершенных сделок, рублей
    tradingsession: str
        Торговая сессия
    """
    bid: Decimal
    biddepth: int
    offer: Decimal
    offerdepth: int
    spread: Decimal
    biddeptht: int
    offerdeptht: int
    open: Decimal
    low: Decimal
    high: Decimal
    last: Decimal
    lastchange: Decimal
    lastchangeprcnt: Decimal
    qty: int
    value: Decimal
    value_usd: Decimal
    waprice: Decimal
    lastcngtolastwaprice: Decimal
    waptoprevwapriceprcnt: Decimal
    waptoprevwaprice: Decimal
    closeprice: Decimal
    marketpricetoday: Decimal
    marketprice: Decimal
    lasttoprevprice: Decimal
    numtrades: int
    voltoday: int
    valtoday: int
    valtoday_usd: int
    etfsettleprice: Decimal
    tradingstatus: str
    updatetime: time
    lastbid: Decimal
    lastoffer: Decimal
    lcloseprice: Decimal
    lcurrentprice: Decimal
    marketprice2: Decimal
    numbids: int
    numoffers: int
    change: Decimal
    time: time
    highbid: Decimal
    lowoffer: Decimal
    priceminusprevwaprice: Decimal
    openperiodprice: Decimal
    seqnum: int
    systime: datetime
    closingauctionprice: Decimal
    closingauctionvolume: Decimal
    issuecapitalization: Decimal
    issuecapitalization_updatetime: time
    etfsettlecurrency: str
    valtoday_rur: int
    tradingsession: str


@dataclass
class OrderBookItem:
    """Активные заявки

    Attributes
    ----------
    secid : str
        Код инструмента
    boardid : str
        Код режима торгов
    buysell : str
        Направленность заявки, приведшая к заключению сделки (покупка\продажа)
    price : float
        Цена котировки
    quantity : int
        Объем котировки, лотов
    seqnum : int
        номер обновления (служебное поле
    updatetime : time
        Время последнего обновления
    decimals : int
        Точность, знаков после запятой
    """
    secid: str
    boardid: str
    buysell: str
    price: float
    quantity: int
    seqnum: int
    updatetime: time
    decimals: int
