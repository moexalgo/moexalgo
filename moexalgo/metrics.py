from __future__ import annotations

from datetime import date, datetime
from typing import Union

import pandas as pd

from moexalgo.session import Session, data_gen
from moexalgo.utils import ISSTickerParamException, ISSDateParamException


def pandas_frame(metrics_it: iter[dict]) -> pd.DataFrame:
    """
    Трансформация данных из итератора в `pd.DataFrame`.

    Parameters
    ----------
    metrics_it : iter[dict]
        Итератор с данными.

    Returns
    -------
    return : pd.DataFrame
        Таблица с данными.
    """

    def normalize_row(row: dict) -> dict:
        """
        Нормализация строки.

        Parameters
        ----------
        row : dict
            Строка данных в формате `dict`.

        Returns
        -------
        return : dict
            Нормализованная строка.
        """
        return dict(
            ticker=row.pop('secid', row.pop('ticker', None)), 
            **{key.lower(): value for key, value in row.items()}
        )

    return pd.DataFrame([normalize_row(row) for row in metrics_it])


class DCls(dict):
    """
    Класс для работы с данными как с атрибутами.

    Parameters
    ----------
    data : dict
        Словарь с данными.
    """
    def __init__(self, **data) -> None:
        super().__init__(**data)

    def __getattr__(self, name):
        if name.startswith('_'):
            return self.__getattribute__(name)
        
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"object has no attribute '{name}'")


def dataclass_it(metrics_it: iter[dict]) -> iter[DCls]:
    """
    Трансформация данных из итератора в класс `DCls`.

    Parameters
    ----------
    metrics_it : iter[dict]
        Итератор с данными.

    Returns
    -------
    return : iter[DCls]
        Итератор с данными.
    """
    for data in metrics_it:
        data['ts'] = datetime.combine(data.pop('tradedate'), data.pop('tradetime'))
        data.pop('SYSTIME', data.pop('systime', None))
        yield DCls(**data)


def calc_offset_limit(offset: int = None,
                      limit: int = None,
                      min_limit: int = 1,
                      standart_limit: int = 10_000,
                      max_limit: int = 50_000,
                      min_offset: int = 0) -> tuple[int, int]:
    """
    Вычисление смещения и лимита.

    Parameters
    ----------
    offset : int, optional
        Смещение относительно начала, by default None.
    limit : int, optional
        Лимит данных, by default None.
    
    Returns
    -------
    return : tuple[int, int]
        Кортеж со смещением и лимитом.
    """
    offset = offset or min_offset
    if limit != -1:
        limit = limit or standart_limit

        limit = min_limit if limit < min_limit else max_limit if limit > max_limit else limit
        offset = min_offset if offset < min_offset else max_limit - 1 if offset >= max_limit else offset

    return offset, limit


def prepare_from_till_dates(from_date: Union[str, date] = None,
                            till_date: Union[str, date] = None) -> tuple[str, str]:
    """
    Подготовка дат начала и окончания.

    Parameters
    ----------
    from_date : Union[str, date], optional
        Дата начала, by default None.
    till_date : Union[str, date], optional
        Дата окончания, by default None.

    Returns
    -------
    return : tuple[str, str]
        Кортеж с датами начала и окончания.
    """
    if (from_date is None) or (till_date is None):
        raise ISSTickerParamException()

    from_date = date.fromisoformat(from_date) if isinstance(from_date, str) else (from_date or date.today())
    if not till_date:
        till_date = from_date
    elif isinstance(till_date, str):
        till_date = date.today() if till_date == 'today' else date.fromisoformat(till_date)
    
    if from_date > till_date:
        raise ISSDateParamException()
    
    return from_date.isoformat(), till_date.isoformat()


def get_metrics_path(metric: str, secid: str = None) -> str:
    """
    Получение пути к метрике.

    Parameters
    ----------
    metric : str
        Метрика.
    secid : str, optional
        Наименование инструмента, by default None.
    
    Returns
    -------
    return : str
        Путь к метрике.
    """
    path = f'datashop/algopack/{metric}'
    if secid is not None:
        path = '/'.join([path, secid.lower()])
    return path


def prepare_request(metric: str, 
                    cs: Session, 
                    *, 
                    secid: str = None, 
                    from_date: Union[str, date] = None,
                    till_date: Union[str, date] = None, 
                    latest: bool = False, 
                    offset: int = None, 
                    limit: int = None) -> iter[dict]:
    """
    Подготовка запроса к API.

    Parameters
    ----------
    metric : str
        Метрика.
    cs : Session
        Сессия.
    secid : str, optional
        Наименование инструмента, by default None.
    from_date : Union[str, date], optional
        Дата начала, by default None.
    till_date : Union[str, date], optional
        Дата окончания, by default None.
    latest : bool, optional
        Получить последние данные, by default `False`.
    offset : int, optional
        Смещение, by default None.
    limit : int, optional
        Лимит, by default None.
    
    Returns
    -------
    return : iter[dict]
        Итератор с данными.
    
    Raises
    ------
    ISSTickerParamException
        Вызывается, если secid не указан.
    ISSDateParamException
        Вызывается, если дата начала больше даты окончания.
    """
    
    from_date, till_date = prepare_from_till_dates(from_date, till_date)
    options = {'from': from_date, 'till': till_date}
    if latest:
        options['latest'] = 1

    offset, limit = calc_offset_limit(offset, limit)
    path = get_metrics_path(metric, secid)

    return data_gen(cs, path, options, offset, limit, section='data')


def prepare_market_request(metric: str,
                           cs: Session, 
                           *, 
                           secid: str = None, 
                           date_: Union[str, date] = None,
                           start: Union[str, date] = None,
                           end: Union[str, date] = None,
                           latest: bool = False, 
                           offset: int = None, 
                           limit: int = None) -> iter[dict]:
    """
    Подготовка запроса к API (для рынка).

    Parameters
    ----------
    metric : str
        Метрика.
    cs : Session
        Сессия.
    secid : str, optional
        Наименование инструмента, by default None.
    start : Union[str, date]
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
    end : Union[str, date]
        Дата конца диапазона выдачи данных.
    date_ : Union[str, date], optional
        Дата, by default None.
    latest : bool, optional
        Получить последние данные, by default `False`.
    offset : int, optional
        Смещение, by default None.
    limit : int, optional
        Лимит, by default None.

    Returns
    -------
    return : iter[dict]
        Итератор с данными.
    """

    date_ = date.today() if (date_ is None) or (date_ == 'today') else date_
    if isinstance(date_, str):
        date_ = date.fromisoformat(date_)

    if isinstance(start, str):
        start = date.fromisoformat(start)

    if isinstance(end, str):
        end = date.fromisoformat(end)

    if secid is not None:
        options = {'from': start.isoformat(), 'till': end.isoformat()}
    else:
        options = {'date': date_.isoformat()}

    if latest:
        options['latest'] = 1
    
    offset, limit = calc_offset_limit(offset, limit)
    if metric.lower().startswith('fo/futoi'):
        if len(metric.lower().split("/")) == 3:
            section = 'futoi'
            path = f'analyticalproducts/futoi/securities/{metric.lower().split("/")[-1]}'
        else:
            section = 'futoi'
            path = f'analyticalproducts/futoi/securities'
    else:
        section = 'data'
        path = get_metrics_path(metric, secid)

    return data_gen(cs, path, options, offset, limit, section=section)
