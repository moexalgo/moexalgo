from __future__ import annotations

from datetime import date
from typing import Union

import pandas as pd

from moexalgo.metrics import prepare_request, dataclass_it, pandas_frame
from moexalgo.session import Session
from moexalgo.tickers import _Ticker


class Futures(_Ticker):
    """
    Класс для работы с фьючерсами.
    Больше информации о фьючерсных инструментах можно найти на странице: https://moexalgo.github.io/des/supercandles/#_2

    Attributes
    ----------
    _PATH : str
        Путь к данным.
    _TYPE : str
        Тип инструмента.
    _LIMIT : int
        Количество записей в результате, если не указано другое значение (по умолчанию 25 000).

    Methods
    ----------
    info : Callable
        Возвращает информацию об инструменте.
    tradestats : Callable
        Возвращает метрики `TradeStat`.
    obstats : Callable
        Возвращает метрики `ObStat`.
    hi2 : Callable
        Возвращает метрики `Hi2`.

    Example
    -------
    .. code-block:: python

        # Получение информации о фьючерсном инструменте
        >>> from moexalgo import futures
        >>> fut = futures.get('AFM4')
        >>> info = fut.info()
        >>> print(info)

        # Получение метрик `TradeStat` по заданным параметрам (по другим статистикам аналогично)
        >>> from moexalgo import futures
        >>> fut = futures.get('AFM4')
        >>> tradestats = fut.tradestats(start='2021-01-01', end='2021-01-10')
        >>> print(tradestats)
    """

    _PATH = 'engines/futures/markets/forts'
    _TYPE = 'fo'
    _LIMIT = 25_000

    def info(self, *fields: tuple[str], use_dataframe: bool = True) -> Union[dict, pd.DataFrame]:
        """
        Возвращает информацию об инструменте.

        Parameters
        ----------
        fields : str
            Поля для отображения.
        use_dataframe : bool
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pandas.DataFrame`, иначе `dict`.

        Returns
        -------
        return : Union[dict, pd.DataFrame]
            Информация об инструменте
        """
        return super().info(*fields, use_dataframe=use_dataframe)
    
    def _prepare_metric(self,
                        metric_type: str,
                        metric: str,
                        start: Union[str, date],
                        end: Union[str, date],
                        latest: bool = None,
                        offset: int = None,
                        cs: Session = None,
                        use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Подготовка метрик.

        Parameters
        ----------
        metric_type : str
            Тип инструмента.
        metric : str
            Название метрики.
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (start может быть равен end, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default None.
        offset : int, optional
            Начальная позиция в последовательности записей, by default None.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или `pd.DataFrame` метрик.
        """
        metrics_it = prepare_request(
            f'{metric_type}/{metric}',
            cs,
            secid=self._secid,
            from_date=start,
            till_date=end,
            latest=latest,
            offset=offset
        )
        return pandas_frame(metrics_it) if use_dataframe else dataclass_it(metrics_it)

    def tradestats(self, 
                   *, 
                   start: Union[str, date], 
                   end: Union[str, date],
                   latest: bool = None, 
                   offset: int = None,
                   cs: Session = None, 
                   use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `TradeStat` (статистику по сделкам) по заданным параметрам.
        Больше информации о метрике `TradeStat` можно найти на странице: https://moexalgo.github.io/des/supercandles/#tradestats_1

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (start может быть равен end, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default None.
        offset : int, optional
            Начальная позиция в последовательности записей, by default None.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.
        
        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или `pd.DataFrame` метрик `TradeStat`.
        """
        return self._prepare_metric(
            self._TYPE,
            'tradestats',
            start,
            end,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def obstats(self, 
                *, 
                start: Union[str, date], 
                end: Union[str, date],
                latest: bool = None, 
                offset: int = None,
                cs: Session = None, 
                use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `ObStat` (статистику по стакану) по заданным параметрам.
        Больше информации о метрике `ObStat` можно найти на странице: https://moexalgo.github.io/des/supercandles/#obstats_1

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (start может быть равен end, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default None.
        offset : int, optional
            Начальная позиция в последовательности записей, by default None.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pandas.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или `pandas.DataFrame` метрик `ObStat`.
        """
        return self._prepare_metric(
            self._TYPE,
            'obstats',
            start,
            end,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def hi2(self, 
            *, 
            start: Union[str, date], 
            end: Union[str, date],
            latest: bool = None, 
            offset: int = None,
            cs: Session = None, 
            use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `Hi2` (индекс рыночной концентрации) по заданным параметрам.
        Чтобы узнать больше о метрике `Hi2`, посетите страницу: https://moexalgo.github.io/des/hi2/

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (start может быть равен end, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default None.
        offset : int, optional
            Начальная позиция в последовательности записей, by default None.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или `pd.DataFrame` метрик `Hi2`.
        """
        return self._prepare_metric(
            self._TYPE,
            'hi2',
            start,
            end,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def alerts(self,
            *,
            start: Union[str, date],
            end: Union[str, date],
            latest: bool = None,
            offset: int = None,
            cs: Session = None,
            use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает MegaAlert (оповещение об аномальной рыночной активности) по заданным параметрам.

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default None.
        offset : int, optional
            Начальная позиция в последовательности записей, by default None.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        ----------
        return : Union[iter, pd.DataFrame]
            Итератор или `pd.DataFrame`
        """
        return self._prepare_metric(
            self._TYPE,
            'alerts',
            start,
            end,
            latest,
            offset,
            cs,
            use_dataframe
        )




def get(name: str) -> Futures:
    """
    Получение фьючерсного инструмента.

    Parameters
    ----------
    name : str
        Наименование фьючерсного инструмента.

    Returns
    -------
    return : Futures
        Фьючерсный инструмент.
    
    Example
    -------
    .. code-block:: python

        # Получение фьючерсного инструмента
        >>> from moexalgo import futures
        >>> fut = futures.get('AFM4')
        >>> info = fut.info()
        >>> print(info)
    """
    return Futures(name)
