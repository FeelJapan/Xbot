from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database.base import Base

class VideoStats(Base):
    __tablename__ = "video_stats"

    id = Column(Integer, primary_key=True)
    video_id = Column(String, ForeignKey("trend_videos.video_id"), nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    video = relationship("TrendVideo", back_populates="stats")
    history = relationship("VideoStatsHistory", back_populates="stats")

class VideoStatsHistory(Base):
    __tablename__ = "video_stats_history"

    id = Column(Integer, primary_key=True)
    stats_id = Column(Integer, ForeignKey("video_stats.id"), nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    recorded_at = Column(DateTime, default=datetime.now)

    stats = relationship("VideoStats", back_populates="history")

class TrendVideo(Base):
    __tablename__ = "trend_videos"

    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(String, nullable=False)
    channel_title = Column(String, nullable=False)
    buzz_score = Column(Float, default=0.0)
    collected_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    stats = relationship("VideoStats", back_populates="video", uselist=False) 