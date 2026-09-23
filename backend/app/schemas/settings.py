from pydantic import BaseModel


class SeasonWindowRequest(BaseModel):
    enabled: bool
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    coverage: float
