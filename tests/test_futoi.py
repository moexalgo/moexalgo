from moexalgo import Futures, Market


def test_futures_ticker_futoi():
    SiU4 = Futures('SiU4')
    it = SiU4.futoi(start="2024-04-22", end='2024-04-22', use_dataframe=False)
    assert next(it)
    assert next(it)

    cnt = 0
    for _ in it:
        cnt += 1
        assert cnt < 9000, "Infinity loop"
    assert cnt


def test_futures_market_futoi():
    fo = Market('FO')
    it = fo.futoi(date="2024-04-22", use_dataframe=False)
    assert next(it)
    assert next(it)

    cnt = 0
    for _ in it:
        cnt += 1
        assert cnt < 9000, "Infinity loop"
    assert cnt