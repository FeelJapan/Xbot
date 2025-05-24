from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
from app.core.config import settings

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
async def search_content(request: SearchRequest):
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