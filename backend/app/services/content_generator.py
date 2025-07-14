"""
コンテンツ生成サービス
ChatGPT APIを使用したテキストコンテンツ生成機能
"""
import os
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import aiohttp
import json
from datetime import datetime
from dataclasses import dataclass, asdict
import sqlite3
from contextlib import asynccontextmanager

from core.logging.logger import get_logger

logger = get_logger("content_generator")

class ContentGenerationError(Exception):
    """コンテンツ生成関連のエラー"""
    pass

@dataclass
class GenerationRequest:
    """生成リクエスト"""
    prompt: str
    template_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    style: str = "casual"
    language: str = "日本語"

@dataclass
class GenerationResult:
    """生成結果"""
    id: str
    content: str
    prompt: str
    template_name: Optional[str]
    parameters: Dict[str, Any]
    created_at: datetime
    model: str = "gpt-3.5-turbo"
    usage: Optional[Dict[str, int]] = None

@dataclass
class PromptTemplate:
    """プロンプトテンプレート"""
    name: str
    template: str
    description: str
    category: str
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ContentGenerator:
    """ChatGPT APIを使用したコンテンツ生成クラス"""
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = "content_generator.db"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self) -> None:
        """データベースの初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 生成履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS generation_history (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        template_name TEXT,
                        parameters TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        model TEXT NOT NULL,
                        usage TEXT
                    )
                """)
                
                # プロンプトテンプレートテーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_templates (
                        name TEXT PRIMARY KEY,
                        template TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                logger.info("データベースを初期化しました")
                
        except Exception as e:
            logger.error(f"データベース初期化エラー: {str(e)}")
            raise ContentGenerationError(f"データベース初期化に失敗しました: {str(e)}")
    
    async def generate_text(self, request: GenerationRequest) -> GenerationResult:
        """
        テキストを生成
        
        Args:
            request: 生成リクエスト
            
        Returns:
            生成結果
        """
        try:
            if not self.api_key:
                raise ContentGenerationError("OpenAI APIキーが設定されていません")
            
            # プロンプトテンプレートの適用
            final_prompt = self._apply_template(request)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.style, request.language)
                    },
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ContentGenerationError(
                            f"テキスト生成に失敗しました: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # 生成結果を作成
                    generation_result = GenerationResult(
                        id=self._generate_id(),
                        content=content,
                        prompt=final_prompt,
                        template_name=request.template_name,
                        parameters=asdict(request),
                        created_at=datetime.now(),
                        model="gpt-3.5-turbo",
                        usage=result.get("usage")
                    )
                    
                    # 履歴に保存
                    await self._save_to_history(generation_result)
                    
                    logger.info(f"テキスト生成成功: {content[:50]}...")
                    return generation_result
                    
        except Exception as e:
            logger.error(f"テキスト生成エラー: {str(e)}")
            raise ContentGenerationError(f"テキスト生成中にエラーが発生しました: {str(e)}")
    
    async def generate_variations(
        self, 
        base_request: GenerationRequest, 
        count: int = 3
    ) -> List[GenerationResult]:
        """
        複数のバリエーションを生成
        
        Args:
            base_request: 基本リクエスト
            count: 生成するバリエーション数
            
        Returns:
            生成結果のリスト
        """
        try:
            variations = []
            
            for i in range(count):
                # パラメータを少し変更してバリエーションを作成
                variation_request = self._create_variation_request(base_request, i)
                result = await self.generate_text(variation_request)
                variations.append(result)
                
            logger.info(f"{count}個のバリエーションを生成しました")
            return variations
            
        except Exception as e:
            logger.error(f"バリエーション生成エラー: {str(e)}")
            raise ContentGenerationError(f"バリエーション生成中にエラーが発生しました: {str(e)}")
    
    def add_prompt_template(self, template: PromptTemplate) -> None:
        """
        プロンプトテンプレートを追加
        
        Args:
            template: プロンプトテンプレート
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO prompt_templates 
                    (name, template, description, category, parameters, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.name,
                    template.template,
                    template.description,
                    template.category,
                    json.dumps(template.parameters),
                    template.created_at.isoformat(),
                    template.updated_at.isoformat()
                ))
                conn.commit()
                
            logger.info(f"プロンプトテンプレートを追加しました: {template.name}")
            
        except Exception as e:
            logger.error(f"プロンプトテンプレート追加エラー: {str(e)}")
            raise ContentGenerationError(f"プロンプトテンプレートの追加に失敗しました: {str(e)}")
    
    def get_prompt_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """
        プロンプトテンプレートを取得
        
        Args:
            category: カテゴリでフィルタリング（オプション）
            
        Returns:
            プロンプトテンプレートのリスト
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute("""
                        SELECT name, template, description, category, parameters, created_at, updated_at
                        FROM prompt_templates WHERE category = ?
                    """, (category,))
                else:
                    cursor.execute("""
                        SELECT name, template, description, category, parameters, created_at, updated_at
                        FROM prompt_templates
                    """)
                
                templates = []
                for row in cursor.fetchall():
                    template = PromptTemplate(
                        name=row[0],
                        template=row[1],
                        description=row[2],
                        category=row[3],
                        parameters=json.loads(row[4]),
                        created_at=datetime.fromisoformat(row[5]),
                        updated_at=datetime.fromisoformat(row[6])
                    )
                    templates.append(template)
                
                return templates
                
        except Exception as e:
            logger.error(f"プロンプトテンプレート取得エラー: {str(e)}")
            raise ContentGenerationError(f"プロンプトテンプレートの取得に失敗しました: {str(e)}")
    
    def get_generation_history(
        self, 
        limit: int = 50, 
        offset: int = 0,
        template_name: Optional[str] = None
    ) -> List[GenerationResult]:
        """
        生成履歴を取得
        
        Args:
            limit: 取得件数
            offset: オフセット
            template_name: テンプレート名でフィルタリング（オプション）
            
        Returns:
            生成履歴のリスト
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if template_name:
                    cursor.execute("""
                        SELECT id, content, prompt, template_name, parameters, created_at, model, usage
                        FROM generation_history 
                        WHERE template_name = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """, (template_name, limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, content, prompt, template_name, parameters, created_at, model, usage
                        FROM generation_history 
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """, (limit, offset))
                
                history = []
                for row in cursor.fetchall():
                    result = GenerationResult(
                        id=row[0],
                        content=row[1],
                        prompt=row[2],
                        template_name=row[3],
                        parameters=json.loads(row[4]),
                        created_at=datetime.fromisoformat(row[5]),
                        model=row[6],
                        usage=json.loads(row[7]) if row[7] else None
                    )
                    history.append(result)
                
                return history
                
        except Exception as e:
            logger.error(f"生成履歴取得エラー: {str(e)}")
            raise ContentGenerationError(f"生成履歴の取得に失敗しました: {str(e)}")
    
    def clear_history(self, before_date: Optional[datetime] = None) -> int:
        """
        生成履歴をクリア
        
        Args:
            before_date: この日時より前の履歴を削除（オプション）
            
        Returns:
            削除された件数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if before_date:
                    cursor.execute("""
                        DELETE FROM generation_history 
                        WHERE created_at < ?
                    """, (before_date.isoformat(),))
                else:
                    cursor.execute("DELETE FROM generation_history")
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"生成履歴をクリアしました: {deleted_count}件削除")
                return deleted_count
                
        except Exception as e:
            logger.error(f"生成履歴クリアエラー: {str(e)}")
            raise ContentGenerationError(f"生成履歴のクリアに失敗しました: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        生成統計を取得
        
        Returns:
            統計情報
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 総生成回数
                cursor.execute("SELECT COUNT(*) FROM generation_history")
                total_generations = cursor.fetchone()[0]
                
                # 今日の生成回数
                today = datetime.now().date().isoformat()
                cursor.execute("""
                    SELECT COUNT(*) FROM generation_history 
                    WHERE DATE(created_at) = ?
                """, (today,))
                today_generations = cursor.fetchone()[0]
                
                # テンプレート別統計
                cursor.execute("""
                    SELECT template_name, COUNT(*) 
                    FROM generation_history 
                    WHERE template_name IS NOT NULL
                    GROUP BY template_name
                """)
                template_stats = dict(cursor.fetchall())
                
                # 平均文字数
                cursor.execute("SELECT AVG(LENGTH(content)) FROM generation_history")
                avg_length = cursor.fetchone()[0] or 0
                
                return {
                    "total_generations": total_generations,
                    "today_generations": today_generations,
                    "template_stats": template_stats,
                    "average_content_length": round(avg_length, 1)
                }
                
        except Exception as e:
            logger.error(f"統計取得エラー: {str(e)}")
            raise ContentGenerationError(f"統計の取得に失敗しました: {str(e)}")
    
    def _apply_template(self, request: GenerationRequest) -> str:
        """プロンプトテンプレートを適用"""
        if not request.template_name:
            return request.prompt
        
        try:
            templates = self.get_prompt_templates()
            template = next((t for t in templates if t.name == request.template_name), None)
            
            if template:
                return template.template.format(prompt=request.prompt)
            else:
                logger.warning(f"テンプレートが見つかりません: {request.template_name}")
                return request.prompt
                
        except Exception as e:
            logger.error(f"テンプレート適用エラー: {str(e)}")
            return request.prompt
    
    def _get_system_prompt(self, style: str, language: str) -> str:
        """システムプロンプトを取得"""
        style_prompts = {
            "casual": "親しみやすく、カジュアルな口調で",
            "formal": "丁寧で、フォーマルな口調で",
            "humorous": "面白く、ユーモアのある口調で",
            "informative": "情報提供に適した、分かりやすい口調で"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["casual"])
        
        return f"あなたは{language}で{style_prompt}コンテンツを生成するアシスタントです。"
    
    def _create_variation_request(self, base_request: GenerationRequest, index: int) -> GenerationRequest:
        """バリエーションリクエストを作成"""
        # パラメータを少し変更
        temperature_variation = base_request.temperature + (index * 0.1)
        temperature_variation = max(0.1, min(1.0, temperature_variation))
        
        return GenerationRequest(
            prompt=base_request.prompt,
            template_name=base_request.template_name,
            temperature=temperature_variation,
            max_tokens=base_request.max_tokens,
            top_p=base_request.top_p,
            frequency_penalty=base_request.frequency_penalty,
            presence_penalty=base_request.presence_penalty,
            style=base_request.style,
            language=base_request.language
        )
    
    def _generate_id(self) -> str:
        """一意のIDを生成"""
        return f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    async def _save_to_history(self, result: GenerationResult) -> None:
        """生成結果を履歴に保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO generation_history 
                    (id, content, prompt, template_name, parameters, created_at, model, usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.id,
                    result.content,
                    result.prompt,
                    result.template_name,
                    json.dumps(result.parameters),
                    result.created_at.isoformat(),
                    result.model,
                    json.dumps(result.usage) if result.usage else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"履歴保存エラー: {str(e)}")
            # 履歴保存の失敗は致命的ではないので、エラーを投げない 