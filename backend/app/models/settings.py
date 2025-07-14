from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # API設定
    x_api_key = Column(String, nullable=True)
    youtube_api_key = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)
    gemini_api_key = Column(String, nullable=True)
    
    # トレンド分析設定
    search_interval = Column(Integer, default=3600)
    max_results = Column(Integer, default=10)
    min_view_count = Column(Integer, default=10000)
    target_regions = Column(JSON, default=list)
    
    # 投稿テーマ設定
    categories = Column(JSON, default=list)
    priority = Column(Integer, default=1)
    seasonal_events = Column(Boolean, default=True)
    
    # 生成AI設定
    prompt_template = Column(String, nullable=True)
    temperature = Column(Integer, default=70)  # 0-100の整数として保存
    max_tokens = Column(Integer, default=1000)
    style = Column(String, default="casual") 