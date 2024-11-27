import pytest

from moexalgo import Ticker, Market


def test_market_eq():
    eq = Market('shares')
    it = eq.alerts(date="2024-09-23", use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


def test_shares_ticker():
    SBER = Ticker('SBER')
    it = SBER.alerts(start='2024-09-23', end='2024-09-23', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


# def test_currency_ticker():
#     cny000000tod = Ticker('CNY000000TOD')
#     it = cny000000tod.alerts(start='2024-04-22', end='2024-04-22', use_dataframe=False)
#     assert isinstance(next(it), object)
