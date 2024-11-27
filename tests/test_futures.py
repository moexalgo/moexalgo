from datetime import date

import pandas as pd
import pytest

from moexalgo import Ticker
from moexalgo.futures import Futures


def test_candles_futures():
    AKM4 = Futures('AKM4', 'RFUD')
    it = AKM4.candles(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)

    it = AKM4.candles(start='2024-04-22', end='2024-04-22', use_dataframe=True)
    assert isinstance(it, pd.DataFrame)

    it = AKM4.tradestats(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


def test_futures_ticker():
    AKM4 = Ticker('AKM4')
    it = AKM4.candles(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


def test_delisted_shares():
    RIZ2 = Futures('RIZ2', 'RFUD')
    assert RIZ2.delisted
    it = RIZ2.tradestats(start='2022-08-02', end='2022-08-02', use_dataframe=False)
    assert next(it)
    assert next(it)

    it = RIZ2.futoi(start='2022-08-02', end='2022-08-02', use_dataframe=False)
    assert next(it)
    assert next(it)


def test_futures_tradestats():
    AKM4 = Futures('AKM4', 'RFUD')
    AKM4.tradestats(start=date(2024, 4, 22), end='2024-04-22')
    AKM4.tradestats(start=date(2024, 4, 22), end=date(2024, 4, 22))
    AKM4.tradestats(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.tradestats(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.tradestats(start=None, end=None)


def test_futures_obstats():
    AKM4 = Futures('AKM4', 'RFUD')
    AKM4.obstats(start=date(2024, 4, 22), end='2024-04-22')
    AKM4.obstats(start=date(2024, 4, 22), end=date(2024, 4, 22))
    AKM4.obstats(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.obstats(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.obstats(start=None, end=None)


def test_futures_hi2():
    AKM4 = Futures('AKM4', 'RFUD')
    AKM4.hi2(start=date(2024, 4, 22), end='2024-04-22')
    AKM4.hi2(start=date(2024, 4, 22), end=date(2024, 4, 22))
    AKM4.hi2(start='2024-04-22', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.hi2(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.hi2(start=None, end=None)


def test_futures_futoi():
    AKM4 = Futures('AKM4', 'RFUD')
    AKM4.futoi(start=date(2024, 4, 22), end='2024-04-22')
    AKM4.futoi(start=date(2024, 4, 22), end=date(2024, 4, 22))
    AKM4.futoi(start='2024-04-22', end='2024-04-22')
    # with pytest.raises(Exception):
    #     AKM4.futoi(start='2024-04-23', end='2024-04-22')
    with pytest.raises(Exception):
        AKM4.futoi(start=None, end=None)
