"""
画像生成サービス
DALL-E APIを使用した画像生成機能
"""
import os
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiohttp
import json
from datetime import datetime

from backend.core.logging.logger import get_logger

logger = get_logger("image_generator")

class ImageGenerationError(Exception):
    """画像生成関連のエラー"""
    pass

class ImageGenerator:
    """DALL-E APIを使用した画像生成クラス"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/images"
        self.default_params = {
            "model": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        }
        
    async def generate_image(
        self, 
        prompt: str, 
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid"
    ) -> Dict[str, Any]:
        """
        画像を生成
        
        Args:
            prompt: 画像生成プロンプト
            size: 画像サイズ
            quality: 画像品質
            style: 画像スタイル
            
        Returns:
            生成された画像の情報
        """
        try:
            if not self.api_key:
                raise ImageGenerationError("OpenAI APIキーが設定されていません")
                
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.default_params["model"],
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "n": self.default_params["n"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url + "/generations",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ImageGenerationError(
                            f"画像生成に失敗しました: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    logger.info(f"画像生成成功: {prompt[:50]}...")
                    return result
                    
        except Exception as e:
            logger.error(f"画像生成エラー: {str(e)}")
            raise ImageGenerationError(f"画像生成中にエラーが発生しました: {str(e)}")
    
    async def generate_variations(
        self, 
        image_path: str, 
        n: int = 1,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        画像のバリエーションを生成
        
        Args:
            image_path: 元画像のパス
            n: 生成するバリエーション数
            size: 画像サイズ
            
        Returns:
            生成されたバリエーション画像の情報
        """
        try:
            if not self.api_key:
                raise ImageGenerationError("OpenAI APIキーが設定されていません")
                
            if not Path(image_path).exists():
                raise ImageGenerationError(f"元画像が見つかりません: {image_path}")
                
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = aiohttp.FormData()
            data.add_field("image", open(image_path, "rb"))
            data.add_field("n", str(n))
            data.add_field("size", size)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url + "/variations",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ImageGenerationError(
                            f"画像バリエーション生成に失敗しました: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    logger.info(f"画像バリエーション生成成功: {n}個")
                    return result
                    
        except Exception as e:
            logger.error(f"画像バリエーション生成エラー: {str(e)}")
            raise ImageGenerationError(f"画像バリエーション生成中にエラーが発生しました: {str(e)}")
    
    def optimize_prompt(self, prompt: str) -> str:
        """
        プロンプトを最適化
        
        Args:
            prompt: 元のプロンプト
            
        Returns:
            最適化されたプロンプト
        """
        # 基本的なプロンプト最適化
        optimized = prompt.strip()
        
        # 画像生成に適した形式に調整
        if not any(keyword in optimized.lower() for keyword in ["photo", "image", "picture", "illustration"]):
            optimized = f"high quality photo of {optimized}"
            
        # 解像度と品質の指定を追加
        optimized += ", high resolution, detailed, professional photography"
        
        return optimized
    
    async def save_generated_image(
        self, 
        image_url: str, 
        save_dir: str = "generated_images"
    ) -> str:
        """
        生成された画像を保存
        
        Args:
            image_url: 画像のURL
            save_dir: 保存ディレクトリ
            
        Returns:
            保存された画像のパス
        """
        try:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            file_path = save_path / filename
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise ImageGenerationError(f"画像のダウンロードに失敗しました: {response.status}")
                    
                    with open(file_path, "wb") as f:
                        f.write(await response.read())
                        
            logger.info(f"画像を保存しました: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"画像保存エラー: {str(e)}")
            raise ImageGenerationError(f"画像保存中にエラーが発生しました: {str(e)}")
    
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """
        生成履歴を取得
        
        Returns:
            生成履歴のリスト
        """
        # 実装予定: データベースから生成履歴を取得
        return []
    
    def clear_history(self) -> bool:
        """
        生成履歴をクリア
        
        Returns:
            クリア成功フラグ
        """
        # 実装予定: データベースの生成履歴をクリア
        logger.info("生成履歴をクリアしました")
        return True 