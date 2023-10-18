from moexalgo.tickers import _Ticker


class Index(_Ticker):
    """ Индекс
    """
    _PATH = 'engines/stock/markets/index'


def get(name: str) -> Index:
    return Index(name)
