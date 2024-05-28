from __future__ import annotations

from .currency import Currency
from .futures import Futures

try:
    from .__version__ import version as __version__
except ImportError:
    pass

import re
from typing import Union

from .market import Market
from .indices import Index
from .stocks import Stock
from .utils import CandlePeriod


def Ticker(secid: str, boardid: str = None) -> Union[Index, Stock]:
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
    if boardid is None:
        secid, *args = re.split('[^a-zA-Z0-9-]', secid)
        if args:
            boardid = args[0]

    stocks = Market('stocks', boardid)
    if stocks._ticker_info(secid):
        return Stock(secid, stocks._boardid)

    currencies = Market('selt', boardid)
    if currencies._ticker_info(secid):
        return Currency(secid, currencies._boardid)

    indices = Market('index', boardid)
    if indices._ticker_info(secid):
        return Index(secid, indices._boardid)

    futures = Market('forts', boardid)
    if futures._ticker_info(secid):
        return Futures(secid, futures._boardid)

    raise LookupError(f"Cannot found ticker: `{secid}`")
