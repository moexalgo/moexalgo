import pytest
from pandas import DataFrame

from moexalgo import Market, Ticker, Stock, Index
from moexalgo.models.common import Candle


def test_tickers_creation():
    eq = Market('EQ')
    moex = Ticker('MOEX')
    assert isinstance(moex, Stock)
    assert moex._boardid == eq._boardid == 'TQBR'
    assert moex._market == eq

    ndx = Market('index')
    imoex = Ticker('IMOEX')
    assert isinstance(imoex, Index)
    assert imoex._boardid == ndx._boardid == 'SNDX'
    assert imoex._market == ndx


def test_tickers_iter():
    moex = Ticker('MOEX')
    it = moex.candles(start='2024-01-10', end='2024-01-10', use_dataframe=False)
    assert isinstance(next(it), Candle)

    it = moex.tradestats(start='2024-01-10', end='2024-01-10', use_dataframe=False)
    assert isinstance(next(it), object)


def test_tickers_orderbook():
    moex = Ticker('MOEX')
    ob = moex.orderbook()
    assert isinstance(ob, DataFrame) and len(ob) < 100

    cny000000tod = Ticker('CNY000000TOD')
    with pytest.raises(NotImplementedError):
        cny000000tod.orderbook()

    akm4 = Ticker('AKM4')
    ob = akm4.orderbook()
    assert isinstance(ob, DataFrame) and len(ob) < 100



if __name__ == '__main__':
    pytest.main()
