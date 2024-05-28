from moexalgo import Ticker
from moexalgo.currency import Currency
from datetime import date
import pytest
import pandas as pd


def test_candles_currency():
    cny000000tod = Currency('CNY000000TOD', 'CETS')
    it = cny000000tod.candles(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


    it = cny000000tod.candles(start='2024-04-22', end='2024-04-22', use_dataframe=True)
    assert isinstance(it, pd.DataFrame)

    it = cny000000tod.tradestats(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)



def test_currency_ticker():
    cny000000tod = Ticker('CNY000000TOD')
    it = cny000000tod.candles(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    

    it = cny000000tod.tradestats(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)



def test_currency_tradestats():
    cny000000tod = Currency('CNY000000TOD', 'CETS')
    cny000000tod.tradestats(start=date(2024, 4, 22),  end='2024-04-22')
    cny000000tod.tradestats(start=date(2024, 4, 22), end=date(2024, 4, 22))
    cny000000tod.tradestats(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.tradestats(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.tradestats(start=None, end=None)


def test_currency_orderstats():
    cny000000tod = Currency('CNY000000TOD', 'CETS')
    cny000000tod.orderstats(start=date(2024, 4, 22),  end='2024-04-22')
    cny000000tod.orderstats(start=date(2024, 4, 22), end=date(2024, 4, 22))
    cny000000tod.orderstats(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.orderstats(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.orderstats(start=None, end=None)


def test_currency_obstats():
    cny000000tod = Currency('CNY000000TOD', 'CETS')
    cny000000tod.obstats(start=date(2024, 4, 22),  end='2024-04-22')
    cny000000tod.obstats(start=date(2024, 4, 22), end=date(2024, 4, 22))
    cny000000tod.obstats(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.obstats(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.obstats(start=None, end=None)


def test_currency_hi2():
    cny000000tod = Currency('CNY000000TOD', 'CETS')
    cny000000tod.hi2(start=date(2024, 4, 22),  end='2024-04-22')
    cny000000tod.hi2(start=date(2024, 4, 22), end=date(2024, 4, 22))
    cny000000tod.hi2(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.hi2(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        cny000000tod.hi2(start=None, end=None)

