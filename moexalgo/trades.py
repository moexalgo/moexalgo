from typing import Iterator

from moexalgo.metrics import calc_offset_limit
from moexalgo.session import Session, data_gen


def dataclass_it(it: Iterator) -> Iterator[dict]:
    for items in it:
        yield dict(**items)


def prepare_request(cs: Session,
                    path: str,
                    boardid: str,
                    secid: str,
                    *,
                    tradeno: int = None,
                    offset: int = None,
                    limit: int = None,
                    ) -> Iterator[dict]:
    """
    Подготовка запроса.

    Parameters
    ----------
    cs : Session
        Сессия.
    path : str
        Путь
    boardid : str
        Идентификатор режима торгов.
    secid : str
        Идентификатор инструмента
    tradeno : int, optional
            Номер сделки с которого выдаются данные, если не задано, то с начала дня.
    offset : int
        Смещение, by default None.
    limit : int
        Лимит, by default None.

    Returns
    -------
    return : Iterator[dict]
        Итератор с данными.
    """

    options = {
        'tradeno': tradeno,
    }
    offset, limit = calc_offset_limit(offset, limit)
    path = f'{path}/boards/{boardid}/securities/{secid}/trades'
    return data_gen(cs, path, options, offset, limit, 'trades')
