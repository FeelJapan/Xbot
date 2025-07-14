from sqlalchemy.orm import Session
from app.models.settings import Settings as SettingsModel
from app.schemas.settings import Settings as SettingsSchema

def get_settings(db: Session, settings_id: int = 1):
    return db.query(SettingsModel).filter(SettingsModel.id == settings_id).first()

def create_settings(db: Session, settings: SettingsSchema):
    db_settings = SettingsModel(
        # API設定
        x_api_key=settings.api.xApiKey,
        youtube_api_key=settings.api.youtubeApiKey,
        openai_api_key=settings.api.openaiApiKey,
        gemini_api_key=settings.api.geminiApiKey,
        
        # トレンド分析設定
        search_interval=settings.trend.searchInterval,
        max_results=settings.trend.maxResults,
        min_view_count=settings.trend.minViewCount,
        target_regions=settings.trend.targetRegions,
        
        # 投稿テーマ設定
        categories=settings.theme.categories,
        priority=settings.theme.priority,
        seasonal_events=settings.theme.seasonalEvents,
        
        # 生成AI設定
        prompt_template=settings.ai.promptTemplate,
        temperature=int(settings.ai.temperature * 100),  # 0-100の整数に変換
        max_tokens=settings.ai.maxTokens,
        style=settings.ai.style,
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_settings(db: Session, settings: SettingsSchema, settings_id: int = 1):
    db_settings = get_settings(db, settings_id)
    if db_settings is None:
        return create_settings(db, settings)
    
    # API設定
    db_settings.x_api_key = settings.api.xApiKey
    db_settings.youtube_api_key = settings.api.youtubeApiKey
    db_settings.openai_api_key = settings.api.openaiApiKey
    db_settings.gemini_api_key = settings.api.geminiApiKey
    
    # トレンド分析設定
    db_settings.search_interval = settings.trend.searchInterval
    db_settings.max_results = settings.trend.maxResults
    db_settings.min_view_count = settings.trend.minViewCount
    db_settings.target_regions = settings.trend.targetRegions
    
    # 投稿テーマ設定
    db_settings.categories = settings.theme.categories
    db_settings.priority = settings.theme.priority
    db_settings.seasonal_events = settings.theme.seasonalEvents
    
    # 生成AI設定
    db_settings.prompt_template = settings.ai.promptTemplate
    db_settings.temperature = int(settings.ai.temperature * 100)
    db_settings.max_tokens = settings.ai.maxTokens
    db_settings.style = settings.ai.style
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

def convert_to_schema(db_settings: SettingsModel) -> SettingsSchema:
    return SettingsSchema(
        api={
            "xApiKey": db_settings.x_api_key,
            "youtubeApiKey": db_settings.youtube_api_key,
            "openaiApiKey": db_settings.openai_api_key,
            "geminiApiKey": db_settings.gemini_api_key,
        },
        trend={
            "searchInterval": db_settings.search_interval,
            "maxResults": db_settings.max_results,
            "minViewCount": db_settings.min_view_count,
            "targetRegions": db_settings.target_regions,
        },
        theme={
            "categories": db_settings.categories,
            "priority": db_settings.priority,
            "seasonalEvents": db_settings.seasonal_events,
        },
        ai={
            "promptTemplate": db_settings.prompt_template,
            "temperature": db_settings.temperature / 100,  # 0-1の浮動小数点数に変換
            "maxTokens": db_settings.max_tokens,
            "style": db_settings.style,
        },
    ) 