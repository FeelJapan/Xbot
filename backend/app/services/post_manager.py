"""
投稿管理サービス
投稿の作成、編集、管理を行う機能
"""
import json
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from backend.core.logging.logger import get_logger
from backend.app.services.content_generator import ContentGenerator
from backend.app.services.image_generator import ImageGenerator
from backend.app.services.video_generator import VideoGenerator
from backend.app.services.x_service import XService

logger = get_logger("post_manager")

class PostError(Exception):
    """投稿管理関連のエラー"""
    pass

class PostStatus(Enum):
    """投稿ステータス"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"

class PostType(Enum):
    """投稿タイプ"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"

@dataclass
class PostContent:
    """投稿コンテンツ"""
    text: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    links: List[str] = None

@dataclass
class PostTemplate:
    """投稿テンプレート"""
    name: str
    description: str
    content_template: str
    hashtags: List[str]
    mentions: List[str]
    post_type: PostType
    enabled: bool = True
    tone: str = "professional"  # professional, casual, formal, friendly
    max_length: int = 280
    include_link: bool = False
    include_media: bool = False

@dataclass
class Post:
    """投稿情報"""
    id: str
    content: PostContent
    scheduled_time: Optional[datetime]
    status: PostStatus
    post_type: PostType
    template_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None
    engagement_stats: Optional[Dict[str, Any]] = None

class PostManager:
    """投稿管理クラス"""
    
    def __init__(self, data_dir: str = "data/posts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.posts_file = self.data_dir / "posts.json"
        self.templates_file = self.data_dir / "templates.json"
        self.drafts_file = self.data_dir / "drafts.json"
        
        # サービス初期化
        self.content_generator = ContentGenerator()
        self.image_generator = ImageGenerator()
        self.video_generator = VideoGenerator()
        self.x_service = XService()
        
        # データ読み込み
        self.posts: Dict[str, Post] = {}
        self.templates: Dict[str, PostTemplate] = {}
        self.drafts: Dict[str, Post] = {}
        self.load_data()
        
    def load_data(self) -> None:
        """データを読み込み"""
        try:
            # 投稿データの読み込み
            if self.posts_file.exists():
                with open(self.posts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posts = {
                        post_id: self._dict_to_post(post_data)
                        for post_id, post_data in data.items()
                    }
            
            # テンプレートデータの読み込み
            if self.templates_file.exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = {
                        name: PostTemplate(**template_data)
                        for name, template_data in data.items()
                    }
            
            # 下書きデータの読み込み
            if self.drafts_file.exists():
                with open(self.drafts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.drafts = {
                        draft_id: self._dict_to_post(draft_data)
                        for draft_id, draft_data in data.items()
                    }
                    
            logger.info("投稿管理データを読み込みました")
            
        except Exception as e:
            logger.error(f"投稿管理データの読み込みに失敗しました: {str(e)}")
            self._create_default_data()
    
    def save_data(self) -> None:
        """データを保存"""
        try:
            # 投稿データの保存
            posts_data = {
                post_id: self._post_to_dict(post)
                for post_id, post in self.posts.items()
            }
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, indent=2, ensure_ascii=False)
            
            # テンプレートデータの保存
            templates_data = {
                name: asdict(template)
                for name, template in self.templates.items()
            }
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, indent=2, ensure_ascii=False)
            
            # 下書きデータの保存
            drafts_data = {
                draft_id: self._post_to_dict(draft)
                for draft_id, draft in self.drafts.items()
            }
            with open(self.drafts_file, 'w', encoding='utf-8') as f:
                json.dump(drafts_data, f, indent=2, ensure_ascii=False)
                
            logger.info("投稿管理データを保存しました")
            
        except Exception as e:
            logger.error(f"投稿管理データの保存に失敗しました: {str(e)}")
            raise PostError(f"投稿管理データの保存に失敗しました: {str(e)}")
    
    def _create_default_data(self) -> None:
        """デフォルトデータを作成"""
        # デフォルトテンプレート
        self.templates = {
            "trend_commentary": PostTemplate(
                name="トレンド解説",
                description="YouTubeトレンド動画の解説投稿",
                content_template="🎬 {title}\n\n{commentary}\n\n#YouTube #トレンド",
                hashtags=["YouTube", "トレンド", "解説"],
                mentions=[],
                post_type=PostType.TEXT
            ),
            "funny_observation": PostTemplate(
                name="面白い発見",
                description="日常の面白い発見を投稿",
                content_template="😄 {observation}\n\n{commentary}\n\n#面白い #発見",
                hashtags=["面白い", "発見", "日常"],
                mentions=[],
                post_type=PostType.TEXT
            ),
            "cultural_insight": PostTemplate(
                name="文化的洞察",
                description="外国人視点からの文化的洞察",
                content_template="🌍 {insight}\n\n{commentary}\n\n#文化 #国際",
                hashtags=["文化", "国際", "洞察"],
                mentions=[],
                post_type=PostType.TEXT
            )
        }
        
        self.save_data()
        logger.info("デフォルト投稿テンプレートを作成しました")
    
    def create_post(
        self,
        content: PostContent,
        post_type: PostType = PostType.TEXT,
        template_name: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Post:
        """投稿を作成"""
        try:
            post_id = self._generate_post_id()
            now = datetime.now()
            
            post = Post(
                id=post_id,
                content=content,
                scheduled_time=scheduled_time,
                status=PostStatus.DRAFT if scheduled_time is None else PostStatus.SCHEDULED,
                post_type=post_type,
                template_name=template_name,
                created_at=now,
                updated_at=now
            )
            
            if scheduled_time is None:
                self.drafts[post_id] = post
            else:
                self.posts[post_id] = post
            
            self.save_data()
            logger.info(f"投稿を作成しました: {post_id}")
            return post
            
        except Exception as e:
            logger.error(f"投稿の作成に失敗しました: {str(e)}")
            raise PostError(f"投稿の作成に失敗しました: {str(e)}")
    
    def update_post(self, post_id: str, **kwargs) -> Post:
        """投稿を更新"""
        try:
            post = self.get_post(post_id)
            if post is None:
                raise PostError(f"投稿が見つかりません: {post_id}")
            
            # 更新可能なフィールドを更新
            for key, value in kwargs.items():
                if hasattr(post, key):
                    setattr(post, key, value)
            
            post.updated_at = datetime.now()
            
            # データを保存
            if post_id in self.drafts:
                self.drafts[post_id] = post
            else:
                self.posts[post_id] = post
            
            self.save_data()
            logger.info(f"投稿を更新しました: {post_id}")
            return post
            
        except Exception as e:
            logger.error(f"投稿の更新に失敗しました: {str(e)}")
            raise PostError(f"投稿の更新に失敗しました: {str(e)}")
    
    def delete_post(self, post_id: str) -> bool:
        """投稿を削除"""
        try:
            if post_id in self.posts:
                del self.posts[post_id]
            elif post_id in self.drafts:
                del self.drafts[post_id]
            else:
                return False
            
            self.save_data()
            logger.info(f"投稿を削除しました: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"投稿の削除に失敗しました: {str(e)}")
            raise PostError(f"投稿の削除に失敗しました: {str(e)}")
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """投稿を取得"""
        return self.posts.get(post_id) or self.drafts.get(post_id)
    
    def get_posts(
        self,
        status: Optional[PostStatus] = None,
        post_type: Optional[PostType] = None,
        limit: int = 50
    ) -> List[Post]:
        """投稿一覧を取得"""
        all_posts = list(self.posts.values()) + list(self.drafts.values())
        
        # フィルタリング
        if status:
            all_posts = [post for post in all_posts if post.status == status]
        if post_type:
            all_posts = [post for post in all_posts if post.post_type == post_type]
        
        # 日時順にソート
        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_posts[:limit]
    
    def get_drafts(self) -> List[Post]:
        """下書き一覧を取得"""
        return list(self.drafts.values())
    
    def get_scheduled_posts(self) -> List[Post]:
        """スケジュール済み投稿一覧を取得"""
        return [
            post for post in self.posts.values()
            if post.status == PostStatus.SCHEDULED
        ]
    
    def schedule_post(self, post_id: str, scheduled_time: datetime) -> Post:
        """投稿をスケジュール"""
        try:
            post = self.get_post(post_id)
            if post is None:
                raise PostError(f"投稿が見つかりません: {post_id}")
            
            post.scheduled_time = scheduled_time
            post.status = PostStatus.SCHEDULED
            post.updated_at = datetime.now()
            
            # 下書きから投稿に移動
            if post_id in self.drafts:
                self.posts[post_id] = post
                del self.drafts[post_id]
            
            self.save_data()
            logger.info(f"投稿をスケジュールしました: {post_id} -> {scheduled_time}")
            return post
            
        except Exception as e:
            logger.error(f"投稿のスケジュールに失敗しました: {str(e)}")
            raise PostError(f"投稿のスケジュールに失敗しました: {str(e)}")
    
    async def post_now(self, post_id: str) -> bool:
        """投稿を即座に実行"""
        try:
            post = self.get_post(post_id)
            if post is None:
                raise PostError(f"投稿が見つかりません: {post_id}")
            
            # Xに投稿
            success = await self.x_service.post_tweet(post.content.text)
            
            if success:
                post.status = PostStatus.POSTED
                post.posted_at = datetime.now()
                post.updated_at = datetime.now()
                
                # 下書きから投稿に移動
                if post_id in self.drafts:
                    self.posts[post_id] = post
                    del self.drafts[post_id]
                
                self.save_data()
                logger.info(f"投稿を実行しました: {post_id}")
                return True
            else:
                post.status = PostStatus.FAILED
                post.error_message = "X API投稿に失敗しました"
                post.updated_at = datetime.now()
                self.save_data()
                logger.error(f"投稿の実行に失敗しました: {post_id}")
                return False
                
        except Exception as e:
            logger.error(f"投稿の実行に失敗しました: {str(e)}")
            if post:
                post.status = PostStatus.FAILED
                post.error_message = str(e)
                post.updated_at = datetime.now()
                self.save_data()
            raise PostError(f"投稿の実行に失敗しました: {str(e)}")
    
    def create_post_from_template(
        self,
        template_name: str,
        **kwargs
    ) -> Post:
        """テンプレートから投稿を作成"""
        try:
            template = self.templates.get(template_name)
            if template is None:
                raise PostError(f"テンプレートが見つかりません: {template_name}")
            
            # テンプレートの内容を展開
            content_text = template.content_template.format(**kwargs)
            
            content = PostContent(
                text=content_text,
                hashtags=template.hashtags.copy(),
                mentions=template.mentions.copy()
            )
            
            return self.create_post(
                content=content,
                post_type=template.post_type,
                template_name=template_name
            )
            
        except Exception as e:
            logger.error(f"テンプレートからの投稿作成に失敗しました: {str(e)}")
            raise PostError(f"テンプレートからの投稿作成に失敗しました: {str(e)}")
    
    def add_template(self, name: str, template: PostTemplate) -> None:
        """テンプレートを追加"""
        try:
            self.templates[name] = template
            self.save_data()
            logger.info(f"テンプレートを追加しました: {name}")
            
        except Exception as e:
            logger.error(f"テンプレートの追加に失敗しました: {str(e)}")
            raise PostError(f"テンプレートの追加に失敗しました: {str(e)}")
    
    def get_templates(self) -> Dict[str, PostTemplate]:
        """テンプレート一覧を取得"""
        return self.templates
    
    def get_enabled_templates(self) -> Dict[str, PostTemplate]:
        """有効なテンプレート一覧を取得"""
        return {
            name: template
            for name, template in self.templates.items()
            if template.enabled
        }
    
    def preview_post(self, post_id: str) -> Dict[str, Any]:
        """投稿のプレビューを生成"""
        try:
            post = self.get_post(post_id)
            if post is None:
                raise PostError(f"投稿が見つかりません: {post_id}")
            
            preview = {
                "id": post.id,
                "content": {
                    "text": post.content.text,
                    "image_url": post.content.image_url,
                    "video_url": post.content.video_url,
                    "hashtags": post.content.hashtags,
                    "mentions": post.content.mentions,
                    "links": post.content.links
                },
                "post_type": post.post_type.value,
                "template_name": post.template_name,
                "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                "status": post.status.value,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat()
            }
            
            return preview
            
        except Exception as e:
            logger.error(f"投稿プレビューの生成に失敗しました: {str(e)}")
            raise PostError(f"投稿プレビューの生成に失敗しました: {str(e)}")
    
    def _generate_post_id(self) -> str:
        """投稿IDを生成"""
        import uuid
        return str(uuid.uuid4())
    
    def _post_to_dict(self, post: Post) -> Dict[str, Any]:
        """Postオブジェクトを辞書に変換"""
        return {
            "id": post.id,
            "content": {
                "text": post.content.text,
                "image_url": post.content.image_url,
                "video_url": post.content.video_url,
                "hashtags": post.content.hashtags or [],
                "mentions": post.content.mentions or [],
                "links": post.content.links or []
            },
            "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
            "status": post.status.value,
            "post_type": post.post_type.value,
            "template_name": post.template_name,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
            "posted_at": post.posted_at.isoformat() if post.posted_at else None,
            "error_message": post.error_message,
            "engagement_stats": post.engagement_stats
        }
    
    def _dict_to_post(self, data: Dict[str, Any]) -> Post:
        """辞書をPostオブジェクトに変換"""
        content_data = data.get("content", {})
        content = PostContent(
            text=content_data.get("text", ""),
            image_url=content_data.get("image_url"),
            video_url=content_data.get("video_url"),
            hashtags=content_data.get("hashtags", []),
            mentions=content_data.get("mentions", []),
            links=content_data.get("links", [])
        )
        
        return Post(
            id=data["id"],
            content=content,
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]) if data.get("scheduled_time") else None,
            status=PostStatus(data["status"]),
            post_type=PostType(data["post_type"]),
            template_name=data.get("template_name"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            posted_at=datetime.fromisoformat(data["posted_at"]) if data.get("posted_at") else None,
            error_message=data.get("error_message"),
            engagement_stats=data.get("engagement_stats")
        ) 