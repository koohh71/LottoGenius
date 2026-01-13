from pydantic import BaseModel
from typing import List, Optional

class GenerateRequest(BaseModel):
    history_limit: int = 30
    fixed_nums: List[int] = []
    excluded_nums: List[int] = []
    count: int = 5

class AddRoundRequest(BaseModel):
    round_no: Optional[int] = None
    numbers: Optional[List[int]] = None
    bonus: Optional[int] = 0

class StatsResponse(BaseModel):
    frequency: List[dict]
    ranges: List[dict]

class LatestRoundResponse(BaseModel):
    latest_round: int
