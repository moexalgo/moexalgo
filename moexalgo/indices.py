from moexalgo.tickers import _Ticker


class Index(_Ticker):
    """
    Класс для работы с индексами.

    Attributes
    ----------
    _PATH : str
        Путь к данным.
    """
    _PATH = 'engines/stock/markets/index'


def get(name: str) -> Index:
    """
    Возвращает объект индекса.

    Parameters
    ----------
    name : str
        Название индекса.

    Returns
    -------
    Index
        Объект индекса.
    """
    return Index(name)
