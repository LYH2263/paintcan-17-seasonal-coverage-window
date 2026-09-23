from calendar import monthrange
from datetime import date


def _key(month: int, day: int) -> int:
    return month * 100 + day


def is_in_window(d: date, start_month: int, start_day: int, end_month: int, end_day: int) -> bool:
    """月日落点判断；起止为同一年序，start > end 时视为跨年窗口（如 12/01 - 02/28）。"""
    md = _key(d.month, d.day)
    start = _key(start_month, start_day)
    end = _key(end_month, end_day)
    if start <= end:
        return start <= md <= end
    return md >= start or md <= end


def validate_window(window: dict) -> dict:
    """校验并归一化季节窗口；非法配置抛 ValueError。停用状态同样校验，避免启用时带病。"""
    enabled = bool(window.get("enabled"))
    try:
        sm, sd = int(window["start_month"]), int(window["start_day"])
        em, ed = int(window["end_month"]), int(window["end_day"])
        coverage = float(window["coverage"])
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError("窗口字段缺失或格式不正确") from e
    for m, d in ((sm, sd), (em, ed)):
        if not 1 <= m <= 12:
            raise ValueError("月份须在 1-12 之间")
        if not 1 <= d <= monthrange(2000, m)[1]:
            raise ValueError(f"{m} 月没有 {d} 日")
    if coverage <= 0:
        raise ValueError("窗内涂布率须为正数")
    if (sm, sd) == (em, ed):
        raise ValueError("起止月日相同，窗口长度为零，属非法顺序")
    return {
        "enabled": enabled,
        "start_month": sm,
        "start_day": sd,
        "end_month": em,
        "end_day": ed,
        "coverage": coverage,
    }


def pick_coverage(work_date: date | None, window: dict, override: float | None, default: float):
    """施工日落窗内用窗内率；窗外用请求覆盖值，再退回系统默认。返回 (覆盖率, 来源)。"""
    if work_date and window.get("enabled") and is_in_window(
        work_date,
        window["start_month"], window["start_day"],
        window["end_month"], window["end_day"],
    ):
        return float(window["coverage"]), "season_window"
    if override is not None:
        return float(override), "request"
    return float(default), "default"
