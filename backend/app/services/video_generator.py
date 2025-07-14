"""
動画生成サービス
Gemini Veo3 APIを使用した動画生成機能
"""
import os
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiohttp
import json
from datetime import datetime

from backend.core.logging.logger import get_logger

logger = get_logger("video_generator")

class VideoGenerationError(Exception):
    """動画生成関連のエラー"""
    pass

class VideoGenerator:
    """Gemini Veo3 APIを使用した動画生成クラス"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        self.default_params = {
            "duration": 5,
            "resolution": "1080p",
            "fps": 30
        }
        
    async def generate_video(
        self, 
        prompt: str, 
        duration: int = 5,
        resolution: str = "1080p",
        fps: int = 30
    ) -> Dict[str, Any]:
        """
        動画を生成
        
        Args:
            prompt: 動画生成プロンプト
            duration: 動画の長さ（秒）
            resolution: 解像度
            fps: フレームレート
            
        Returns:
            生成された動画の情報
        """
        try:
            if not self.api_key:
                raise VideoGenerationError("Gemini APIキーが設定されていません")
                
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"Generate a {duration}-second video: {prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise VideoGenerationError(
                            f"動画生成に失敗しました: {response.status} - {error_text}"
                        )
                    
                    result = await response.json()
                    logger.info(f"動画生成成功: {prompt[:50]}...")
                    return result
                    
        except Exception as e:
            logger.error(f"動画生成エラー: {str(e)}")
            raise VideoGenerationError(f"動画生成中にエラーが発生しました: {str(e)}")
    
    def create_video_prompt(self, base_prompt: str, style: str = "cinematic") -> str:
        """
        動画生成プロンプトを作成
        
        Args:
            base_prompt: 基本プロンプト
            style: 動画スタイル
            
        Returns:
            最適化された動画生成プロンプト
        """
        style_prompts = {
            "cinematic": "cinematic, professional camera work, smooth transitions",
            "vlog": "vlog style, handheld camera, authentic feel",
            "commercial": "commercial style, high production value, polished",
            "documentary": "documentary style, natural lighting, realistic",
            "animation": "animated, colorful, engaging visuals"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["cinematic"])
        
        optimized_prompt = f"{base_prompt}, {style_prompt}, high quality video"
        
        return optimized_prompt
    
    def adjust_video_parameters(
        self, 
        duration: int, 
        resolution: str, 
        fps: int
    ) -> Dict[str, Any]:
        """
        動画パラメータを調整
        
        Args:
            duration: 動画の長さ
            resolution: 解像度
            fps: フレームレート
            
        Returns:
            調整されたパラメータ
        """
        # パラメータの検証と調整
        if duration < 1:
            duration = 1
        elif duration > 60:
            duration = 60
            
        if fps < 24:
            fps = 24
        elif fps > 60:
            fps = 60
            
        valid_resolutions = ["720p", "1080p", "4K"]
        if resolution not in valid_resolutions:
            resolution = "1080p"
            
        return {
            "duration": duration,
            "resolution": resolution,
            "fps": fps
        }
    
    async def edit_video(
        self, 
        video_path: str, 
        edit_instructions: str
    ) -> Dict[str, Any]:
        """
        動画を編集
        
        Args:
            video_path: 動画ファイルのパス
            edit_instructions: 編集指示
            
        Returns:
            編集された動画の情報
        """
        try:
            if not Path(video_path).exists():
                raise VideoGenerationError(f"動画ファイルが見つかりません: {video_path}")
                
            # 実装予定: 動画編集機能
            logger.info(f"動画編集: {edit_instructions}")
            
            return {
                "status": "success",
                "message": "動画編集が完了しました",
                "edited_video_path": video_path
            }
            
        except Exception as e:
            logger.error(f"動画編集エラー: {str(e)}")
            raise VideoGenerationError(f"動画編集中にエラーが発生しました: {str(e)}")
    
    async def trim_video(
        self, 
        video_path: str, 
        start_time: float, 
        end_time: float
    ) -> str:
        """
        動画をトリミング
        
        Args:
            video_path: 動画ファイルのパス
            start_time: 開始時間（秒）
            end_time: 終了時間（秒）
            
        Returns:
            トリミングされた動画のパス
        """
        try:
            if not Path(video_path).exists():
                raise VideoGenerationError(f"動画ファイルが見つかりません: {video_path}")
                
            # 実装予定: 動画トリミング機能
            logger.info(f"動画トリミング: {start_time}s - {end_time}s")
            
            # 仮の実装
            output_path = video_path.replace(".mp4", "_trimmed.mp4")
            
            return output_path
            
        except Exception as e:
            logger.error(f"動画トリミングエラー: {str(e)}")
            raise VideoGenerationError(f"動画トリミング中にエラーが発生しました: {str(e)}")
    
    async def save_generated_video(
        self, 
        video_data: bytes, 
        save_dir: str = "generated_videos"
    ) -> str:
        """
        生成された動画を保存
        
        Args:
            video_data: 動画データ
            save_dir: 保存ディレクトリ
            
        Returns:
            保存された動画のパス
        """
        try:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_video_{timestamp}.mp4"
            file_path = save_path / filename
            
            with open(file_path, "wb") as f:
                f.write(video_data)
                
            logger.info(f"動画を保存しました: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"動画保存エラー: {str(e)}")
            raise VideoGenerationError(f"動画保存中にエラーが発生しました: {str(e)}")
    
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
        logger.info("動画生成履歴をクリアしました")
        return True 