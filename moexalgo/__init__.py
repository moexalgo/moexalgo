from __future__ import annotations

try:
    from .__version__ import version as __version__
except ImportError:
    pass

import re

from .market import Market
from .indices import Index
from .shares import Share


def Ticker(secid: str, boardid: str = None) -> Index | Share:
    """ Резолвер тикера

    Parameters
    ----------
    secid: str
        Тикер инструмента
    boardid: str
        Тип рынка

    Returns
    -------
     Обект класса Index или Share

    Raises
    ------
    LookupError
        Если тикер не найден.
    """
    if boardid is None:
        secid, *args = re.split('\W', secid)
        if args:
            boardid = args[0]
    shares = Market('shares', boardid)
    if shares._ticker_info(secid):
        return Share(secid, shares._boardid)
    indices = Market('index', boardid)
    if indices._ticker_info(secid):
        return Index(secid, indices._boardid)
    raise LookupError(f"Cannot found ticker: `{secid}`")
