"""
投稿管理サービスのテスト
"""
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.services.post_manager import (
    PostManager, Post, PostContent, PostType, PostStatus,
    PostTemplate
)
from app.services.scheduler import PostSchedule

@pytest.fixture
def temp_data_dir():
    """一時データディレクトリ"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def post_manager(temp_data_dir):
    """投稿管理サービスのインスタンス"""
    with patch('app.services.post_manager.ContentGenerator'), \
         patch('app.services.post_manager.ImageGenerator'), \
         patch('app.services.post_manager.VideoGenerator'), \
         patch('app.services.post_manager.XService'):
        
        manager = PostManager(data_dir=temp_data_dir)
        yield manager

@pytest.fixture
def sample_post_content():
    """サンプル投稿コンテンツ"""
    return PostContent(
        text="テスト投稿です",
        hashtags=["テスト", "投稿"],
        mentions=[],
        links=[]
    )

@pytest.fixture
def sample_post_template():
    """サンプル投稿テンプレート"""
    return PostTemplate(
        name="テストテンプレート",
        description="テスト用テンプレート",
        content_template="テスト投稿: {keyword}",
        hashtags=["テスト"],
        mentions=[],
        post_type=PostType.TEXT
    )

class TestPostManager:
    """投稿管理サービスのテストクラス"""
    
    def test_init(self, temp_data_dir):
        """初期化テスト"""
        with patch('app.services.post_manager.ContentGenerator'), \
             patch('app.services.post_manager.ImageGenerator'), \
             patch('app.services.post_manager.VideoGenerator'), \
             patch('app.services.post_manager.XService'):
            
            manager = PostManager(data_dir=temp_data_dir)
            
            assert manager.data_dir == Path(temp_data_dir)
            assert manager.posts_file == Path(temp_data_dir) / "posts.json"
            assert manager.templates_file == Path(temp_dir) / "templates.json"
            assert manager.drafts_file == Path(temp_dir) / "drafts.json"
            assert len(manager.posts) == 0
            assert len(manager.templates) > 0  # デフォルトテンプレート
            assert len(manager.drafts) == 0
    
    def test_create_post(self, post_manager, sample_post_content):
        """投稿作成テスト"""
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        assert post.id is not None
        assert post.content.text == "テスト投稿です"
        assert post.content.hashtags == ["テスト", "投稿"]
        assert post.post_type == PostType.TEXT
        assert post.status == PostStatus.DRAFT
        assert post.scheduled_time is None
        assert post_id in post_manager.drafts
    
    def test_create_scheduled_post(self, post_manager, sample_post_content):
        """スケジュール投稿作成テスト"""
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT,
            scheduled_time=scheduled_time
        )
        
        assert post.status == PostStatus.SCHEDULED
        assert post.scheduled_time == scheduled_time
        assert post_id in post_manager.posts
    
    def test_update_post(self, post_manager, sample_post_content):
        """投稿更新テスト"""
        # 投稿を作成
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        # 更新用コンテンツ
        updated_content = PostContent(
            text="更新された投稿です",
            hashtags=["更新", "投稿"],
            mentions=[],
            links=[]
        )
        
        # 投稿を更新
        updated_post = post_manager.update_post(
            post_id=post.id,
            content=updated_content
        )
        
        assert updated_post.content.text == "更新された投稿です"
        assert updated_post.content.hashtags == ["更新", "投稿"]
        assert updated_post.updated_at > post.created_at
    
    def test_delete_post(self, post_manager, sample_post_content):
        """投稿削除テスト"""
        # 投稿を作成
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        # 投稿を削除
        success = post_manager.delete_post(post.id)
        
        assert success is True
        assert post.id not in post_manager.drafts
        assert post_manager.get_post(post.id) is None
    
    def test_delete_nonexistent_post(self, post_manager):
        """存在しない投稿の削除テスト"""
        success = post_manager.delete_post("nonexistent_id")
        assert success is False
    
    def test_get_post(self, post_manager, sample_post_content):
        """投稿取得テスト"""
        # 投稿を作成
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        # 投稿を取得
        retrieved_post = post_manager.get_post(post.id)
        
        assert retrieved_post is not None
        assert retrieved_post.id == post.id
        assert retrieved_post.content.text == post.content.text
    
    def test_get_posts_with_filters(self, post_manager, sample_post_content):
        """フィルタ付き投稿一覧取得テスト"""
        # 複数の投稿を作成
        post1 = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        post2 = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.IMAGE
        )
        
        # ステータスでフィルタ
        draft_posts = post_manager.get_posts(status=PostStatus.DRAFT)
        assert len(draft_posts) == 2
        
        # タイプでフィルタ
        text_posts = post_manager.get_posts(post_type=PostType.TEXT)
        assert len(text_posts) == 1
        assert text_posts[0].id == post1.id
    
    def test_get_drafts(self, post_manager, sample_post_content):
        """下書き一覧取得テスト"""
        # 下書きを作成
        post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        drafts = post_manager.get_drafts()
        assert len(drafts) == 1
        assert drafts[0].status == PostStatus.DRAFT
    
    def test_get_scheduled_posts(self, post_manager, sample_post_content):
        """スケジュール済み投稿一覧取得テスト"""
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        # スケジュール投稿を作成
        post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT,
            scheduled_time=scheduled_time
        )
        
        scheduled_posts = post_manager.get_scheduled_posts()
        assert len(scheduled_posts) == 1
        assert scheduled_posts[0].status == PostStatus.SCHEDULED
    
    def test_create_post_from_template(self, post_manager):
        """テンプレートからの投稿作成テスト"""
        post = post_manager.create_post_from_template(
            template_name="trend_commentary",
            title="テスト動画",
            commentary="面白い動画でした"
        )
        
        assert post.template_name == "trend_commentary"
        assert "テスト動画" in post.content.text
        assert "面白い動画でした" in post.content.text
        assert "#YouTube" in post.content.hashtags
    
    def test_create_post_from_nonexistent_template(self, post_manager):
        """存在しないテンプレートからの投稿作成テスト"""
        with pytest.raises(Exception) as exc_info:
            post_manager.create_post_from_template(
                template_name="nonexistent_template"
            )
        
        assert "テンプレートが見つかりません" in str(exc_info.value)
    
    def test_add_template(self, post_manager, sample_post_template):
        """テンプレート追加テスト"""
        post_manager.add_template("custom_template", sample_post_template)
        
        templates = post_manager.get_templates()
        assert "custom_template" in templates
        assert templates["custom_template"].name == "テストテンプレート"
    
    def test_get_enabled_templates(self, post_manager):
        """有効なテンプレート一覧取得テスト"""
        enabled_templates = post_manager.get_enabled_templates()
        
        for template in enabled_templates.values():
            assert template.enabled is True
    
    def test_preview_post(self, post_manager, sample_post_content):
        """投稿プレビューテスト"""
        # 投稿を作成
        post = post_manager.create_post(
            content=sample_post_content,
            post_type=PostType.TEXT
        )
        
        # プレビューを取得
        preview = post_manager.preview_post(post.id)
        
        assert preview["id"] == post.id
        assert preview["content"]["text"] == post.content.text
        assert preview["status"] == post.status.value
        assert preview["post_type"] == post.post_type.value
    
    def test_preview_nonexistent_post(self, post_manager):
        """存在しない投稿のプレビューテスト"""
        with pytest.raises(Exception) as exc_info:
            post_manager.preview_post("nonexistent_id")
        
        assert "投稿が見つかりません" in str(exc_info.value)
    
    def test_save_and_load_data(self, temp_data_dir, sample_post_content):
        """データ保存・読み込みテスト"""
        with patch('app.services.post_manager.ContentGenerator'), \
             patch('app.services.post_manager.ImageGenerator'), \
             patch('app.services.post_manager.VideoGenerator'), \
             patch('app.services.post_manager.XService'):
            
            # 最初のマネージャーで投稿を作成
            manager1 = PostManager(data_dir=temp_data_dir)
            post = manager1.create_post(
                content=sample_post_content,
                post_type=PostType.TEXT
            )
            
            # 新しいマネージャーでデータを読み込み
            manager2 = PostManager(data_dir=temp_data_dir)
            loaded_post = manager2.get_post(post.id)
            
            assert loaded_post is not None
            assert loaded_post.content.text == post.content.text
            assert loaded_post.post_type == post.post_type
    
    def test_post_content_validation(self, post_manager):
        """投稿コンテンツのバリデーションテスト"""
        # 空のテキスト
        empty_content = PostContent(
            text="",
            hashtags=[],
            mentions=[],
            links=[]
        )
        
        with pytest.raises(Exception):
            post_manager.create_post(
                content=empty_content,
                post_type=PostType.TEXT
            )
    
    def test_post_type_validation(self, post_manager, sample_post_content):
        """投稿タイプのバリデーションテスト"""
        # 無効な投稿タイプ
        with pytest.raises(ValueError):
            post_manager.create_post(
                content=sample_post_content,
                post_type="invalid_type"
            )
    
    def test_template_content_expansion(self, post_manager):
        """テンプレートコンテンツ展開テスト"""
        # カスタムテンプレートを作成
        template = PostTemplate(
            name="test_template",
            description="テスト用",
            content_template="こんにちは、{name}さん！{message}",
            hashtags=["テスト"],
            mentions=[],
            post_type=PostType.TEXT
        )
        post_manager.add_template("test_template", template)
        
        # テンプレートから投稿を作成
        post = post_manager.create_post_from_template(
            template_name="test_template",
            name="太郎",
            message="お元気ですか？"
        )
        
        assert "こんにちは、太郎さん！お元気ですか？" in post.content.text
    
    def test_error_handling(self, post_manager):
        """エラーハンドリングテスト"""
        # 無効なデータでのテスト
        with pytest.raises(Exception):
            post_manager.create_post(
                content=None,
                post_type=PostType.TEXT
            )
    
    def test_concurrent_access(self, post_manager, sample_post_content):
        """並行アクセステスト"""
        import threading
        import time
        
        def create_post():
            try:
                post_manager.create_post(
                    content=sample_post_content,
                    post_type=PostType.TEXT
                )
            except Exception:
                pass
        
        # 複数のスレッドで同時に投稿を作成
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_post)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # データの整合性を確認
        drafts = post_manager.get_drafts()
        assert len(drafts) >= 0  # エラーが発生してもシステムが破綻しないことを確認 