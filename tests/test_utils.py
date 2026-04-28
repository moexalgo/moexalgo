from moexalgo.utils import calc_offset_limit


def test_calc_offset_limit_does_not_cap_large_offsets():
    assert calc_offset_limit(69_000, 10_000) == (69_000, 10_000)


def test_calc_offset_limit_still_caps_limit():
    assert calc_offset_limit(0, 100_000) == (0, 50_000)
