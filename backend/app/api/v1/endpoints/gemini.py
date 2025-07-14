from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings
from typing import Optional, List

router = APIRouter()

# Gemini APIの初期化
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiRequest(BaseModel):
    """Gemini APIリクエストのモデル"""
    prompt: str
    model: Optional[str] = settings.GEMINI_MODEL
    max_tokens: Optional[int] = settings.GEMINI_MAX_TOKENS
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 40

class GeminiResponse(BaseModel):
    """Gemini APIレスポンスのモデル"""
    text: str
    model: str
    usage: dict

@router.post("/generate", response_model=GeminiResponse)
async def generate_text(request: GeminiRequest):
    """
    Gemini APIを使用してテキストを生成する
    
    Args:
        request (GeminiRequest): 生成リクエスト
        
    Returns:
        GeminiResponse: 生成されたテキストと使用情報
    """
    try:
        # モデルの設定
        model = genai.GenerativeModel(
            model_name=request.model,
            generation_config={
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "max_output_tokens": request.max_tokens,
            }
        )
        
        # テキスト生成
        response = model.generate_content(request.prompt)
        
        # レスポンスの整形
        return GeminiResponse(
            text=response.text,
            model=request.model,
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(response.text.split()),
                "total_tokens": len(request.prompt.split()) + len(response.text.split())
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(e)}"
        )

@router.get("/models")
async def list_models():
    """
    利用可能なGeminiモデルの一覧を取得する
    
    Returns:
        List[str]: モデル名のリスト
    """
    try:
        models = genai.list_models()
        return [model.name for model in models if "gemini" in model.name.lower()]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        ) 