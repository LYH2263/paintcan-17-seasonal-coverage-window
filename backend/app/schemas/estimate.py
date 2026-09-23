from datetime import date

from pydantic import BaseModel


class EstimateRequest(BaseModel):
    room_id: int
    coats: int | None = None
    coverage: float | None = None
    work_date: date | None = None
    persist: bool = True
