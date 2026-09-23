from app.db import connect
from app.engines.estimate import estimate_room
from app.engines.season import pick_coverage, validate_window
from app.repositories import openings, rooms, runs, settings


class PaintService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_rooms(self): return rooms.list_all(self._c)
    def room_detail(self, rid):
        r = rooms.get(self._c, rid)
        if not r: return None
        return {"room": r, "openings": openings.for_room(self._c, rid)}
    def settings(self):
        m = settings.get_map(self._c)
        return {
            "coverage": float(m.get("coverage", "8")),
            "coats": int(m.get("coats", "2")),
            "season_window": settings.season_window(self._c),
        }
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def save_window(self, window):
        cleaned = validate_window(window)
        settings.save_season_window(self._c, cleaned)
        return cleaned
    def estimate(self, room_id, persist, coats=None, coverage=None, work_date=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        default_cov, ct = settings.coverage_coats(self._c)
        ct = int(coats or ct)
        window = settings.season_window(self._c)
        cov, source = pick_coverage(work_date, window, coverage, default_cov)
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        result = estimate_room(r["length"], r["width"], r["height"], ops, cov, ct)
        if persist:
            # 钉选本次实际所用涂布率、来源与施工日，后续改窗口不影响旧条
            payload = {
                "room_id": room_id,
                "coats": ct,
                "coverage": cov,
                "coverage_source": source,
                "work_date": work_date.isoformat() if work_date else None,
            }
            rid = runs.insert(self._c, "estimate", payload, result, room_id)
        else:
            rid = None
        return {
            "run_id": rid,
            "room_id": room_id,
            "coverage_source": source,
            "work_date": work_date.isoformat() if work_date else None,
            **result,
        }
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}
