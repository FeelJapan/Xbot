from datetime import datetime
from dataclasses import dataclass

@dataclass
class TrendData:
    id: int
    keyword: str
    category: str
    timestamp: datetime
    score: float
    engagement_rate: float
    comment_count: int
    view_count: int 