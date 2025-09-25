from __future__ import annotations

import re
import typing as t
import weakref
from datetime import date, datetime
from typing import Union

from moexalgo import trades
from moexalgo.candles import Candle, prepare_request, pandas_frame, dataclass_it
from moexalgo.market import Market
from moexalgo.metrics import prepare_market_request, dataclass_it as dict_it
from moexalgo.requests import get_secid_info_and_boards
from moexalgo.session import Session, data_gen
from moexalgo.utils import pd, CandlePeriod

PERPETUAL = ("USDRUBF", "EURRUBF", "CNYRUBF", "IMOEXF", "GLDRUBF", "SBERF", "GAZPF")


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
        >>> marketdata = ticker._marketdata()
        >>> print(marketdata)

            # Получение свечей инструмента по заданным параметрам
        >>> candles = ticker._candles(start='2021-01-01', end='2021-01-10')
        >>> for candle in candles:
        ...     print(candle)

            # Получение текущего стакана лучших цен
        >>> orderbook = ticker.orderbook()
        >>> print(orderbook)
    """

    _PATH = "Основная часть пути к API, должна быть определена в суперклассах"

    _secid: str
    _boardid: str
    _delisted: bool
    _sec_info: dict[str, t.Any] = dict()
    _board_info: dict[str, t.Any] = dict()

    def __new__(
        cls,
        secid: str,
        boardid: str = None,
        market: str = None,
        engine: str = None,
        description: dict = None,
        board_info: dict = None,
    ) -> _Ticker:
        """
        Создает новый объект инструмента.

        Parameters
        ----------
        secid : str
            Идентификатор инструмента.
        boardid : str
            Идентификатор рынка.
        market : str
            Рынок

        Returns
        -------
        _Ticker
            Объект инструмента.
        """
        if boardid is None or market is None:
            if info := _resolve_ticker(secid, boardid):
                secid, boardid, market, engine, description, board_info = info
            else:
                raise LookupError(f"Cannot found ticker: `{secid}`")

        market = Market(market, boardid)
        instance = super().__new__(cls)
        instance._secid = secid
        instance._boardid = market._boardid
        instance._r_market = weakref.ref(market)
        instance._sec_info = description
        instance._board_info = board_info
        return instance

    @property
    def delisted(self) -> bool:
        return not self._board_info["listed_from"] <= datetime.now().date() <= self._board_info["listed_till"]

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

                if securities := info.get("securities"):

                    if not fields:
                        fields = tuple(self._market._fields["securities"].keys())

                    exclude_fields = ("STATUS", "LATNAME", "CURRENCYID", "SECTYPE")
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

                if securities := info.get("marketdata"):

                    if not fields:
                        fields = tuple(self._market._fields["marketdata"].keys())

                    titles = self._market._fields["marketdata"]
                    securities = [(name, titles[name]["title"], value) for (name, value) in securities.items()]
                    securities = list(filter(lambda x: x[0] in fields, securities))

                    index, title, value = zip(*securities)
                    if use_dataframe:
                        return pd.DataFrame(dict(title=title, value=value), index=index)
                    else:
                        return dict(zip(index, value))

    def candles(
        self,
        *,
        start: Union[str, date],
        end: Union[str, date],
        period: Union[str, int, CandlePeriod] = None,
        offset: int = 0,
        cs: Session = None,
        latest: bool = False,
        use_dataframe: bool = True,
    ) -> Union[iter[Candle], pd.DataFrame]:
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
            latest=latest,
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
        if self._PATH.startswith("engines/currency/markets"):
            raise NotImplementedError("OrderBook is not implemented for currencies")
        path = f"{self._PATH}/boards/{self._boardid}/securities/{self._secid}/orderbook"
        orderbook_it = data_gen(cs=cs, path=path, options={}, offset=0, limit=-1, section="orderbook")
        return pandas_frame(orderbook_it) if use_dataframe else dataclass_it(orderbook_it)

    def futoi(
        self,
        *,
        start: Union[str, date],
        end: Union[str, date],
        # latest: bool = None,
        # offset: int = None,
        cs: Session = None,
        use_dataframe: bool = True,
    ) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `FUTOI` по заданным параметрам.

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        latest : bool, optional
            Включает режим выдачи последних записей в наборе.
        offset : int, optional
            Начальная позиция в последовательности записей.
        cs : Session, optional
            Клиентская сессия, если используется.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или `pd.DataFrame` метрик `FUTOI`.

        Raises
        ------
        NotImplementedError
            Вызывается, если `FUTOI` не поддерживается для данного рынка.
        """
        sectype = self._secid
        if self._secid not in PERPETUAL:
            sectype = self._secid[:2]
        metrics_it = prepare_market_request(
            f"fo/futoi/{sectype}",
            cs,
            secid=self._secid,
            start=start,
            end=end,
            # latest=latest,
            # offset=offset,
            limit=-1,
        )
        return pandas_frame(metrics_it) if use_dataframe else dict_it(metrics_it)

    @classmethod
    def _get_sec_info(cls, secid: str):
        if secid not in cls._sec_info:
            rv = data_gen(None, f"securities/{secid}", {}, 0, 100, section="boards")
            if found := [info for info in rv if info["is_primary"] == 1]:
                cls._sec_info[secid] = found[0]
        try:
            return cls._sec_info[secid]
        except KeyError:
            raise LookupError(f"Cannot found ticker: `{secid}`")

    def trades(
        self, *, tradeno: int = None, cs: Session = None, use_dataframe: bool = True
    ) -> Union[iter[dict], pd.DataFrame]:
        """
        Возвращает итератор сделок за последний день или начиная с заданного `tradeno`.

        Parameters
        ----------
        tradeno : int, optional
            Номер сделки с которого выдаются данные, если не задано, то с начала дня.
        cs : Session, optional
            Клиентская сессия, если используется, by default None.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе итератор.

        Returns
        -------
        return : Union[iter[dict], pd.DataFrame]
            Итератор сделок.
        """

        trades_it = trades.prepare_request(cs, self._PATH, self._boardid, self._secid, tradeno=tradeno)
        return pandas_frame(trades_it) if use_dataframe else trades.dataclass_it(trades_it)


def _resolve_ticker(secid: str, boardid: str = None) -> tuple[str, str, str, str, dict, dict] | None:
    if boardid is None:
        secid, *args = re.split("[^a-zA-Z0-9-]", secid)
        if args:
            boardid = args[0]
    try:
        description, boards = get_secid_info_and_boards(secid)
    except KeyError:
        return None
    if found := [board for name, board in boards.items() if board["is_primary"]]:
        board_info = found[0]
        if boardid:
            if boardid != board_info["boardid"]:
                raise ValueError("Wrong `boardid`")
        boardid = board_info["boardid"]
        market = board_info["market"]
        engine = board_info["engine"]
        return secid, boardid, market, engine, description, board_info
