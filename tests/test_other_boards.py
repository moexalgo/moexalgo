from moexalgo import Ticker


def test_shares_ticker():
    UWGN = Ticker('UWGN')
    it = UWGN.candles(start='2024-04-22', end='2024-04-22', use_dataframe=False)
    assert isinstance(next(it), object)
    assert next(it)
