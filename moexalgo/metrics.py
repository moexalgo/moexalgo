from __future__ import annotations

from datetime import date, datetime

import pandas

from moexalgo.session import Session, data_gen


def pandas_frame(metrics_it):
    def normalize_row(row):
        return dict(ticker=row.pop('secid'), **{key.lower(): value for key, value in row.items()})

    return pandas.DataFrame([normalize_row(row) for row in metrics_it])


def dataclass_it(dcls, metrics_it):
    for data in metrics_it:
        data['ts'] = datetime.combine(data.pop('tradedate'), data.pop('tradetime'))
        data.pop('SYSTIME')
        yield dcls(**data)


def prepare_request(metric: str, cs: Session, *, secid: str = None, from_date: str | date = None,
                    till_date: str | date = None, latest: bool = False, offset: int = None, limit: int = None):
    offset = offset or 0
    limit = limit or 10000
    limit = limit if 1 <= limit <= 50000 else 5000
    offset = offset if 0 <= offset < limit else 0
    from_date = date.fromisoformat(from_date) if isinstance(from_date, str) else (from_date or date.today())
    if till_date:
        if isinstance(till_date, str):
            till_date = date.today() if till_date=='today' else date.fromisoformat(till_date)
        options = dict(**{'from': from_date.isoformat(), 'till': till_date.isoformat()})
    else:
        options = dict(**{'date': from_date.isoformat()})
    if latest:
        options['latest'] = 1
    if secid is not None:
        path = f'datashop/algopack/eq/{metric}/{secid.lower()}'
    else:
        path = f'datashop/algopack/eq/{metric}'
    return data_gen(cs, path, options, offset, limit, section='data')
