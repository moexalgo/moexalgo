import sys
from datetime import date
from enum import Enum
from typing import Any, Iterable
from typing import Union, NamedTuple

import orjson as json  # noqa

pd = None
if "ipykernel" in sys.modules:
    try:
        import pandas as pd
        from pandas import DataFrame  # noqa
    except ImportError:
        pass
else:
    type DataFrame = Any


class CandlePeriod(Enum):
    """
    Возможные временные интервалы для свечей.
    """

    ONE_MINUTE = 1
    TEN_MINUTES = 10
    ONE_HOUR = 60
    ONE_DAY = 24
    ONE_WEEK = 7
    ONE_MONTH = 31


class Desc(NamedTuple):
    aliases: list[str]
    features: dict[str, str] | None = None


def normalize_period(period: CandlePeriod | int | str) -> int:
    """
    Нормализует значение периода во внутреннее представление ISS.
    """
    interval = CandlePeriod.TEN_MINUTES.value

    if isinstance(period, CandlePeriod):
        interval = period.value

    elif isinstance(period, int):
        if period == 1:
            interval = CandlePeriod.ONE_MINUTE.value
        elif period == 10:
            interval = CandlePeriod.TEN_MINUTES.value
        elif period == 60:
            interval = CandlePeriod.ONE_HOUR.value
        elif period == 24:
            interval = CandlePeriod.ONE_DAY.value
        elif period == 7:
            interval = CandlePeriod.ONE_WEEK.value
        elif period == 31:
            interval = CandlePeriod.ONE_MONTH.value
        else:
            raise ValueError("Некорректное значение параметра `period`")

    elif isinstance(period, str):
        if period == "1min":
            interval = CandlePeriod.ONE_MINUTE.value
        elif period == "10min":
            interval = CandlePeriod.TEN_MINUTES.value
        elif period in ("1h", "1H"):
            interval = CandlePeriod.ONE_HOUR.value
        elif period in ("1d", "1D"):
            interval = CandlePeriod.ONE_DAY.value
        elif period in ("1w", "1W"):
            interval = CandlePeriod.ONE_WEEK.value
        elif period in ("1m", "1M"):
            interval = CandlePeriod.ONE_MONTH.value
        else:
            raise ValueError("Некорректное значение параметра `period`")

    elif period is None:
        pass
    else:
        raise TypeError("Неверный тип для `period`")

    return interval


def prepare_from_till_dates(from_date: Union[str, date] = None, till_date: Union[str, date] = None) -> tuple[str, str]:
    """
    Подготовка дат начала и окончания.

    Parameters
    ----------
    from_date :
        Дата начала, by default None.
    till_date :
        Дата окончания, by default None.

    Returns
    -------
    return : tuple[str, str]
        Кортеж с датами начала и окончания.
    """
    if (from_date is None) or (till_date is None):
        raise ValueError("Оба параметра `from_date` и `till_date` должны быть заданы")

    from_date = date.fromisoformat(from_date) if isinstance(from_date, str) else (from_date or date.today())
    if not till_date:
        till_date = from_date
    elif isinstance(till_date, str):
        till_date = date.today() if till_date == "today" else date.fromisoformat(till_date)

    if from_date > till_date:
        raise ValueError("Параметр `from_date` должен быть меньше или равный `till_date`")

    return from_date.isoformat(), till_date.isoformat()


def calc_offset_limit(
    offset: int = None,
    limit: int = None,
    min_limit: int = 1,
    standart_limit: int = 10_000,
    max_limit: int = 50_000,
    min_offset: int = 0,
) -> tuple[int, int]:
    """
    Вычисление смещения и лимита.

    Parameters
    ----------
    offset : int, optional
        Смещение относительно начала, by default None.
    limit : int, optional
        Лимит данных, by default None.

    Returns
    -------
    return : tuple[int, int]
        Кортеж со смещением и лимитом.
    """
    offset = offset or min_offset
    if limit != -1:
        limit = limit or standart_limit

        limit = min_limit if limit < min_limit else max_limit if limit > max_limit else limit
        offset = min_offset if offset < min_offset else max_limit - 1 if offset >= max_limit else offset

    return offset, limit


def normalize_data(data: Iterable[dict[str, Any]], *fields: str | tuple[str, str]) -> Iterable[dict[str, Any]]:
    names = {"secid": "ticker", "boardid": "board"}
    names.update(dict((f, f) if isinstance(f, str) else (f[0], f[1]) for f in fields))

    keys = [names.get(name.lower(), name.lower()) for name in data["columns"]]
    rows = data["data"]
    data = [dict(zip(keys, row)) for row in rows]
    if fields:
        keys = tuple(names.values())
        return [dict((k, v) for k, v in row.items() if k in keys) for row in data]
    return data


def result_adapter(result: dict | Iterable[dict], native: bool) -> dict | Iterable[dict] | DataFrame | None:
    """Преобразует результат в `pandas.DataFrame` если применимо."""
    use_dataframe = not native and pd is not None
    if use_dataframe:
        if result is None:
            return None
        result = pd.DataFrame([result] if isinstance(result, dict) else list(result))
    return result
