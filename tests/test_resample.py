import moexalgo
import moexalgo.tools


def test_resample_trades():
    moex = moexalgo.Ticker('MOEX')
    data_5m = moex.obstats(start="2025-01-01", end="2025-01-31")
    data_1d = moexalgo.tools.resample(data_5m, period="1d")
    assert data_1d

