from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
from app.core.config import settings

router = APIRouter()

class SearchRequest(BaseModel):
    """
    検索リクエストのモデル
    
    Attributes:
        query (str): 検索クエリ文字列
    """
    query: str

@router.post("/search")
async def search_content(request: SearchRequest):
    """
    検索クエリに基づいてXの投稿内容を生成するエンドポイント
    
    Args:
        request (SearchRequest): 検索リクエストオブジェクト
        
    Returns:
        dict: 生成された投稿内容を含む辞書
        
    Raises:
        HTTPException: API呼び出しに失敗した場合
    """
    try:
        # ChatGPT APIを呼び出して投稿内容を生成
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはX（旧Twitter）の投稿を生成するアシスタントです。ユーザーのキーワードに基づいて、魅力的で簡潔な投稿を作成してください。"},
                {"role": "user", "content": f"以下のキーワードに基づいて、Xの投稿を作成してください：{request.query}"}
            ],
            max_tokens=100,
            temperature=0.7,
        )

        # 生成されたテキストを取得
        content = response.choices[0].message.content.strip()

        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 