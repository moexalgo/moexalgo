from __future__ import annotations

from datetime import date
from typing import Union, Iterator

import pandas as pd

from moexalgo.metrics import calc_offset_limit, prepare_from_till_dates
from moexalgo.models import Candle
from moexalgo.session import Session, data_gen
from moexalgo.utils import CandlePeriod


def pandas_frame(candles_it: iter) -> pd.DataFrame:
    """
    Преобразование итератора свечей в `pd.DataFrame`.

    Parameters
    ----------
    candles_it : iter
        Итератор свечей.
    
    Returns
    -------
    return : pd.DataFrame
        Данные в формате `pd.DataFrame`.
    """

    def _make_lower_keys(dct_: dict) -> dict:
        """
        Преобразование ключей словаря в нижний регистр.

        Parameters
        ----------
        dct_ : dict
            Словарь с данными.
        
        Returns
        -------
        return : dict
            Словарь с ключами в нижнем регистре.
        """
        return {key.lower(): value for (key, value) in dct_.items()}

    return pd.DataFrame([_make_lower_keys(dct) for dct in candles_it])


def dataclass_it(candles_it: iter) -> iter[Candle]:
    """
    Преобразование итератора свечей в класс `Candle`.

    Parameters
    ----------
    candles_it : iter
        Итератор свечей.
    
    Returns
    -------
    return : iter[Candle]
        Итератор свечей в формате `Candle`.
    """
    for candle in candles_it:
        yield Candle(**candle)


def normalize_period(period: CandlePeriod | int | str) -> int:
    def _raise_error() -> None:
        """
        Вызов ошибки.

        Raises
        ------
        ValueError
            Ошибка о неправильном параметре `period`.
        """
        raise ValueError("Неправильный параметр `period`")

    if isinstance(period, CandlePeriod):
        interval_seconds = period.value

    elif isinstance(period, int):
        if period == 1:
            interval_seconds = CandlePeriod.ONE_MINUTE.value
        elif period == 10:
            interval_seconds = CandlePeriod.TEN_MINUTES.value
        elif period == 60:
            interval_seconds = CandlePeriod.ONE_HOUR.value
        elif period == 24:
            interval_seconds = CandlePeriod.ONE_DAY.value
        elif period == 7:
            interval_seconds = CandlePeriod.ONE_WEEK.value
        elif period == 31:
            interval_seconds = CandlePeriod.ONE_MONTH.value
        else:
            _raise_error()

    elif isinstance(period, str):
        if period == '1min':
            interval_seconds = CandlePeriod.ONE_MINUTE.value
        elif period == '10min':
            interval_seconds = CandlePeriod.TEN_MINUTES.value
        elif period == '1h':
            interval_seconds = CandlePeriod.ONE_HOUR.value
        elif period == '1d':
            interval_seconds = CandlePeriod.ONE_DAY.value
        elif period == '1w':
            interval_seconds = CandlePeriod.ONE_WEEK.value
        elif period == '1m':
            interval_seconds = CandlePeriod.ONE_MONTH.value
        else:
            _raise_error()

    elif period is None:
        interval_seconds = CandlePeriod.TEN_MINUTES.value
    else:
        raise TypeError("Неверный тип для `period`")
    return interval_seconds


def prepare_request(cs: Session,
                    path: str, 
                    boardid: str, 
                    secid: str, 
                    *,
                    from_date: Union[str, date] = None, 
                    till_date: Union[str, date] = None,
                    period: Union[CandlePeriod, int, str] = None, 
                    offset: int = None, 
                    limit: int = None, 
                    latest: bool = False) -> Iterator[dict] | None:
    
    """
    Подготовка запроса.

    Parameters
    ----------
    cs : Session
        Сессия.
    path : str
        Путь
    boardid : str
        Идентификатор режима торгов.
    secid : str
        Идентификатор инструмента
    from_date : Union[str, date]
        Дата начала, by default None.
    till_date : Union[str, date]
        Дата окончания, by default None.
    period : Union[CandlePeriod, int, str]
        Период, by default None.
    offset : int
        Смещение, by default None.
    limit : int
        Лимит, by default None.
    latest : bool
        Последние данные, by default None.

    Returns
    -------
    return : Iterator[dict] | None
        Итератор с данными или None.

    Raises
    ------
    ValueError
        Ошибка о неправильном параметре `period`.
    TypeError
        Неверный тип для `period`.
    """

    interval_seconds = normalize_period(period)
    from_date, till_date = prepare_from_till_dates(from_date, till_date)
    
    options = {
            'from': from_date, 
            'till': till_date,
            'interval': interval_seconds
        }

    offset, limit = calc_offset_limit(offset, limit)

    if latest:
        options['iss.reverse'] = True
        limit = 1

    path = f'{path}/boards/{boardid}/securities/{secid}/candles'
    return data_gen(cs, path, options, offset, limit, 'candles')
