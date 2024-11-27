from __future__ import annotations

import re
from datetime import date
from typing import Optional, Union

from moexalgo import session
from moexalgo.metrics import prepare_market_request, dataclass_it, pandas_frame
from moexalgo.session import Session, data_gen
from moexalgo.utils import result_deserializer, pd

_AVAILABLE = {
    'index': dict(),
    'shares': dict(),
    'selt': dict(),

    'forts': dict()
}
_ALIASES = {
    'index': ('engines/stock/markets/index', 'SNDX'),
    'shares': ('engines/stock/markets/shares', 'TQBR'),
    'stock': ('engines/stock/markets/shares', 'TQBR'),
    'stocks': ('engines/stock/markets/shares', 'TQBR'),
    'EQ': ('engines/stock/markets/shares', 'TQBR'),

    'selt': ('engines/currency/markets/selt', 'CETS'),
    'FX': ('engines/currency/markets/selt', 'CETS'),
    'currency': ('engines/currency/markets/selt', 'CETS'),

    'forts': ('engines/futures/markets/forts', 'RFUD'),
    'FO': ('engines/futures/markets/forts', 'RFUD'),
    'futures': ('engines/futures/markets/forts', 'RFUD'),
}


def market_for(secid: str, boardid: str, cs: Session = None) -> Optional[Market]:
    """
    Возвращает рынок, на котором торгуется заданный инструмент.

    Parameters
    ----------
    secid : str
        Уникальный идентификатор инструмента.
    boardid : str
        Идентификатор рынка, указывающий на специфическую торговую площадку или сегмент рынка.
    cs : Session, optional
        Клиентская сессия, если используется.

    Returns
    -------
    return : Optional[Market]
        Экземпляр класса Market, представляющий рынок, на котором торгуется заданный инструмент.
    """
    for _, boards in _AVAILABLE.items():
        if market := boards.get(boardid):
            if market.securities_for(secid, cs):
                return market


class Market:
    """
    Представление конкретного раздела биржевого рынка.

    Больше информации о FUTOI можно найти на странице: https://moexalgo.github.io/des/futoi/

    Этот класс предоставляет доступ к информации о биржевом рынке, а также позволяет
    оперировать данными конкретного рынка по его уникальному идентификатору.

    Parameters
    ----------
    name : str
        Название рынка или его символическое имя.
    boardid : str, optional
        Идентификатор рынка, указывающий на специфическую торговую площадку или сегмент рынка.
        Если не указан, класс попытается автоматически определить идентификатор на основе общих правил.

    Methods
    -------
    tickers : Callable[[Session, bool], Union[List[Dict[str, Any]], pandas.DataFrame]]
        Возвращает список всех инструментов рынка.
    
    marketdata : Callable[[Session, bool], Union[List[Dict[str, Any]], pandas.DataFrame]]
        Возвращает статистическую информацию о всех инструментах рынка.
    
    tradestats : Callable[[Session, bool], Union[Iterator[TradeStat], pandas.DataFrame]]
        Возвращает метрики `TradeStat` по заданным параметрам.
    
    orderstats : Callable[[Session, bool], Union[Iterator[OrderStat], pandas.DataFrame]]
        Возвращает метрики `OrderStat` по заданным параметрам.
    
    obstats : Callable[[Session, bool], Union[Iterator[ObStat], pandas.DataFrame]]
        Возвращает метрики `ObStat` по заданным параметрам.
    
    futoi : Callable[[Session, bool], Union[Iterator[FUTOI], pandas.DataFrame]]
        Возвращает метрики `FUTOI` по заданным параметрам.
    
    Returns
    -------
    return : Market
        Экземпляр класса Market, представляющий указанный рынок.

    Raises
    ------
    NotImplementedError
        Вызывается, если рынок с указанным названием не поддерживается.

    Example
    -------
    .. code-block:: python

        # Получение информации об акции
        >>> try:
        >>>     market_instance = Market("index", "MOEX")
        >>>     print(market_instance)
        >>>     market_instance._ensure_loaded()
        >>> except NotImplementedError:
        >>>     print("Рынок не поддерживается.")
    """
    _name: str
    _path: str
    _pref: str
    _boardid: str
    _fields: dict[str, dict[str, dict]] = None
    _values: dict[str, dict[str, dict]] = None
    _delisted: list[str] = None
    _LIMIT = 25_000

    def __new__(cls, name: str, boardid: str = None) -> Market:
        """
        Создает новый экземпляр класса Market.

        Parameters
        ----------
        name : str
            Название рынка или его символическое имя.
        boardid : str, optional
            Идентификатор рынка, указывающий на специфическую торговую площадку или сегмент рынка.
            Если не указан, класс попытается автоматически определить идентификатор на основе общих правил.
        
        Returns
        -------
        return : Market
            Экземпляр класса Market, представляющий указанный рынок.
        
        Raises
        ------
        NotImplementedError
            Вызывается, если рынок с указанным названием не поддерживается.

        Example
        -------
        .. code-block:: python
        
            # Получение информации об акции
            >>> market_instance = Market("index", "MOEX")
            >>> print(market_instance)
        """
        if '/' not in name:
            path, default_boardid = _ALIASES.get(name, (None, None))
            boardid = boardid or default_boardid
            name = path.split('/')[-1]
        else:
            path = name
            name = name.split('/')[-1]

        if name not in _AVAILABLE:
            raise NotImplementedError(f"Market {name} is not supported")

        market = _AVAILABLE.setdefault(name, dict())
        prefs = [k for k, v in _ALIASES.items() if v[0].startswith(path) and len(k) == 2]
        pref = prefs[0].lower() if prefs else None
        if boardid not in market:
            market[boardid] = super().__new__(cls)
            market[boardid]._name = name
            market[boardid]._path = path
            market[boardid]._pref = pref
            market[boardid]._boardid = boardid

        return market[boardid]

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._name}/{self._boardid}')"

    def _ensure_loaded(self, cs: Session = None) -> None:
        """
        Проверяет, загружены ли данные о рынке и его инструментах.
        Если данные не загружены, загружает их.

        Parameters
        ----------
        cs : Session, optional
            Клиентская сессия, если используется.

        Returns
        -------
        return : None
        """
        if self._fields is None or self._values is None:
            with Session(cs or session.default) as client:
                self._fields = client.get_objects(
                    f'{self._path}/boards/{self._boardid}/securities/columns',
                    lambda data: result_deserializer(data, key=lambda item: item['name']))

                self._values = client.get_objects(
                    f'{self._path}/boards/{self._boardid}/securities/',
                    lambda data: result_deserializer(data, key=lambda item: item['SECID']))

    def _is_delisted(self, secid: str, cs: Session = None):
        raise NotImplementedError("Deprecated")
        # self._ensure_loaded(cs)
        # if self._delisted is None:
        #     market = self._name
        #     engine = self._path.split('/')[1]
        #     "&group_by=type&group_by_filter=preferred_share&iss.only=securities&securities.columns=secid"
        #     with Session(cs or session.default) as client:
        #         data = data_gen(cs, f'securities/',
        #                         {'engine': engine, 'market': market, 'is_trading': 0,
        #                          'iss.only': 'securities', 'securities.columns': 'secid'},
        #                         0, 10000, 'securities')
        #         self._delisted = [row['secid'] for row in data]
        # return secid in self._delisted

    def _ticker_info(self, secid: str, cs: Session = None) -> dict[str, dict[str, dict]]:
        """
        Возвращает информацию о заданном инструменте.

        Parameters
        ----------
        secid : str
            Уникальный идентификатор инструмента.
        cs : Session, optional
            Клиентская сессия, если используется.

        Returns
        -------
        return : Dict[str, Any]
            Информация о заданном инструменте.
        """
        raise NotImplementedError("Deprecated")
        # self._ensure_loaded(cs)
        # marketdata = self._values['marketdata'].get(secid)
        # securities = self._values['securities'].get(secid)
        # if securities or marketdata:
        #     return dict(securities=securities, marketdata=marketdata)
        # if self._is_delisted(secid):
        #     return dict(securities=None, marketdata=None)

    def _normalize_row(self, row: dict[str, dict], fields: tuple[str]) -> dict[str, dict]:
        """
        Нормализует строку данных о статистике инструмента.

        Parameters
        ----------
        row : Dict[str, Any]
            Строка данных о статистике инструмента.
        fields : Tuple[str]
            Поля, которые необходимо оставить в строке данных.

        Returns
        -------
        return : Dict[str, Any]
            Нормализованная строка данных о статистике инструмента.
        """
        return dict(
            ticker=row['SECID'],
            **{key.lower(): value for key, value in row.items() if key in fields}
        )

    def _get_data(self,
                  option: str,
                  cs: Session = None,
                  use_dataframe: bool = True,
                  fields: tuple[str] = None) -> Union[list[dict], pd.DataFrame]:
        """
        Возвращает данные о рынке по заданному параметру.

        Parameters
        ----------
        option : str
            Параметр, по которому необходимо получить данные.
        cs : Session, optional
            Клиентская сессия, если используется.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе список.
        fields : Tuple[str], optional
            Поля, которые необходимо оставить в строке данных.
        
        Returns
        -------
        return : Union[list[dict], pd.DataFrame]
            Объекты типа List или `pd.DataFrame`.
        """
        self._ensure_loaded(cs)
        if use_dataframe:
            return pd.DataFrame(
                [self._normalize_row(row, fields) for row in self._values[option].values()]
            )
        else:
            return list(self._values[option].values())

    def tickers(self, cs: Session = None, use_dataframe: bool = True) -> Union[list[dict], pd.DataFrame]:
        """
        Возвращает список всех инструментов рынка.

        Parameters
        ----------
        cs : Session, optional
            Клиентская сессия, если используется.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе список.
        
        Returns
        -------
        return : Union[list[dict], pd.DataFrame]
            Объекты типа List или `pd.DataFrame`.
        """
        fields = (
            'SHORTNAME',  # Краткое наименование
            'LOTSIZE',  # Размер лота
            'DECIMALS',  # Количество знаков после запятой
            'MINSTEP',  # Минимальный шаг цены
            'ISSUESIZE',  # Объем выпуска
            'ISIN',  # Стандартное наименование
            'REGNUMBER',  # Регистрационный номер
            'LISTLEVEL'  # Уровень листинга
        )

        return self._get_data('securities', cs, use_dataframe, fields)

    def marketdata(self, cs: Session = None, use_dataframe: bool = True) -> Union[list[dict], pd.DataFrame]:
        """ 
        Возвращает статистическую информацию о всех инструментах рынка.

        Parameters
        ----------
        cs : Session, optional
            Клиентская сессия, если используется.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если `True`, то возвращает `pd.DataFrame`, иначе список.

        Returns
        -------
        return : Union[list[dict], pd.DataFrame]
            Объекты типа List или `pd.DataFrame`.
        """
        fields = (
            'BID',  # Лучшая цена покупки
            'OFFER',  # Лучшая цена продажи
            'BIDDEPTHT',  # Глубина стакана покупки
            'OFFERDEPTHT',  # Глубина стакана продажи
            'OPEN',  # Цена открытия
            'HIGH',  # Максимальная цена
            'LOW',  # Минимальная цена
            'LAST',  # Цена последней сделки
            'WAPRICE',  # Средневзвешенная цена
            'LASTTOPREVPRICE',  # Изменение цены последней сделки к предыдущей
            'NUMTRADES',  # Количество сделок
            'VOLTODAY',  # Объем сделок за день
            'VALTODAY',  # Объем сделок за день в валюте
            'VALTODAY_USD',  # Объем сделок за день в долларах
            'OPENPERIODPRICE',  # Цена открытия периода
            'CLOSINGAUCTIONPRICE',  # Цена закрытия аукциона
            'CLOSINGAUCTIONVOLUME',  # Объем закрытия аукциона
            'ISSUECAPITALIZATION',  # Капитализация
            'UPDATETIME',  # Время обновления
            'SYSTIME'  # Время системы
        )

        return self._get_data('marketdata', cs, use_dataframe, fields)

    def _prepare_metric(self,
                        metric: str,
                        metric_type: str = None,
                        date: Union[str, date] = None,
                        latest: bool = None,
                        offset: int = None,
                        cs: Session = None,
                        use_dataframe: bool = True,
                        limit: int = None) -> Union[iter, pd.DataFrame]:
        """
        Подготавливает запрос к рынку по заданным параметрам.

        Parameters
        ----------
        metric : str
            Метрика, по которой необходимо получить данные.
        metric_type : str, optional
            Тип метрики, by default None
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
        return : Iterator[TradeStat] | pd.DataFrame
            Итератор или `pd.DataFrame` метрик.
        """
        metrics_it = prepare_market_request(
            f'{metric_type}/{metric}',
            cs,
            date_=date,
            latest=latest,
            offset=offset,
            limit=limit or 50_000
        )
        return pandas_frame(metrics_it) if use_dataframe else dataclass_it(metrics_it)

    def tradestats(self,
                   *,
                   date: Union[str, date] = None,
                   latest: bool = None,
                   offset: int = None,
                   cs: Session = None,
                   use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """ 
        Возвращает метрики `TradeStat` по заданным параметрам.

        Parameters
        ----------
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest : bool, optional
            Включает режим выдачи последних записей в наборе.
        offset : int, optional
            Начальная позиция в последовательности записей.
        cs : Session, optional
            Клиентская сессия, если используется.
        use_dataframe : bool, optional
            Изменяет тип возвращаемого объекта, by default `True`.
            Если True, то возвращает pd.DataFrame, иначе итератор.

        Returns
        -------
        return : Union[iter, pd.DataFrame]
            Итератор или pd.DataFrame метрик `TradeStat`.
        """

        return self._prepare_metric(
            'tradestats',
            self._pref,
            date,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def orderstats(self,
                   *,
                   date: Union[str, date] = None,
                   latest: bool = None,
                   offset: int = None,
                   cs: Session = None,
                   use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `OrderStat` по заданным параметрам.

        Parameters
        ----------
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
            Итератор или pd.DataFrame метрик `OrderStat`.
        """

        return self._prepare_metric(
            'orderstats',
            self._pref,
            date,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def obstats(self,
                *,
                date: Union[str, date] = None,
                latest: bool = None,
                offset: int = None,
                cs: Session = None,
                use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `ObStat` по заданным параметрам.

        Parameters
        ----------
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
            Итератор или `pd.DataFrame` метрик `ObStat`.
        """
        return self._prepare_metric(
            'obstats',
            self._pref,
            date,
            latest,
            offset,
            cs,
            use_dataframe
        )

    def futoi(self,
              *,
              date: Union[str, date] = None,
              # latest: bool = None,
              # offset: int = None,
              cs: Session = None,
              use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает метрики `FUTOI` по заданным параметрам.

        Parameters
        ----------
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
        if not self._path.startswith('engines/futures/markets'):
            raise NotImplementedError("FUTOI is not implemented for this market")

        return self._prepare_metric(
            'FUTOI',
            self._pref,
            date,
            latest=None,
            offset=None,
            cs=cs,
            use_dataframe=use_dataframe,
            limit=-1
        )

    def alerts(self,
                *,
                date: Union[str, date] = None,
                latest: bool = None,
                offset: int = None,
                cs: Session = None,
                use_dataframe: bool = True) -> Union[iter, pd.DataFrame]:
        """
        Возвращает MegaAlert (оповещение об аномальной рыночной активности) по заданным параметрам.

        Parameters
        ----------
        date : Union[str, date], optional
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
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
            Итератор или `pd.DataFrame`.
        """
        if not self._path.startswith('engines/stock/markets'):
            raise NotImplementedError
        return self._prepare_metric(
            'alerts',
            self._pref,
            date,
            latest,
            offset,
            cs,
            use_dataframe
        )