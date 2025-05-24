from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    content: str
    scheduled_time: datetime

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    posted: Optional[bool] = None

class PostInDB(PostBase):
    id: int
    posted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 