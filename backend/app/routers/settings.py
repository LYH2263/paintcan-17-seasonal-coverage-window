from fastapi import APIRouter, HTTPException
from app.schemas.settings import SeasonWindowRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.put("/settings/season-window")
def put_season_window(body: SeasonWindowRequest):
    with PaintService() as s:
        try:
            return s.save_window(body.model_dump())
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
