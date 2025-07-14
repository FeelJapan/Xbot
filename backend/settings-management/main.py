from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
import json
import os
from pathlib import Path

app = FastAPI(title="Settings Management Service")

# 設定ファイルのパス
SETTINGS_DIR = Path("config")
SETTINGS_DIR.mkdir(exist_ok=True)

class APISettings(BaseModel):
    x_api_key: Optional[str] = None
    x_api_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

class TrendAnalysisSettings(BaseModel):
    search_conditions: Dict = {}
    analysis_parameters: Dict = {}
    update_frequency: int = 60  # 分単位
    data_retention_days: int = 30
    analysis_targets: Dict = {}

class PostThemeSettings(BaseModel):
    categories: Dict = {}
    priorities: Dict = {}
    seasonal_events: Dict = {}
    post_styles: Dict = {}
    auto_suggestions: bool = False

class AISettings(BaseModel):
    prompt_templates: Dict = {}
    generation_parameters: Dict = {}
    style_settings: Dict = {}
    quality_settings: Dict = {}
    history_enabled: bool = True

def load_settings(file_name: str) -> Dict:
    file_path = SETTINGS_DIR / f"{file_name}.json"
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_settings(file_name: str, settings: Dict):
    file_path = SETTINGS_DIR / f"{file_name}.json"
    with open(file_path, "w") as f:
        json.dump(settings, f, indent=2)

@app.get("/api/settings")
async def get_api_settings():
    return load_settings("api")

@app.post("/api/settings")
async def update_api_settings(settings: APISettings):
    save_settings("api", settings.dict())
    return {"message": "API settings updated successfully"}

@app.get("/trend-analysis/settings")
async def get_trend_analysis_settings():
    return load_settings("trend_analysis")

@app.post("/trend-analysis/settings")
async def update_trend_analysis_settings(settings: TrendAnalysisSettings):
    save_settings("trend_analysis", settings.dict())
    return {"message": "Trend analysis settings updated successfully"}

@app.get("/post-theme/settings")
async def get_post_theme_settings():
    return load_settings("post_theme")

@app.post("/post-theme/settings")
async def update_post_theme_settings(settings: PostThemeSettings):
    save_settings("post_theme", settings.dict())
    return {"message": "Post theme settings updated successfully"}

@app.get("/ai/settings")
async def get_ai_settings():
    return load_settings("ai")

@app.post("/ai/settings")
async def update_ai_settings(settings: AISettings):
    save_settings("ai", settings.dict())
    return {"message": "AI settings updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
