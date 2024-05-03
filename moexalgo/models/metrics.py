# DEPRECATED!
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class TradeStat:
    """ Метрика "Статистика торгов"

    Attributes
    ----------
    secid: str
        Код инструмента
    ts: datetime
        Дата/время данных
    pr_open: Decimal
        Цена открытия за период
    pr_high: Decimal
        Макс цена за период
    pr_low: Decimal
        Минимальная цена за период
    pr_close: Decimal
        Цена закрытия за период
    pr_change: Decimal
        Изменение цены за период, %
    trades: int
        Кол-во сделок
    vol: int
        Объем бумаг, лот
    val: Decimal
        Объем бумаг, руб.
    pr_std: Decimal
        Стандартное отклонение цены
    disb: Decimal
        Соотношение объема продавец/покупатель
    pr_vwap: Decimal
        Средневзвешенная цена
    trades_b: int
        Кол-во сделок на покупку
    vol_b: int
        Объем покупок, лот
    val_b: Decimal
        Объем покупок, руб.
    pr_vwap_b: Decimal
        Цена покупки средневзвешенная
    trades_s: int
        Кол-во сделок на продажу
    vol_s: int
        Объем продаж, лот
    val_s: Decimal
        Объем продаж, руб.
    pr_vwap_s: Decimal
        Цена продажи средневзвешенная
    """
    secid: str
    ts: datetime
    pr_open: Decimal
    pr_high: Decimal
    pr_low: Decimal
    pr_close: Decimal
    pr_change: Decimal
    trades: int
    vol: int
    val: Decimal
    pr_std: Decimal
    disb: Decimal
    pr_vwap: Decimal
    trades_b: int
    vol_b: int
    val_b: Decimal
    pr_vwap_b: Decimal
    trades_s: int
    vol_s: int
    val_s: Decimal
    pr_vwap_s: Decimal


@dataclass
class OrderStat:
    """ Метрика "Статистика заявок"

    Attributes
    ----------
    secid: str
        Код инструмента
    ts: datetime
        Момент времени на который рассчитаны метрики
    put_orders: int
        Количество поставленных в стакан сделок
    put_orders_b: int
        Количество поставленных в стакан сделок на покупку
    put_orders_s: int
        Количество поставленных в стакан сделок на продажу
    put_vol: int
        Объем заявок в лотах, поставленных в стакан
    put_vol_b: int
        Объем заявок в лотах, поставленных в стакан сделок на покупку
    put_vol_s: int
        Объем заявок в лотах, поставленных в стакан сделок на продажу
    put_val: Decimal
        Объем в деньгах заявок поставленных в стакан
    put_val_b: Decimal
        Объем в деньгах заявок поставленных в стакан сделок на покупку
    put_val_s: Decimal
        Объем в деньгах заявок поставленных в стакан на продажу
    cancel_orders: int
        Количество снятых заявок
    cancel_orders_b: int
        Количество снятых заявок на покупку
    cancel_orders_s: int
        Количество снятых заявок на продажу
    cancel_vol: int
        Объем снятых заявок в лотах
    cancel_vol_b: int
        Объем снятых заявок в лотах на покупку
    cancel_vol_s: int
        Объем снятых заявок в лотах на продажу
    cancel_val: Decimal
        Объем в деньгах снятых заявок
    cancel_val_b: Decimal
        Объем в деньгах снятых заявок на покупку
    cancel_val_s: Decimal
        Объем в деньгах снятых заявок на продажу
    put_vwap_b: Decimal
        Средневзвешенная цена поставленных заявок на покупку
    put_vwap_s: Decimal
        Средневзвешенная цена поставленных заявок на продажу
    cancel_vwap_b: Decimal
        Средневзвешенная цена отмененных заявок на покупку
    cancel_vwap_s: Decimal
        Средневзвешенная цена отмененных заявок на продажу
    """
    secid: str
    ts: datetime
    put_orders: int
    put_orders_b: int
    put_orders_s: int
    put_vol: int
    put_vol_b: int
    put_vol_s: int
    put_val: Decimal
    put_val_b: Decimal
    put_val_s: Decimal
    cancel_orders: int
    cancel_orders_b: int
    cancel_orders_s: int
    cancel_vol: int
    cancel_vol_b: int
    cancel_vol_s: int
    cancel_val: Decimal
    cancel_val_b: Decimal
    cancel_val_s: Decimal
    put_vwap_b: Decimal
    put_vwap_s: Decimal
    cancel_vwap_b: Decimal
    cancel_vwap_s: Decimal


@dataclass
class ObStat:
    """ Метрика "Стакан стакана заявок"

    Attributes
    ----------
    secid: str
        Код инструмента
    ts: datetime
        Момент времени на который рассчитаны метрики
    spread_bbo: Decimal
        Спред между лучшей ценой покупки и продажи
    spread_lv10: Decimal
        Спред между 10ым уровнем цен
    spread_1mio: Decimal
        Спред на 1 млн руб
    levels_b: int
        Кол-во уровней цен в стакане (покупка)
    levels_s: int
        Кол-во уровней цен в стакане (продажа)
    vol_b: int
        Совокупный объем заявок в стакане на всех уровнях (покупка)
    vol_s: int
        Совокупный объем заявок в стакане на всех уровнях (продажа)
    val_b: Decimal
        Совокупный объем заявок в стакане на всех уровнях (покупка), руб
    val_s: Decimal
        Совокупный объем заявок в стакане на всех уровнях (продажа), руб
    imbalance_vol_bbo: int
        Дисбаланс объема по лучшим ценам
    imbalance_val_bbo: Decimal
        Дисбаланс объема (руб) по лучшим ценам
    imbalance_vol: int
        Дисбаланс объема на всем стакане (все уровни)
    imbalance_val: Decimal
        Дисбаланс объема (руб) на всем стакане (все уровни)
    vwap_b: Decimal
        Средневзвешенная цена покупки в стакане
    vwap_s: Decimal
        Средневзвешенная цена продажи в стакане
    vwap_b_1mio: Decimal
        Цена покупки актива на 1 млн руб
    vwap_s_1mio: Decimal
        Цена продажи актива на 1 млн руб
    """
    secid: str
    ts: datetime
    spread_bbo: Decimal
    spread_lv10: Decimal
    spread_1mio: Decimal
    levels_b: int
    levels_s: int
    vol_b: int
    vol_s: int
    val_b: Decimal
    val_s: Decimal
    imbalance_vol_bbo: int
    imbalance_val_bbo: Decimal
    imbalance_vol: int
    imbalance_val: Decimal
    vwap_b: Decimal
    vwap_s: Decimal
    vwap_b_1mio: Decimal
    vwap_s_1mio: Decimal
