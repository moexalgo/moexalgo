from moexalgo import Ticker


def test_trades_shares():
    moex = Ticker('MOEX')
    it = moex.trades(use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)

    SBER = Ticker('SBER')
    it = SBER.tradestats(start='2024-05-06', end='2024-05-06', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)


def test_trades_currency():
    CNY000000TOD = Ticker('CNY000000TOD')
    it = CNY000000TOD.trades(use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)
