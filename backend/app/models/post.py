from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base

class Post(Base):
    """
    投稿を表すデータベースモデル
    
    Attributes:
        id (int): 投稿の一意識別子
        content (str): 投稿の内容
        scheduled_time (datetime): 投稿予定時刻
        posted (bool): 投稿済みフラグ
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    posted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 