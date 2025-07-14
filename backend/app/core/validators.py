import google.generativeai as genai
from app.core.config import settings
from typing import Tuple, Optional

def validate_gemini_settings() -> Tuple[bool, Optional[str]]:
    """
    Gemini API設定の検証を行う
    
    Returns:
        Tuple[bool, Optional[str]]: (検証結果, エラーメッセージ)
    """
    try:
        # APIキーの検証
        if not settings.GEMINI_API_KEY:
            return False, "Gemini APIキーが設定されていません"
            
        # APIキーの形式検証
        if not settings.GEMINI_API_KEY.startswith("AI"):
            return False, "無効なGemini APIキーの形式です"
            
        # モデルの検証
        if settings.GEMINI_MODEL not in ["gemini-pro", "gemini-pro-vision"]:
            return False, "無効なGeminiモデルが指定されています"
            
        # トークン制限の検証
        if not (1 <= settings.GEMINI_MAX_TOKENS <= 32768):
            return False, "無効な最大トークン数が指定されています"
            
        # API接続テスト
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
        response = model.generate_content("Hello")
        
        if not response.text:
            return False, "Gemini APIからの応答が不正です"
            
        return True, None
        
    except Exception as e:
        return False, f"Gemini API設定の検証中にエラーが発生しました: {str(e)}" 