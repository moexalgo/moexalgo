from __future__ import annotations

import re
from datetime import date

from moexalgo import session, metrics, models
from moexalgo.session import Session
from moexalgo.utils import result_deserializer, is_interactive, pandas

_AVAILABLE = {'index': dict(), 'shares': dict()}
_ALIASES = {
    'index': ('index', 'SNDX'),
    'shares': ('shares', 'TQBR'),
    'stocks': ('shares', 'TQBR'),
    'EQ': ('shares', 'TQBR'),
}


def market_for(secid: str, boardid: str, cs: Session = None):
    """

    Parameters
    ----------
    secid
    boardid
    cs

    Returns
    -------

    """
    for _, boards in _AVAILABLE.items():
        if market := boards.get(boardid):
            if market.securities_for(secid, cs):
                return market


class Market:
    """ Раздел биржевого рынка
    """
    _name: str
    _boardid: str
    _fields: dict[str, dict[str, dict]] = None
    _values: dict[str, dict[str, dict]] = None

    def __new__(cls, name: str, boardid: str = None):
        if boardid is None:
            name_, boardid = _ALIASES.get(name, (None, None))
            if boardid is not None:
                name = name_
            else:
                name, *args = re.split('\W', name)
                if args:
                    boardid = args[0]
        if name not in _AVAILABLE:
            raise NotImplementedError(f"Market {name} is not supported")
        market = _AVAILABLE.setdefault(name, dict())
        if boardid not in market:
            market[boardid] = super().__new__(cls)
            market[boardid]._name = name
            market[boardid]._boardid = boardid
        return market[boardid]

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._name}/{self._boardid}')"

    def _ensure_loaded(self, cs: Session = None):
        if self._fields is None or self._values is None:
            with Session(cs or session.default) as client:
                self._fields = client.get_objects(
                    f'engines/stock/markets/{self._name}/boards/{self._boardid}/securities/columns',
                    lambda data: result_deserializer(data, key=lambda item: item['name']))
                self._values = client.get_objects(
                    f'engines/stock/markets/{self._name}/boards/{self._boardid}/securities/',
                    lambda data: result_deserializer(data, key=lambda item: item['SECID']))

    def _ticker_info(self, secid: str, cs: Session = None):
        """
        Предоставляет информацию о заданном инструменте

        Parameters
        ----------
        secid: str
        cs: Session

        Returns
        -------
        dict
        """
        self._ensure_loaded(cs)
        marketdata = self._values['marketdata'].get(secid)
        securities = self._values['securities'].get(secid)
        if securities or marketdata:
            return dict(securities=securities, marketdata=marketdata)

    def tickers(self, cs: Session = None):
        """ Справочная информация о всех инструментах рынка """

        def normalize_row(row):
            fields = ('SHORTNAME', 'LOTSIZE', 'DECIMALS',
                      'MINSTEP', 'ISSUESIZE', 'ISIN', 'REGNUMBER', 'LISTLEVEL')
            return dict(ticker=row['SECID'], **{key.lower(): value for key, value in row.items() if key in fields})

        self._ensure_loaded(cs)
        if is_interactive():
            return pandas.DataFrame([normalize_row(row) for row in self._values['securities'].values()])
        else:
            return list(self._values['securities'].values())

    def marketdata(self, cs: Session = None):
        """ Статистическая информация о всех инструментах рынка """

        def normalize_row(row):
            fields = ('BID', 'OFFER', 'BIDDEPTHT', 'OFFERDEPTHT', 'OPEN', 'HIGH', 'LOW', 'LAST',
                      'WAPRICE', 'LASTTOPREVPRICE', 'NUMTRADES', 'VOLTODAY', 'VALTODAY', 'VALTODAY_USD',
                      'OPENPERIODPRICE', 'CLOSINGAUCTIONPRICE', 'CLOSINGAUCTIONVOLUME', 'ISSUECAPITALIZATION',
                      'UPDATETIME', 'SYSTIME')
            return dict(ticker=row['SECID'], **{key.lower(): value for key, value in row.items() if key in fields})

        self._ensure_loaded(cs)
        if is_interactive():
            return pandas.DataFrame([normalize_row(row) for row in self._values['marketdata'].values()])
        else:
            return list(self._values['marketdata'].values())

    def tradestats(self, *, date: str | date = None, latest: bool = None,
                   offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `TradeStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
        metrics_it = metrics.prepare_request('tradestats', cs, from_date=date, latest=latest,
                                             offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.TradeStat, metrics_it)

    def orderstats(self, *, date: str | date = None, latest: bool = None,
                   offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `OrderStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
        metrics_it = metrics.prepare_request('orderstats', cs, from_date=date, latest=latest,
                                             offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.OrderStat, metrics_it)

    def obstats(self, *, date: str | date = None, latest: bool = None,
                offset: int = None, limit: int = None, cs: Session = None):
        """ Возвращает метрики `ObStat` по заданным параметрам.

        Parameters
        ----------
        date:
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
        metrics_it = metrics.prepare_request('obstats', cs, from_date=date, latest=latest,
                                             offset=offset, limit=(limit or 25000))
        if is_interactive():
            return metrics.pandas_frame(metrics_it)
        else:
            return metrics.dataclass_it(models.ObStat, metrics_it)
