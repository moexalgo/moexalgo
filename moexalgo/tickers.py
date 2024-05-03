from __future__ import annotations

from datetime import date
import re
from typing import Union
import weakref

from moexalgo.candles import Candle, dataclass_it, prepare_request, pandas_frame
from moexalgo.market import Market
from moexalgo.session import Session, data_gen
from moexalgo.utils import pd, CandlePeriod


class _Ticker:
    """
    Базовый класс для работы с инструментами.

    Attributes
    ----------
    _PATH : str
        Путь к данным.
    _secid : str
        Идентификатор инструмента.
    _boardid : str
        Идентификатор рынка.
    _r_market : weakref.ref
        Ссылка на объект рынка.

    Methods
    -------
    info : Callable
        Возвращает информацию об инструменте.
    marketdata : Callable
        Возвращает рыночную информацию и статистику об инструменте.
    candles : Callable
        Возвращает итератор свечей инструмента по заданным параметрам.
    orderbook : Callable
        Возвращает текущий стакан лучших цен.

    Example
    -------
    .. code-block:: python
    
        # Получение информации об акции
        >>> from moexalgo import tickers
        >>> ticker = tickers.get('SBER')

        >>> print(ticker)

        # Получение информации об инструменте
        >>> info = ticker.info()
        >>> print(info)

            # Получение рыночной информации и статистики об инструменте
        >>> marketdata = ticker.marketdata()
        >>> print(marketdata)

            # Получение свечей инструмента по заданным параметрам
        >>> candles = ticker.candles(start='2021-01-01', end='2021-01-10')
        >>> for candle in candles:
        ...     print(candle)

            # Получение текущего стакана лучших цен
        >>> orderbook = ticker.orderbook()
        >>> print(orderbook)
    """

    _PATH = 'Основная часть пути к API, должна быть определена в суперклассах'

    _secid: str
    _boardid: str

    def __new__(cls, secid: str, boardid: str = None) -> _Ticker:
        """
        Создает новый объект инструмента.

        Parameters
        ----------
        secid : str
            Идентификатор инструмента.
        boardid : str
            Идентификатор рынка.

        Returns
        -------
        _Ticker
            Объект инструмента.
        """
        if boardid is None:
            secid, *args = re.split('\W', secid)
            if args:
                boardid = args[0]
        
        market = Market(cls._PATH, boardid)
        if market._ticker_info(secid):
            instance = super().__new__(cls)
            instance._secid = secid
            instance._boardid = market._boardid
            instance._r_market = weakref.ref(market)
            return instance
        raise LookupError(f"Cannot found ticker: ({secid}, {boardid or ''})")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._secid}/{self._boardid}')"

    @property
    def _market(self) -> Market:
        """
        Раздел рынка в который входит инструмент.

        Returns
        -------
        Market
            Раздел рынка.
        """
        return self._r_market()

    def info(self, *fields: tuple[str], use_dataframe: bool = True) -> Union[dict, pd.DataFrame]:
        """
        Возвращает информацию об инструменте, словарь или `pd.DataFrame`

        Parameters
        ----------
        fields : tuple[str]
            Поля для отображения
        use_dataframe : bool
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе словарь.

        Returns
        -------
        return : Union[dict, pd.DataFrame]
            Информация об инструменте
        """

        if self._market:

            if info := self._market._ticker_info(self._secid):

                if securities := info.get('securities'):

                    if not fields:
                        fields = tuple(self._market._fields['securities'].keys())
                    
                    exclude_fields = ('STATUS', 'LATNAME', 'CURRENCYID', 'SECTYPE')
                    fields = tuple(filter(lambda f: f not in exclude_fields, fields))
                    securities = list(filter(lambda x: x[0] in fields, securities.items()))

                    if use_dataframe:
                        index, value = zip(*securities)
                        return pd.DataFrame(dict(value=value), index=index)
                    
                    else:
                        return dict(securities)

    def marketdata(self, *fields, use_dataframe: bool = True) -> Union[dict, pd.DataFrame]:
        """
        Возвращает рыночную информацию и статистику об инструменте.

        Parameters
        ----------
        fields : tuple[str]
            Поля для отображения
        use_dataframe : bool
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе словарь.

        Returns
        -------
        return : Union[dict, pd.DataFrame]
            Рыночная информация и статистика об инструменте.
        """

        if self._market:

            if info := self._market._ticker_info(self._secid):

                if securities := info.get('marketdata'):

                    if not fields:
                        fields = tuple(self._market._fields['marketdata'].keys())
                    
                    titles = self._market._fields['marketdata']
                    securities = [(name, titles[name]['title'], value) for (name, value) in securities.items()]
                    securities = list(filter(lambda x: x[0] in fields, securities))

                    index, title, value = zip(*securities)
                    if use_dataframe:
                        return pd.DataFrame(dict(title=title, value=value), index=index)
                    else:
                        return dict(zip(index, value))

    def candles(self, 
                *, 
                start: Union[str, date], 
                end: Union[str, date],
                period: Union[str, int, CandlePeriod] = None, 
                offset: int = 0,
                cs: Session = None, 
                latest: bool = False, 
                use_dataframe: bool = True) -> Union[iter[Candle], pd.DataFrame]:
        """
        Возвращает итератор свечей инструмента по заданным параметрам.

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        period : Union[str, int, CandlePeriod], optional
            Период свечи, by default None.

            Если `int`, то интерпретируется в следующем формате:
            - 1 - 1 минута
            - 10 - 10 минут
            - 60 - 1 час
            - 24 - 1 день
            - 7 - 1 неделя
            - 31 - 1 месяц

            Если `str`, то интерпретируется в следующем формате:
            - '1min' - 1 минута
            - '10min' - 10 минут
            - '1h' - 1 час
            - '1d' - 1 день
            - '1w' - 1 неделя
            - '1m' - 1 месяц
        
        offset : int, optional
            Начальная позиция в последовательности записей, by default 0.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default False.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter[Candle], pd.DataFrame]
            Итератор свечей.
        """

        candles_it = prepare_request(
            cs, 
            self._PATH, 
            self._boardid, 
            self._secid, 
            period=period,
            from_date=start, 
            till_date=end, 
            offset=offset,
            latest=latest
        )
        return pandas_frame(candles_it) if use_dataframe else dataclass_it(candles_it)

    def orderbook(self, cs: Session = None, use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает текущий стакан лучших цен.

        Parameters
        ----------
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Стакан лучших цен.
        """
        if self._PATH.startswith('engines/currency/markets'):
            raise NotImplementedError("OrderBook is not implemented for currencies")
        path = f'{self._PATH}/boards/{self._boardid}/securities/{self._secid}/orderbook'
        orderbook_it = data_gen(
            cs=cs, 
            path=path, 
            options={}, 
            offset=0, 
            limit=-1,
            section='orderbook'
        )
        return pandas_frame(orderbook_it) if use_dataframe else dataclass_it(orderbook_it)
