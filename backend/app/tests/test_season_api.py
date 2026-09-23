import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    import importlib

    import app.config
    import app.db
    import app.repositories
    import app.routers
    import app.services.paint_service
    importlib.reload(app.config)
    importlib.reload(app.db)
    for name in ("openings", "rooms", "runs", "settings"):
        importlib.reload(getattr(app.repositories, name))
    importlib.reload(app.services.paint_service)
    for name in ("dashboard", "estimate", "history", "rooms", "settings"):
        importlib.reload(getattr(app.routers, name))
    importlib.reload(app.routers)
    import app.seed
    importlib.reload(app.seed)
    app.seed.init_db()
    import app.main
    importlib.reload(app.main)
    return TestClient(app.main.app)


def test_window_save_validation(client):
    bad = client.put("/api/settings/season-window", json={
        "enabled": True, "start_month": 6, "start_day": 1,
        "end_month": 8, "end_day": 31, "coverage": 0,
    })
    assert bad.status_code == 422
    bad2 = client.put("/api/settings/season-window", json={
        "enabled": True, "start_month": 3, "start_day": 10,
        "end_month": 3, "end_day": 10, "coverage": 6,
    })
    assert bad2.status_code == 422
    ok = client.put("/api/settings/season-window", json={
        "enabled": True, "start_month": 6, "start_day": 1,
        "end_month": 8, "end_day": 31, "coverage": 6,
    })
    assert ok.status_code == 200
    assert client.get("/api/settings").json()["season_window"]["coverage"] == 6.0


def test_window_estimate_and_pinned_history(client):
    client.put("/api/settings/season-window", json={
        "enabled": True, "start_month": 6, "start_day": 1,
        "end_month": 8, "end_day": 31, "coverage": 6,
    })
    # 施工日在窗内：用窗内率 6，而不是默认 8
    r = client.post("/api/estimate", json={
        "room_id": 1, "persist": True, "work_date": "2026-07-15",
    }).json()
    assert r["coverage"] == 6.0
    assert r["coverage_source"] == "season_window"
    assert r["liters"] == round(46.41 * 2 / 6, 2)

    # 窗外：无覆盖值时走默认 8
    out = client.post("/api/estimate", json={
        "room_id": 1, "persist": True, "work_date": "2026-09-01",
    }).json()
    assert out["coverage"] == 8.0 and out["coverage_source"] == "default"

    # 窗外但请求体给覆盖值：用请求值
    ov = client.post("/api/estimate", json={
        "room_id": 1, "persist": True, "work_date": "2026-09-01", "coverage": 10,
    }).json()
    assert ov["coverage"] == 10.0 and ov["coverage_source"] == "request"

    hist = client.get("/api/history").json()["items"]
    pinned = next(h for h in hist if json.loads(h["input_json"]).get("work_date") == "2026-07-15")
    assert json.loads(pinned["input_json"])["coverage"] == 6.0

    # 改窗内率后，旧条所用率与升数不变
    client.put("/api/settings/season-window", json={
        "enabled": True, "start_month": 6, "start_day": 1,
        "end_month": 8, "end_day": 31, "coverage": 4,
    })
    hist2 = client.get("/api/history").json()["items"]
    pinned2 = next(h for h in hist2 if h["id"] == pinned["id"])
    assert json.loads(pinned2["input_json"])["coverage"] == 6.0
    assert json.loads(pinned2["result_json"])["liters"] == r["liters"]

    # 停用窗口后新测走请求体/默认，窗内日期也不再用窗内率
    client.put("/api/settings/season-window", json={
        "enabled": False, "start_month": 6, "start_day": 1,
        "end_month": 8, "end_day": 31, "coverage": 4,
    })
    off = client.post("/api/estimate", json={
        "room_id": 1, "persist": True, "work_date": "2026-07-15",
    }).json()
    assert off["coverage"] == 8.0 and off["coverage_source"] == "default"
