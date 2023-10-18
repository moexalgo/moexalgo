from __future__ import annotations

from datetime import date

from moexalgo import metrics, models, candles
from moexalgo.session import Session
from moexalgo.tickers import _Ticker
from moexalgo.utils import is_interactive


class Share(_Ticker):
    """ Акция
    Attributes
    ----------

    """
    _PATH = 'engines/stock/markets/shares'

    def info(self, *fields: str):
        fields = fields or ['SHORTNAME', 'LOTSIZE', 'STATUS', 'DECIMALS', 'MINSTEP',
                            'ISSUESIZE', 'ISIN', 'LATNAME', 'CURRENCYID', 'SECTYPE', 'LISTLEVEL']
        return super().info(*fields)

    def tradestats(self, *, date: str | date = None, till_date: str | date = None,
                   latest: bool = None, offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `TradeStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных или дата начала диапазона выдачи данных, если указан параметр `till_date`.
            Если не указано, данные выдаются за сегодняшнее число.
        till_date:
            Дата конца диапазона выдачи данных, может быть указана как 'today' для выдачи данных "по сейчас".
        latest:
            Включает режим выдачи последних `latest` записей в наборе
        offset:
            Начальная позиция в последовательности записей
        limit:
            Максимальное количество записей в результате
        cs:
            Клиентская сессия, если используется

        Returns
        -------
            Итератор или `pandas.DataFrame` метрик `TradeStat`

        """
        metrics_it = metrics.prepare_request('tradestats', cs, secid=self._secid, from_date=date, till_date=till_date,
                                             latest=latest, offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.TradeStat, metrics_it)

    def orderstats(self, *, date: str | date = None, till_date: str | date = None,
                   latest: bool = None, offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `OrderStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных или дата начала диапазона выдачи данных, если указан параметр `till_date`.
            Если не указано, данные выдаются за сегодняшнее число.
        till_date:
            Дата конца диапазона выдачи данных, может быть указана как 'today' для выдачи данных "по сейчас".
        latest:
            Включает режим выдачи последних `latest` записей в наборе
        offset:
            Начальная позиция в последовательности записей
        limit:
            Максимальное количество записей в результате
        cs:
            Клиентская сессия, если используется

        Returns
        -------
            Итератор или `pandas.DataFrame` метрик `OrderStat`

        """
        metrics_it = metrics.prepare_request('orderstats', cs, secid=self._secid, from_date=date, till_date=till_date,
                                             latest=latest, offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.OrderStat, metrics_it)

    def obstats(self, *, date: str | date = None, till_date: str | date = None,
                latest: bool = None, offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `ObStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных или дата начала диапазона выдачи данных, если указан параметр `till_date`.
            Если не указано, данные выдаются за сегодняшнее число.
        till_date:
            Дата конца диапазона выдачи данных, может быть указана как 'today' для выдачи данных "по сейчас".
        latest:
            Включает режим выдачи последних `latest` записей в наборе
        offset:
            Начальная позиция в последовательности записей
        limit:
            Максимальное количество записей в результате
        cs:
            Клиентская сессия, если используется

        Returns
        -------
            Итератор или `pandas.DataFrame` метрик `TradeStat`

        """
        metrics_it = metrics.prepare_request('obstats', cs, secid=self._secid, from_date=date, till_date=till_date,
                                             latest=latest, offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.ObStat, metrics_it)


def get(name: str) -> Share:
    return Share(name)
