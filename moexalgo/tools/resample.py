import re
from datetime import datetime, timedelta, date, time


def normalize_period(period: int | str) -> tuple[int, int, str]:
    if isinstance(period, str):
        if found := re.match("([0-9]+)([a-zA-Z]+)", period):
            number, symbol = found.groups()
            number = int(number)
            if period == found.group():
                if symbol == "min":
                    if number in (5, 10, 15):
                        return 1, int(number), f"{number}min"
                    elif number in (20, 30):
                        return 10, int(number), f"{number}min"
                elif symbol in ("h", "H"):
                    if number in (1, 2, 3, 6, 12):
                        return 60, number * 60, f"{number}h"
                elif symbol in ("d", "D"):
                    if number in (1, 5, 10):
                        return 24, number * 60 * 24, f"{number}d"
                elif symbol in ("w", "W"):
                    if number in (1, 2, 4):
                        return 7, number * 60 * 24 * 7, f"{number}d"

    raise ValueError(
        f"Wrong period value: {period}. "
        ""
        "Accepted period values: '1min', '5min', '10min', '15min', '20min', '30min', "
        "'1h', '2h', '3h', '6h', '12h', '1D', '5D', '10D', '1W', '2W', '4W', '1M'"
    )


def _intervals_gen(from_date: date | datetime, period: int):
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    begin = datetime.combine(from_date, time(0))
    end = begin + timedelta(minutes=period)
    while begin.year <= date.today().year:
        yield begin, end - timedelta(seconds=1)
        begin = end
        end = begin + timedelta(minutes=period)


def candles(data, minutes: int):
    accum = list()
    intervals = None

    def make_candle(start, finish):
        candle = dict(
            begin=start.isoformat(), end=finish.isoformat(), open=0, high=0, low=0, close=0, volume=0, value=0
        )
        if accum:
            candle.update(
                {
                    "open": accum[0]["open"],
                    "close": accum[-1]["close"],
                    "high": max([item["high"] for item in accum]),
                    "low": min([item["low"] for item in accum]),
                    "volume": sum([item["volume"] for item in accum]),
                    "value": round(sum([item["value"] for item in accum])),
                }
            )
            accum.clear()
        return candle

    counter = 0
    start = finish = None
    for candle in data:
        begin = datetime.fromisoformat(candle["begin"])
        end = datetime.fromisoformat(candle["end"])
        if intervals is None:
            intervals = _intervals_gen(begin, minutes)
            start, finish = next(intervals)
            while not end <= finish:
                start, finish = next(intervals)
        if begin > finish:
            if accum or counter:
                yield make_candle(start, finish)
                counter += 1
            start, finish = next(intervals)
        if start <= begin and end <= finish:
            accum.append(candle)
    yield make_candle(start, finish)
