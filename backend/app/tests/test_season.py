from datetime import date

import pytest

from app.engines.season import is_in_window, pick_coverage, validate_window

WIN = {"enabled": True, "start_month": 6, "start_day": 1,
       "end_month": 8, "end_day": 31, "coverage": 5.5}
CROSS = {"enabled": True, "start_month": 12, "start_day": 1,
         "end_month": 2, "end_day": 28, "coverage": 5.5}


def test_in_window_normal_bounds():
    assert is_in_window(date(2026, 6, 1), 6, 1, 8, 31)
    assert is_in_window(date(2026, 8, 31), 6, 1, 8, 31)
    assert is_in_window(date(2026, 7, 15), 6, 1, 8, 31)


def test_outside_window_normal():
    assert not is_in_window(date(2026, 5, 31), 6, 1, 8, 31)
    assert not is_in_window(date(2026, 9, 1), 6, 1, 8, 31)
    assert not is_in_window(date(2026, 1, 1), 6, 1, 8, 31)


def test_cross_year_window():
    assert is_in_window(date(2026, 12, 1), 12, 1, 2, 28)
    assert is_in_window(date(2027, 1, 31), 12, 1, 2, 28)
    assert is_in_window(date(2027, 2, 28), 12, 1, 2, 28)
    assert not is_in_window(date(2026, 11, 30), 12, 1, 2, 28)
    assert not is_in_window(date(2027, 3, 1), 12, 1, 2, 28)


def test_pick_uses_window_rate_inside():
    cov, source = pick_coverage(date(2026, 7, 1), WIN, 9.0, 8.0)
    assert cov == 5.5 and source == "season_window"


def test_pick_override_wins_outside():
    cov, source = pick_coverage(date(2026, 9, 1), WIN, 9.0, 8.0)
    assert cov == 9.0 and source == "request"


def test_pick_default_outside_without_override():
    cov, source = pick_coverage(date(2026, 9, 1), WIN, None, 8.0)
    assert cov == 8.0 and source == "default"


def test_pick_disabled_window_falls_back():
    w = dict(WIN, enabled=False)
    cov, source = pick_coverage(date(2026, 7, 1), w, None, 8.0)
    assert cov == 8.0 and source == "default"
    cov, source = pick_coverage(date(2026, 7, 1), w, 7.0, 8.0)
    assert cov == 7.0 and source == "request"


def test_pick_without_date():
    cov, source = pick_coverage(None, WIN, None, 8.0)
    assert cov == 8.0 and source == "default"


def test_validate_rejects_non_positive_coverage():
    with pytest.raises(ValueError):
        validate_window(dict(WIN, coverage=0))
    with pytest.raises(ValueError):
        validate_window(dict(WIN, coverage=-2))


def test_validate_rejects_bad_order():
    # 起止月日相同（零长度窗口）
    with pytest.raises(ValueError):
        validate_window({**WIN, "start_month": 7, "start_day": 10,
                         "end_month": 7, "end_day": 10})


def test_validate_rejects_impossible_day():
    with pytest.raises(ValueError):
        validate_window({**WIN, "end_month": 2, "end_day": 30})
    with pytest.raises(ValueError):
        validate_window({**WIN, "start_month": 13, "start_day": 1})


def test_validate_normalizes_disabled():
    out = validate_window(dict(WIN, enabled=False))
    assert out["enabled"] is False and out["coverage"] == 5.5
