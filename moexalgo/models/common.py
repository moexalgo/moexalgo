from dataclasses import dataclass
from datetime import time, datetime


@dataclass
class Candle:
    """Модель объекта `Свеча`

    Attributes
    ----------
    open : float
        Цена открытия свечи
    close - Цена закрытия свечи : float
    high : float
        Максимальная цена
    low : float
        Минимальная цена
    value : float
        Денежный оборот
    volume : int
        Количество
    begin : datetime
        Дата и время открытия свечи
    end : datetime
        Дата и время закрытия свечи
    """
    open: float
    close: float
    high: float
    low: float
    value: float
    volume: int
    begin: datetime
    end: datetime
