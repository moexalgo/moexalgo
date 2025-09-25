import re
import statistics
import typing as t
from datetime import datetime, timedelta, date, time

import moexalgo

try:
    import pandas as pd

    type Data = list[dict[str, t.Any]] | pd.DataFrame
except ImportError:
    type Data = list[dict[str, t.Any]]

type Metrics = t.Literal["tradestats", "orderstats", "obstats"]


def _normalize(data: list[dict[str, t.Any]]) -> list[dict[str, t.Any]]:
    def normalize(item: dict[str, t.Any]):
        if ticker := item.pop('ticker', item.pop('secid', None)):
            end = item.pop('end', None)
            begin = item.pop('begin', None)
            tradedate = item.pop('tradedate', None)
            tradetime = item.pop('tradetime', None)
            if tradedate and tradetime:
                tradedate = date.fromisoformat(tradedate) if isinstance(tradedate, str) else tradedate
                tradetime = time.fromisoformat(tradetime) if isinstance(tradetime, str) else tradetime
                end = datetime.combine(tradedate, tradetime)
                begin = end - timedelta(minutes=5)
            if end and begin:
                begin = datetime.fromisoformat(begin) if isinstance(begin, str) else begin
                end = datetime.fromisoformat(end) if isinstance(end, str) else end
                return dict(ticker=ticker, begin=begin, end=end, **item)
        raise ValueError(f"Wrong item: {item}")

    return list(map(normalize, data))


def _resolve_and_normalize(
        data: list[dict[str, t.Any]]
) -> tuple[Metrics | None, list[dict[str, t.Any]]]:
    metrics = None
    if data:
        match data[0]:
            case {"trades": trades, "vol": vol}:
                if trades and vol:
                    metrics = "tradestats"
            case {"put_orders_b": put_orders, "cancel_orders_b": cancel_orders}:
                if put_orders or cancel_orders:
                    metrics = "orderstats"
            case {"levels_b": levels_b, "levels_s": levels_s}:
                if levels_b or levels_s:
                    metrics = "obstats"
        if metrics:
            data = _normalize(data)
    return metrics, data


def normalize_period(period: int | str):
    if isinstance(period, str):
        if found := re.match("([0-9]+)([a-zA-Z]+)", period):
            number, symbol = found.groups()
            if period == found.group():
                if symbol == "min":
                    number = int(number)
                    if number // 5 == number / 5:
                        return int(number), f"{number}min"
                elif symbol == "h":
                    return int(number) * 60, f"{number}h"
                elif symbol == "d":
                    return int(number) * 60 * 24, f"{number}d"
                elif symbol == "w":
                    return int(number) * 60 * 24 * 7, f"{number}w"
                elif symbol == "m":
                    raise NotImplementedError(f"Period {period} is not supported in this case")
    elif isinstance(period, int):
        if period // 5 == period / 5:
            return period, f"{period}min"
    raise ValueError(f"Wrong period value: {period}")

def normalize_int(value):
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        return None
    return value

def normalize_float(value, decimals=None):
    try:
        value = float(value)
        if decimals is not None:
            value = round(value, decimals)
    except (ValueError, TypeError):
        return None
    return value


def save_(func, items, name):
    items = [item[name] for item in items if item[name] is not None] if items else []
    return func(items) if items else None


def _tradestats_calculator(items: list[dict[str, t.Any]], lotsize: int, decimals: int) -> dict[str, t.Any]:
    TO_MEAN = ['pr_std']
    TO_SUM = ['vol', 'val', 'trades', 'trades_b', 'trades_s', 'vol_b', 'vol_s', 'val_b', 'val_s']
    items = [dict((k, normalize_int(v) if k in (
        'trades', 'trades_b', 'trades_s', 'vol', 'vol_b', 'vol_s',
        'sec_pr_open', 'sec_pr_high', 'sec_pr_low', 'sec_pr_close')
    else (normalize_float(v) if k in (
        'pr_std', 'val', 'val_b', 'val_s',
        'pr_open', 'pr_high', 'pr_low', 'pr_close', 'oi_open', 'oi_high', 'oi_low', 'oi_close'
    ) else v)) for k, v in item.items()) for item in items]

    result = None
    for N in range(len(items)):
        tradestat = items[N]
        offset = tradestat.pop('offset')
        if result is None:
            result = tradestat
            result['sec_pr_open'] = offset + tradestat['sec_pr_open']
            result['sec_pr_high'] = offset + tradestat['sec_pr_high']
            result['sec_pr_low'] = offset + tradestat['sec_pr_low']
            result['sec_pr_close'] = offset + tradestat['sec_pr_close']

        if tradestat['pr_high'] > result['pr_high']:
            result['pr_high'] = tradestat['pr_high']
            result['sec_pr_high'] = offset + tradestat['sec_pr_high']
        if tradestat['pr_low'] < result['pr_low']:
            result['pr_low'] = offset + tradestat['pr_low']
            result['sec_pr_low'] = offset + tradestat['sec_pr_low']
        result['pr_close'] = tradestat['pr_close']
        result['sec_pr_close'] = offset + tradestat['sec_pr_close']
        if 'im' in tradestat:
            result['im'] = tradestat['im']

        if 'oi_open' in tradestat:
            if tradestat['oi_high'] > result['oi_high']:
                result['oi_high'] = tradestat['oi_high']
            if tradestat['oi_low'] < result['oi_low']:
                result['oi_low'] = tradestat['oi_low']
            result['oi_close'] = tradestat['oi_close']

    for name in TO_SUM:
        if name in result:
            result[name] = save_(sum, items, name)
    for name in TO_MEAN:
        if name in result:
            try:
                result[name] = save_(statistics.mean, items, name)
            except statistics.StatisticsError:
                pass
    result['pr_std'] = round(result['pr_std'], 4) if result['pr_std'] else None
    result['pr_change'] = round(100 * (result['pr_close'] - result['pr_open']) / result['pr_open'], 4)
    result['disb'] = (round((result['vol_b'] - result['vol_s']) / result['vol'], 2)
                      if result['vol'] > 0 else None)
    result['pr_vwap'] = round(result['val'] / (result['vol'] * lotsize), decimals) if result['vol'] else None
    result['pr_vwap_b'] = round(result['val_b'] / (result['vol_b'] * lotsize), decimals) if result['vol_b'] else None
    result['pr_vwap_s'] = round(result['val_s'] / (result['vol_s'] * lotsize), decimals) if result['vol_s'] else None

    for key, value in tuple(result.items()):
        if 'val' in key:
            result[key] = normalize_float(value, 0)
    return result


def _orderstats_calculator(items: list[dict[str, t.Any]], lotsize: int, decimals: int) -> dict[str, t.Any]:
    TO_SUM = ['put_orders_b', 'put_orders_s', 'put_val_b', 'put_val_s', 'put_vol_b', 'put_vol_s',
              'put_vol', 'put_val', 'put_orders', 'cancel_orders_b', 'cancel_orders_s', 'cancel_val_b',
              'cancel_val_s', 'cancel_vol_b', 'cancel_vol_s', 'cancel_vol', 'cancel_val', 'cancel_orders']

    items = [dict((k, normalize_int(v) if k in (
        'put_orders', 'put_vol', 'put_orders_b', 'put_orders_s', 'put_vol_b', 'put_vol_s',
        'cancel_orders', 'cancel_vol', 'cancel_orders_b', 'cancel_orders_s', 'cancel_vol_b', 'cancel_vol_s'
    ) else (normalize_float(v) if k in (
        'put_val', 'put_val_b', 'put_val_s', 'cancel_val', 'cancel_val_b', 'cancel_val_s'
    ) else v)) for k, v in item.items()) for item in items]

    result = None
    for N in range(len(items)):
        orderstat = items[N]
        if result is None:
            result = orderstat
            continue
    for name in TO_SUM:
        if name in result:
            result[name] = save_(sum, items, name)
    result['put_vwap_b'] = (round(result['put_val_b'] / (result['put_vol_b'] * lotsize), decimals)
                            if result['put_vol_b'] else None)
    result['cancel_vwap_b'] = (round(result['cancel_val_b'] / (result['cancel_vol_b'] * lotsize), decimals)
                               if result['cancel_vol_b'] else None)
    result['put_vwap_s'] = (round(result['put_val_s'] / (result['put_vol_s'] * lotsize), decimals)
                            if result['put_vol_s'] else None)
    result['cancel_vwap_s'] = (round(result['cancel_val_s'] / (result['cancel_vol_s'] * lotsize), decimals)
                               if result['cancel_vol_s'] else None)
    for key, value in tuple(result.items()):
        if 'val' in key:
            result[key] = normalize_float(value, 0)
    return result


def _obstats_calculator(items: list[dict[str, t.Any]], lotsize: int, decimals: int) -> dict[str, t.Any]:
    TO_MEAN = [
        'spread_bbo', 'spread_lv10', 'spread_1mio', 'spread_l1', 'spread_l10', 'spread_l2', 'spread_l3', 'spread_l5',
        'spread_l20', 'levels_b', 'levels_s', 'imbalance_val', 'imbalance_vol_bbo', 'imbalance_val_bbo', 'vwap_b_1mio',
        'vwap_s_1mio', 'vol_b', 'vol_s', 'val_b', 'val_s', 'vol_b_l1', 'vol_b_l10', 'vol_b_l2', 'vol_b_l3', 'vol_b_l5',
        'vol_b_l20', 'vol_s_l1', 'vol_s_l10', 'vol_s_l2', 'vol_s_l20', 'vol_s_l3', 'vol_s_l5', 'micro_price',
        'mid_price'
    ]

    items = [dict((k, normalize_int(v) if k in (
        'levels_b', 'levels_s', 'vol_b', 'vol_s', 'vol_b_l1', 'vol_b_l10', 'vol_b_l2', 'vol_b_l3',
        'vol_b_l5', 'vol_b_l20', 'vol_s_l1', 'vol_s_l10', 'vol_s_l2', 'vol_s_l20', 'vol_s_l3', 'vol_s_l5'
    ) else (normalize_float(v) if k in (
        'spread_bbo', 'spread_lv10', 'spread_1mio', 'spread_l1', 'spread_l10', 'spread_l2', 'spread_l3',
        'spread_l5', 'spread_l20', 'imbalance_vol_bbo', 'imbalance_val_bbo', 'vwap_b_1mio', 'vwap_s_1mio',
        'val_b', 'val_s', 'micro_price', 'mid_price', 'imbalance_val'
    ) else v)) for k, v in item.items()) for item in items]

    result = None
    for N in range(len(items)):
        obstat = items[N]
        if result is None:
            result = obstat
            continue
    for name in TO_MEAN:
        if name in result:
            try:
                result[name] = save_(statistics.mean, items, name)
            except statistics.StatisticsError:
                pass
    for vwap, val, vol in [
        ('vwap_b', 'val_b', 'vol_b'),
        ('vwap_b_l1', 'val_b_l1', 'vol_b_l1'),
        ('vwap_b_l2', 'val_b_l2', 'vol_b_l2'),
        ('vwap_b_l3', 'val_b_l3', 'vol_b_l3'),
        ('vwap_b_l5', 'val_b_l5', 'vol_b_l5'),
        ('vwap_b_l10', 'val_b_l10', 'vol_b_l10'),
        ('vwap_b_l20', 'val_b_l20', 'vol_b_l20'),
        ('vwap_s', 'val_s', 'vol_s'),
        ('vwap_s_l1', 'val_s_l1', 'vol_s_l1'),
        ('vwap_s_l2', 'val_s_l2', 'vol_s_l2'),
        ('vwap_s_l3', 'val_s_l3', 'vol_s_l3'),
        ('vwap_s_l5', 'val_s_l5', 'vol_s_l5'),
        ('vwap_s_l10', 'val_s_l10', 'vol_s_l10'),
        ('vwap_s_l20', 'val_s_l20', 'vol_s_l20'),

    ]:
        if vol in result and val in result:
            result[vwap] = round(result[val] / (result[vol] * lotsize), decimals) if result[vol] else None

    for key, value in tuple(result.items()):
        if 'spread' in key:
            result[key] = normalize_float(value, 1)
        elif 'imbalance' in key:
            result[key] = normalize_float(value, 2)
        elif 'val' in key:
            result[key] = normalize_float(value, 0)
        elif 'vol' in key or 'levels' in key:
            result[key] = normalize_int(value)
        elif 'vwap' in key or 'price' in key:
            result[key] = normalize_float(value, decimals)
    return result


class Resampler:

    def __init__(self, metrics: Metrics, ticker: str, from_date: date, period: int, *args):
        match metrics:
            case "tradestats":
                self._calculator = _tradestats_calculator
            case "orderstats":
                self._calculator = _orderstats_calculator
            case "obstats":
                self._calculator = _obstats_calculator
            case _:
                raise NotImplementedError(f"Resampler is not support '{metrics}' metrics")

        self._ticker = ticker
        self._accum = list()
        self._calculator_args = args
        self._intervals = self._intervals_gen(from_date, period)
        self._begin, self._end = next(self._intervals)

    def __call__(self, item: dict[str, t.Any] = None) -> dict[str, t.Any] | None:
        result = None
        if item is not None:
            begin = item.pop('begin')
            end = item.pop('end')
            while not (self._begin <= begin and end <= self._end):
                if result is None:
                    result = self._get_result()
                self._begin, self._end = next(self._intervals)
            item['offset'] = (begin - self._begin).total_seconds()
            self._accum.append(item)
        else:
            result = self._get_result()
        return result

    def _get_result(self):
        result = None
        if self._accum:
            result = dict(ticker=self._ticker, begin=self._begin, end=self._end,
                          **self._calculator(self._accum, *self._calculator_args))
            result.pop('offset', None)
            self._accum.clear()
        return result

    @staticmethod
    def _intervals_gen(from_date: date, period: int):
        begin = datetime.combine(from_date, time(0))
        end = begin + timedelta(minutes=period)
        while begin.year <= date.today().year:
            yield begin, end
            begin = end
            end = begin + timedelta(minutes=period)

    @classmethod
    def it(cls, metrics, data: list[dict[str, t.Any]], period: int):
        resamplers = dict()
        ticker_args = dict(
            (item['SECID'], (item.get('LOTSIZE', item.get('LOTVOLUME', -1)), item['DECIMALS']))
            for item in sum(list([a for a in item]
                                 for item in [market.tickers(use_dataframe=False)
                                              for market in [moexalgo.Market(market)
                                                             for market in ['EQ', 'FX', 'FO']]]), start=[])
        )
        for item in data:
            ticker = item.pop('ticker')
            if ticker in ticker_args:
                resampler = resamplers.setdefault(ticker,
                                                  cls(metrics, ticker, item['begin'].date(), period, *ticker_args[ticker]))
                if result := resampler(item):
                    yield result
        for resampler in resamplers.values():
            if result := resampler():
                yield result


def resample(data: Data, period: int | str) -> Data:
    if not isinstance(data, list):
        data = data.to_dict('records')
        used_fd = True
    else:
        used_fd = False
    period, _ = normalize_period(period)
    metrics, data = _resolve_and_normalize(data)
    if metrics is None:
        raise NotImplementedError("Resample is not implement for this data")
    result = list(Resampler.it(metrics, data, period))
    return pd.DataFrame(result) if used_fd else result
