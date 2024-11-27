import pytest
from moexalgo import Market


def test_markets_creation():
    eq = Market('EQ')
    assert eq == Market('EQ')
    assert eq == Market('shares')
    assert eq == Market('shares', 'TQBR')

    tickers = eq.tickers(use_dataframe=False)
    assert len([ticker for ticker in tickers]) > 50


    it = eq.tradestats(date="2024-01-10", use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


    index = Market('index')
    assert index != eq
    assert index == Market('index', 'SNDX')


def test_market_eq():
    eq = Market('shares')
    assert eq._pref == 'eq'
    it = eq.tradestats(date="2024-01-10", use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)



def test_market_fx():
    fx = Market('currency')
    tickers = fx.tickers(use_dataframe=False)
    assert len([ticker for ticker in tickers]) > 10


    assert fx._pref == 'fx'
    it = fx.tradestats(date="2024-04-22", use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)



def test_market_fo():
    fo = Market('futures')
    tickers = fo.tickers(use_dataframe=False)
    assert len([ticker for ticker in tickers]) > 10

    assert fo._pref == 'fo'
    it = fo.tradestats(date="2024-04-22", use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


def test_futoi():
    fo = Market('FO')
    it = fo.tradestats(date='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


    it = fo.futoi(date='2024-04-08', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


if __name__ == '__main__':
    pytest.main()
