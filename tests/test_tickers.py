import pytest
from moexalgo import Ticker, Market, Stock, Index, Futures, Currency
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

    fut = Market('futures')
    akm4 = Ticker('AKM4')
    assert isinstance(akm4, Futures)
    assert akm4._boardid == fut._boardid == 'RFUD'
    assert akm4._market == fut

    riz2 = Ticker('RIZ2')
    assert isinstance(riz2, Futures)
    assert riz2._boardid == fut._boardid == 'RFUD'
    assert riz2._market == fut

    cur = Market('currency')
    cny = Ticker('CNY000000TOD')
    assert isinstance(cny, Currency)
    assert cny._boardid == cur._boardid == 'CETS'
    assert cny._market == cur


def test_tickers_iter():
    moex = Ticker('MOEX')
    it = moex.candles(start='2024-01-10', end='2024-01-10', use_dataframe=False)
    assert isinstance(next(it), Candle)
    next(it)

    it = moex.tradestats(start='2024-01-10', end='2024-01-10', use_dataframe=False)
    assert isinstance(next(it), object)
    next(it)


if __name__ == '__main__':
    pytest.main()
