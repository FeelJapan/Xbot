from pydantic import BaseModel
from typing import List, Optional, Dict

class ApiSettings(BaseModel):
    xApiKey: Optional[str] = None
    youtubeApiKey: Optional[str] = None
    openaiApiKey: Optional[str] = None
    geminiApiKey: Optional[str] = None

class TrendSettings(BaseModel):
    # 検索条件の設定
    searchInterval: int = 3600
    maxResults: int = 10
    minViewCount: int = 10000
    targetRegions: List[str] = ["JP", "US"]
    keywords: List[str] = []
    categories: List[str] = []
    language: str = "ja"
    timeRange: str = "day"  # day, week, month

    # 分析パラメータの調整
    buzzScoreWeights: Dict[str, float] = {
        "viewCount": 0.3,
        "engagement": 0.25,
        "commentActivity": 0.2,
        "channelInfluence": 0.15,
        "sentiment": 0.1
    }
    engagementThreshold: float = 0.1
    commentAnalysisDepth: int = 100
    sentimentAnalysisPrecision: float = 0.8

    # データ管理設定
    cacheEnabled: bool = True
    cacheExpiration: int = 3600  # 秒
    backupEnabled: bool = True
    backupInterval: int = 86400  # 秒
    dataRetentionDays: int = 30
    cleanupEnabled: bool = True

class ThemeSettings(BaseModel):
    categories: List[str] = []
    priority: int = 1
    seasonalEvents: bool = True

class AiSettings(BaseModel):
    promptTemplate: Optional[str] = None
    temperature: float = 0.7
    maxTokens: int = 1000
    style: str = "casual"

class Settings(BaseModel):
    api: ApiSettings
    trend: TrendSettings
    theme: ThemeSettings
    ai: AiSettings 