from __future__ import annotations

from typing import Union

from .tickers import _Ticker, _resolve_ticker

try:
    from .__version__ import version as __version__
except ImportError:
    pass

from .requests import get_secid_info_and_boards

from .next import Market as NewMarket, Ticker as NewTicker, protocols
from .market import Market as OldMarket
from .tickers import _Ticker
from .stocks import Stock
from .indices import Index
from .currency import Currency
from .futures import Futures
from .utils import CandlePeriod
from .tools import resample

AnyTickers = Union["Stock", "Index", "Currency", "Futures"]


def Market(secid: str, boardid: str = None) -> OldMarket | protocols.Market:
    """
    Получение объекта определяющего раздел финансового рынка.
    """
    try:
        return OldMarket(secid, boardid)
    except NotImplementedError:
        return NewMarket(secid, boardid)


def Ticker(secid: str, boardid: str = None) -> AnyTickers | protocols.Ticker:
    """
    Получение объекта финансового инструмента по тикеру и типу рынка.

    Этот метод позволяет получить объект `Index` или `Stock`, содержащий информацию
    о финансовом инструменте, идентифицируемом по тикеру и, опционально, типу рынка.

    Parameters
    ----------
    secid : str
        Тикер финансового инструмента, например "GAZP" для акций Газпрома.
    boardid : str, optional
        Идентификатор рынка, на котором торгуется инструмент,
        например "TQBR" для основного рынка акций на Московской бирже.

    Notes
    -----
    По умолчанию значение `None` для `boardid` означает использование стандартного рынка.

    Returns
    -------
    return : Union[Index, Stock]
        Объект класса Index или Stock, содержащий информацию о запрашиваемом финансовом инструменте.

    Raises
    ------
    LookupError
        Исключение возникает, если тикер не найден на указанном рынке.

    Example
    -------
    .. code-block:: python

        # Получение информации об акции
        >>> try:
        >>>     instrument = Ticker("GAZP", "TQBR")
        >>>     print(instrument)
        >>> except LookupError:
        >>>     print("Тикер не найден.")
    """
    if info := _resolve_ticker(secid, boardid):
        secid, boardid, market, engine, *args = info
        allowed_tickers = dict((item._PATH, item) for item in [Currency, Futures, Index, Stock])
        if allowed_ticker := allowed_tickers.get(f"engines/{engine}/markets/{market}"):
            return allowed_ticker(*info)

    return NewTicker(secid, boardid)
