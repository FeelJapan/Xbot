from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    """
    投稿の基本スキーマ
    
    Attributes:
        content (str): 投稿の内容
        scheduled_time (datetime): 投稿予定時刻
    """
    content: str
    scheduled_time: datetime

class PostCreate(PostBase):
    """
    投稿作成用のスキーマ
    """
    pass

class PostUpdate(PostBase):
    """
    投稿更新用のスキーマ
    
    Attributes:
        posted (Optional[bool]): 投稿済みフラグ
    """
    posted: Optional[bool] = None

class PostInDB(PostBase):
    """
    データベース内の投稿を表すスキーマ
    
    Attributes:
        id (int): 投稿の一意識別子
        posted (bool): 投稿済みフラグ
        created_at (datetime): 作成日時
        updated_at (Optional[datetime]): 更新日時
    """
    id: int
    posted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """
        設定クラス
        
        Attributes:
            from_attributes (bool): ORMモデルからの属性読み込みを有効化
        """
        from_attributes = True 