import os

import pytest

from moexalgo import Market, session

session.TOKEN = os.environ["APIKEY"]


def test_market():
    eq = Market("EQ")

    assert len(eq.tickers()) > 50
    assert len(eq.marketdata()) > 50

    it = eq.tradestats(date="2024-01-05")
    assert isinstance(next(it), object)
    data = list(it)
    assert len(data) > 10000

    assert len(eq.trades()) > 10
    assert len(eq.candles()) > 10


if __name__ == "__main__":
    pytest.main()
