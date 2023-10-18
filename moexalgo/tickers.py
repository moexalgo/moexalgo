from __future__ import annotations

import re
import weakref
from datetime import date, timedelta

from moexalgo import session, candles
from moexalgo.market import Market
from moexalgo.models.common import Candle
from moexalgo.session import Session
from moexalgo.utils import is_interactive, pandas, result_deserializer

from moexalgo import metrics
from moexalgo import models

class _Ticker:
    """ Объект класса `Инструмент`
    """
    _PATH = 'API main path part, must be defined in superclasses'

    _secid: str
    _boardid: str

    def __new__(cls, secid: str, boardid: str = None):
        if boardid is None:
            secid, *args = re.split('\W', secid)
            if args:
                boardid = args[0]
        market = Market(cls._PATH.split('/')[-1], boardid)
        if market._ticker_info(secid):
            inst = super().__new__(cls)
            inst._secid = secid
            inst._boardid = market._boardid
            inst._r_market = weakref.ref(market)
            return inst
        raise LookupError(f"Cannot found ticker: ({secid}, {boardid or ''})")

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._secid}/{self._boardid}')"

    @property
    def _market(self):
        """ Раздел рынка в который входит инструмент """
        return self._r_market()

    def info(self, *fields, cs: Session = None):
        """ Возвращает информацию об инструменте, словарь или `pandas.DataFrame` """
        if self._market:
            if info := self._market._ticker_info(self._secid):
                if securities := info.get('securities'):
                    fields = fields or tuple(self._market._fields['securities'].keys())
                    fields = tuple(filter(lambda f : f not in ('STATUS', 'LATNAME', 'CURRENCYID', 'SECTYPE'), fields))
                    titles = self._market._fields['securities']
                    index, title, value = zip(*[(name, titles[name]['title'], value)
                                                for name, value in securities.items() if name in fields])
                    if is_interactive():
                        return pandas.DataFrame(index=index, data=dict(value=value))
                    else:
                        return dict(zip(index, value))

    def marketdata(self, *fields, cs: Session = None):
        """ Возвращает рыночную информацию и статистику об инструменте, словарь или `pandas.DataFrame` """
        if self._market:
            if info := self._market._ticker_info(self._secid):
                if securities := info.get('marketdata'):
                    fields = fields or tuple(self._market._fields['marketdata'].keys())
                    titles = self._market._fields['marketdata']
                    index, title, value = zip(*[(name, titles[name]['title'], value)
                                                for name, value in securities.items() if name in fields])
                    if is_interactive():
                        return pandas.DataFrame(index=index, data=dict(title=title, value=value))
                    else:
                        return dict(zip(index, value))

    def candles(self, *, date: str | date = None, till_date: str | date = None,
                period: str | int = None, offset: int = 0, limit: int = None, cs: Session = None):
        """ Возвращает итератор или `pandas.DataFrame` свечей инструмента по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных или дата начала диапазона выдачи данных, если указан параметр `till_date`.
            Если не указано, данные выдаются за сегодняшнее число.
        till_date:
            Дата конца диапазона выдачи данных, может быть указана как 'today' для выдачи данных "по сейчас"
        period:
            Период в минутах 1, 10, 60 или '1m', '10m', '1h', 'D', 'W', 'M', 'Q'; по умолчанию 60
        offset:
            Начальная позиция в последовательности записей
        limit:
            Максимальное количество записей в результате
        cs:
            Клиентская сессия

        Returns
        -------
            Объекты типа `Candles`
        """
        candles_it = candles.prepare_request(cs, self._PATH, self._boardid, self._secid, period=period,
                                             from_date=date, till_date=till_date, offset=offset, limit=limit)
        if is_interactive():
            return candles.pandas_frame(candles_it)
        else:
            return candles.dataclass_it(candles_it)

