from datetime import datetime, time, timedelta
from typing import Any, Iterable

from moexalgo.features.common import CommonMarket
from moexalgo.session import Session
from moexalgo.utils import DataFrame, result_adapter, normalize_data


class ExtraMarketMixin:
    """
    Миксин добавляющий методы: `trades`, `candles` обобщенному классу `Market`.
    """

    def trades(
        self: CommonMarket,
        tradeno: int | None = None,
        recno: int | None = None,
        *,
        native: bool = False,
    ) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Возвращает последние сделки в обратной сортировке если `tradeno`/`recno` не заданно.
        Если задано сделки возвращаются от заданного `tradeno`/`recno`.

        Parameters
        ----------
        tradeno :
            Номер сделки до которого выдаются данные, для валютного и фондового рынка.
        recno :
            Номер порядка заключения сделок, для срочного рынка.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        key = "recno" if self.market in ("forts", "options") else "tradeno"
        options = dict()
        if tradeno is not None:
            options[key] = tradeno
        else:
            options["reversed"] = 1
        options["native"] = native
        return result_adapter(fetch_trades(self.engine, self.market, self.boardid, **options), native)

    def candles(self, native: bool = False) -> Iterable[dict[str, Any]] | DataFrame:
        """
        Метод возвращает две последние минутные свечи по всем инструментам рынка.

        Parameters
        ----------
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        data = list(reversed(list(self.trades(native=True))))
        if data:
            today = datetime.fromisoformat(data[-1]["systime"]).date()
            finish = datetime.combine(today, time.fromisoformat(data[-1]["tradetime"]))
            start = datetime.combine(today, time.fromisoformat(data[0]["tradetime"]))
            begin = datetime.fromtimestamp(int(finish.timestamp() / 60) * 60)
            end = begin + timedelta(minutes=1) - timedelta(microseconds=1)
            begin = begin - timedelta(minutes=1)
            while begin < start:
                tradeno = (int(data[0]["tradeno"]) - 3000) if data[0]["tradeno"] > 3000 else 0
                prev = [prev for prev in self.trades(tradeno, native=True) if prev["tradeno"] < data[0]["tradeno"]]
                data = prev + data
                start = datetime.combine(today, time.fromisoformat(data[0]["tradetime"]))
            trades = [
                trade
                for trade in [
                    dict(
                        ticker=r["ticker"],
                        tradetime=datetime.combine(today, time.fromisoformat(r["tradetime"])),
                        price=r["price"],
                        quantity=r.get("quantity"),
                        value=r.get("value"),
                    )
                    for r in data
                ]
                if begin <= trade["tradetime"] <= end
            ]
            data = make_candles(trades, begin, 60)
        return result_adapter(data, native)


def fetch_trades(engine, market: str, boardid: str, **options) -> Iterable[dict[str, Any]]:
    with Session() as client:
        return normalize_data(
            client.get_objects(
                f"engines/{engine}/markets/{market}/boards/{boardid}/trades", lambda data: data["trades"], **options
            )
        )


def make_candles(trades: list[dict[str, Any]], begin: datetime, interval: int) -> list[dict[str, Any]]:

    def make_candles_(ticker, data, end_):
        return dict(
            ticker=ticker,
            open=data[0]["price"],
            high=max(item["price"] for item in data),
            low=min(item["price"] for item in data),
            close=data[-1]["price"],
            volume=int(sum(item["quantity"] or 0 for item in data)),
            value=round(sum(item["value"] or 0 for item in data), 1),
            begin=end_ - timedelta(seconds=interval),
            end=(
                data[-1]["tradetime"]
                if end_ - timedelta(microseconds=1) >= datetime.now()
                else end_ - timedelta(microseconds=1)
            ).replace(microsecond=0),
        )

    trades_ = dict()
    for trade in sorted(trades, key=lambda t: (t["ticker"], t["tradetime"])):
        trades_.setdefault(trade["ticker"], []).append(trade)
    candles = []
    for ticker, trades in trades_.items():
        data = []
        end_ = begin + timedelta(seconds=interval)
        for trade in trades:
            if trade["tradetime"] < end_:
                data.append(trade)
            else:
                if data:
                    candles.append(make_candles_(ticker, data, end_))
                data = []
                end_ += timedelta(seconds=interval)
        if data:
            candles.append(make_candles_(ticker, data, end_))
    return candles
