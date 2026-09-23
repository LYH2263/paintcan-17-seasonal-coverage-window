import json
import sqlite3

DEFAULT_WINDOW = {
    "enabled": False,
    "start_month": 12, "start_day": 1,
    "end_month": 2, "end_day": 28,
    "coverage": 6.0,
}


def get_map(conn):
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))


def season_window(conn):
    """读取季节窗口配置；缺失或数据损坏时回退默认停用窗口。"""
    row = conn.execute("SELECT value FROM settings WHERE key='season_window'").fetchone()
    if not row:
        return dict(DEFAULT_WINDOW)
    try:
        w = json.loads(row["value"])
        return {
            "enabled": bool(w.get("enabled")),
            "start_month": int(w["start_month"]),
            "start_day": int(w["start_day"]),
            "end_month": int(w["end_month"]),
            "end_day": int(w["end_day"]),
            "coverage": float(w["coverage"]),
        }
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return dict(DEFAULT_WINDOW)


def save_season_window(conn, window: dict):
    conn.execute(
        "INSERT INTO settings(key,value) VALUES('season_window',?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (json.dumps(window, ensure_ascii=False),),
    )
    conn.commit()
