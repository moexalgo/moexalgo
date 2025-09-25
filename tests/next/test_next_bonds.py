import pytest

from moexalgo.next import Market, Ticker


def test_next_market_bonds(apikey):
    bonds = Market("bonds")
    assert list(bonds.tickers())
    with pytest.raises(AttributeError):
        assert bonds.info()


def test_next_ticker_bonds(apikey):
    su25085rmfs0 = Ticker("SU25085RMFS0")
    assert su25085rmfs0.info()
    with pytest.raises(AttributeError):
        assert su25085rmfs0.tickers()

    bond = Ticker("SU26212RMFS9")
    candles = bond.candles("2025-09-19", "2025-09-19", "10min")
    assert list(candles)

    trades = bond.trades()
    assert list(trades)
