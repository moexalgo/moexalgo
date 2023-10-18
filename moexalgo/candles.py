from __future__ import annotations

from datetime import date

import pandas

from moexalgo.models import Candle
from moexalgo.session import Session, data_gen


def pandas_frame(candles_it):
    def normalize_row(row):
        return dict(**{key.lower(): value for key, value in row.items()})

    return pandas.DataFrame([normalize_row(row) for row in candles_it])


def dataclass_it(candles_it):
    for data in candles_it:
        yield Candle(**data)


def prepare_request(cs: Session, path: str, boardid: str, secid: str, *,
                    from_date: str | date = None, till_date: str | date = None,
                    period: str | int = None, offset: int = None, limit: int = None):
    latest = False  # ToDo: Не реализовано в свечах
    period_map = {'1m': 60, '10m': 600, '1h': 3600, '1D': 86400, '1W': 604800, '1M': 2678400, '1Q': 8035200}
    period_norm = {60: 1, 600: 10, 3600: 60, 86400: 24, 604800: 7, 2678400: 31, 8035200: 4}
    period = period or 60
    try:
        period = period_norm[((period * 60 if period in (1, 10, 60) else 3600)
                              if isinstance(period, int) else period_map['1' + period if len(period) == 1 else period])]
    except KeyError:
        raise ValueError("Wrong parameter `period`")
    offset = offset or 0
    limit = limit or 10000
    limit = limit if 1 <= limit <= 50000 else 10000
    offset = offset if 0 <= offset < limit else 0
    from_date = date.fromisoformat(from_date) if isinstance(from_date, str) else (from_date or date.today())
    if till_date:
        if isinstance(till_date, str):
            till_date = date.today() if till_date == 'today' else date.fromisoformat(till_date)
        options = dict(**{'from': from_date.isoformat(), 'till': till_date.isoformat()})
    else:
        options = dict(**{'from': from_date.isoformat(), 'till': from_date.isoformat()})
    options['interval'] = period
    if latest:
        options['latest'] = 1
    path = f'{path}/boards/{boardid}/securities/{secid}/candles'
    return data_gen(cs, path, options, offset, limit, 'candles')
