"""
テーマ設定管理サービスのテスト
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from datetime import datetime

from app.services.theme_config_manager import (
    ThemeConfigManager, 
    Category, 
    SeasonalEvent, 
    PostStyle
)
from core.error_handling.error_handler import ConfigError

@pytest.fixture
def temp_config_dir():
    """テスト用の一時設定ディレクトリ"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def theme_manager(temp_config_dir):
    """テスト用のテーマ設定マネージャー"""
    return ThemeConfigManager(config_dir=temp_config_dir)

@pytest.fixture
def sample_category():
    """サンプルカテゴリ"""
    return Category(
        name="テストカテゴリ",
        priority=3,
        keywords=["テスト", "サンプル"],
        seasonal_weight=1.2
    )

@pytest.fixture
def sample_seasonal_event():
    """サンプル季節イベント"""
    return SeasonalEvent(
        name="テストイベント",
        start_date="01-01",
        end_date="01-07",
        categories=["entertainment"],
        weight=1.5
    )

@pytest.fixture
def sample_post_style():
    """サンプル投稿スタイル"""
    return PostStyle(
        name="テストスタイル",
        tone="親しみやすい",
        format="短文",
        length_limit=280,
        language="日本語"
    )

class TestThemeConfigManager:
    """テーマ設定マネージャーのテストクラス"""
    
    def test_init_creates_config_dir(self, temp_config_dir):
        """初期化時に設定ディレクトリが作成されるテスト"""
        manager = ThemeConfigManager(config_dir=temp_config_dir)
        config_dir_path = Path(temp_config_dir)
        assert config_dir_path.exists()
        assert config_dir_path.is_dir()
    
    def test_init_creates_default_config_when_file_not_exists(self, theme_manager):
        """設定ファイルが存在しない場合のデフォルト設定作成テスト"""
        # デフォルト設定が作成されることを確認
        assert len(theme_manager.categories) > 0
        assert len(theme_manager.seasonal_events) > 0
        assert len(theme_manager.post_styles) > 0
        
        # デフォルトカテゴリの確認
        assert "entertainment" in theme_manager.categories
        assert "technology" in theme_manager.categories
        assert "lifestyle" in theme_manager.categories
        assert "culture" in theme_manager.categories
    
    def test_load_config_from_existing_file(self, temp_config_dir):
        """既存の設定ファイルからの読み込みテスト"""
        # テスト用の設定ファイルを作成
        config_data = {
            "categories": {
                "test_category": {
                    "name": "テストカテゴリ",
                    "priority": 3,
                    "keywords": ["テスト"],
                    "seasonal_weight": 1.0,
                    "enabled": True
                }
            },
            "seasonal_events": {},
            "post_styles": {}
        }
        
        config_file = Path(temp_config_dir) / "theme_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        # 設定を読み込み
        manager = ThemeConfigManager(config_dir=temp_config_dir)
        
        assert "test_category" in manager.categories
        assert manager.categories["test_category"].name == "テストカテゴリ"
        assert manager.categories["test_category"].priority == 3
    
    def test_save_config(self, theme_manager):
        """設定保存テスト"""
        # カテゴリを追加
        category = Category(
            name="保存テストカテゴリ",
            priority=2,
            keywords=["保存", "テスト"],
            seasonal_weight=1.1
        )
        theme_manager.categories["save_test"] = category
        
        # 設定を保存
        theme_manager.save_config()
        
        # 設定ファイルが作成されたことを確認
        config_file = Path(theme_manager.config_dir) / "theme_config.json"
        assert config_file.exists()
        
        # 保存された内容を確認
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert "save_test" in saved_data["categories"]
        assert saved_data["categories"]["save_test"]["name"] == "保存テストカテゴリ"
    
    def test_save_config_error(self, theme_manager):
        """設定保存エラーテスト"""
        # 読み取り専用ディレクトリでエラーを発生させる
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigError, match="テーマ設定の保存に失敗しました"):
                theme_manager.save_config()
    
    def test_add_category(self, theme_manager, sample_category):
        """カテゴリ追加テスト"""
        theme_manager.add_category("test_category", sample_category)
        
        assert "test_category" in theme_manager.categories
        assert theme_manager.categories["test_category"].name == "テストカテゴリ"
        assert theme_manager.categories["test_category"].priority == 3
    
    def test_update_category(self, theme_manager, sample_category):
        """カテゴリ更新テスト"""
        # カテゴリを追加
        theme_manager.categories["test_category"] = sample_category
        
        # カテゴリを更新
        theme_manager.update_category("test_category", priority=5, enabled=False)
        
        assert theme_manager.categories["test_category"].priority == 5
        assert theme_manager.categories["test_category"].enabled == False
    
    def test_update_category_not_found(self, theme_manager):
        """存在しないカテゴリの更新テスト"""
        with pytest.raises(ConfigError, match="カテゴリが見つかりません"):
            theme_manager.update_category("nonexistent", priority=5)
    
    def test_delete_category(self, theme_manager, sample_category):
        """カテゴリ削除テスト"""
        # カテゴリを追加
        theme_manager.categories["test_category"] = sample_category
        
        # カテゴリを削除
        theme_manager.delete_category("test_category")
        
        assert "test_category" not in theme_manager.categories
    
    def test_delete_category_not_found(self, theme_manager):
        """存在しないカテゴリの削除テスト"""
        with pytest.raises(ConfigError, match="カテゴリが見つかりません"):
            theme_manager.delete_category("nonexistent")
    
    def test_get_categories(self, theme_manager):
        """カテゴリ一覧取得テスト"""
        categories = theme_manager.get_categories()
        assert isinstance(categories, dict)
        assert len(categories) > 0
    
    def test_get_enabled_categories(self, theme_manager, sample_category):
        """有効なカテゴリ一覧取得テスト"""
        # 無効なカテゴリを追加
        disabled_category = Category(
            name="無効カテゴリ",
            priority=1,
            keywords=["無効"],
            seasonal_weight=1.0,
            enabled=False
        )
        theme_manager.categories["disabled"] = disabled_category
        
        enabled_categories = theme_manager.get_enabled_categories()
        
        # 無効なカテゴリが含まれていないことを確認
        assert "disabled" not in enabled_categories
    
    def test_add_seasonal_event(self, theme_manager, sample_seasonal_event):
        """季節イベント追加テスト"""
        theme_manager.add_seasonal_event("test_event", sample_seasonal_event)
        
        assert "test_event" in theme_manager.seasonal_events
        assert theme_manager.seasonal_events["test_event"].name == "テストイベント"
        assert theme_manager.seasonal_events["test_event"].weight == 1.5
    
    def test_get_current_seasonal_events(self, theme_manager):
        """現在の季節イベント取得テスト"""
        # 現在の日付に基づいてテスト
        current_events = theme_manager.get_current_seasonal_events()
        assert isinstance(current_events, list)
    
    def test_get_category_priority_with_seasonal_weight(self, theme_manager):
        """季節イベントを考慮したカテゴリ優先度取得テスト"""
        # entertainmentカテゴリの優先度を取得
        priority = theme_manager.get_category_priority("entertainment")
        assert isinstance(priority, float)
        assert priority > 0
    
    def test_get_category_priority_nonexistent(self, theme_manager):
        """存在しないカテゴリの優先度取得テスト"""
        priority = theme_manager.get_category_priority("nonexistent")
        assert priority == 1.0  # デフォルト値
    
    def test_get_recommended_categories(self, theme_manager):
        """推奨カテゴリ取得テスト"""
        recommended = theme_manager.get_recommended_categories(limit=3)
        assert isinstance(recommended, list)
        assert len(recommended) <= 3
    
    def test_add_post_style(self, theme_manager, sample_post_style):
        """投稿スタイル追加テスト"""
        theme_manager.add_post_style("test_style", sample_post_style)
        
        assert "test_style" in theme_manager.post_styles
        assert theme_manager.post_styles["test_style"].name == "テストスタイル"
        assert theme_manager.post_styles["test_style"].length_limit == 280
    
    def test_get_post_styles(self, theme_manager):
        """投稿スタイル一覧取得テスト"""
        styles = theme_manager.get_post_styles()
        assert isinstance(styles, dict)
        assert len(styles) > 0
    
    def test_get_enabled_post_styles(self, theme_manager):
        """有効な投稿スタイル一覧取得テスト"""
        enabled_styles = theme_manager.get_enabled_post_styles()
        assert isinstance(enabled_styles, dict)
        
        # すべてのスタイルが有効であることを確認
        for style in enabled_styles.values():
            assert style.enabled == True
    
    def test_validate_config_valid(self, theme_manager):
        """有効な設定の検証テスト"""
        errors = theme_manager.validate_config()
        assert isinstance(errors, list)
        # デフォルト設定は有効なので、エラーはないはず
        assert len(errors) == 0
    
    def test_validate_config_invalid_category(self, theme_manager):
        """無効なカテゴリ設定の検証テスト"""
        # 無効なカテゴリを追加
        invalid_category = Category(
            name="",  # 空の名前
            priority=10,  # 無効な優先度
            keywords=["テスト"],
            seasonal_weight=1.0
        )
        theme_manager.categories["invalid"] = invalid_category
        
        errors = theme_manager.validate_config()
        assert len(errors) > 0
        assert any("カテゴリ 'invalid' の名前が空です" in error for error in errors)
        assert any("カテゴリ 'invalid' の優先度が無効です" in error for error in errors)
    
    def test_validate_config_invalid_seasonal_event(self, theme_manager):
        """無効な季節イベント設定の検証テスト"""
        # 無効な季節イベントを追加
        invalid_event = SeasonalEvent(
            name="",  # 空の名前
            start_date="invalid-date",  # 無効な日付
            end_date="invalid-date",
            categories=["entertainment"],
            weight=1.0
        )
        theme_manager.seasonal_events["invalid"] = invalid_event
        
        errors = theme_manager.validate_config()
        assert len(errors) > 0
        assert any("季節イベント 'invalid' の名前が空です" in error for error in errors)
        assert any("季節イベント 'invalid' の日付形式が無効です" in error for error in errors)
    
    def test_validate_config_invalid_post_style(self, theme_manager):
        """無効な投稿スタイル設定の検証テスト"""
        # 無効な投稿スタイルを追加
        invalid_style = PostStyle(
            name="",  # 空の名前
            tone="テスト",
            format="テスト",
            length_limit=0,  # 無効な文字数制限
            language="日本語"
        )
        theme_manager.post_styles["invalid"] = invalid_style
        
        errors = theme_manager.validate_config()
        assert len(errors) > 0
        assert any("投稿スタイル 'invalid' の名前が空です" in error for error in errors)
        assert any("投稿スタイル 'invalid' の文字数制限が無効です" in error for error in errors)
    
    def test_load_config_file_error(self, temp_config_dir):
        """設定ファイル読み込みエラーテスト"""
        # 無効なJSONファイルを作成
        config_file = Path(temp_config_dir) / "theme_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # エラーが発生してもデフォルト設定が作成されることを確認
        manager = ThemeConfigManager(config_dir=temp_config_dir)
        assert len(manager.categories) > 0
        assert len(manager.seasonal_events) > 0
        assert len(manager.post_styles) > 0
    
    def test_category_dataclass(self):
        """Categoryデータクラステスト"""
        category = Category(
            name="テスト",
            priority=3,
            keywords=["キーワード1", "キーワード2"],
            seasonal_weight=1.2,
            enabled=True
        )
        
        assert category.name == "テスト"
        assert category.priority == 3
        assert category.keywords == ["キーワード1", "キーワード2"]
        assert category.seasonal_weight == 1.2
        assert category.enabled == True
    
    def test_seasonal_event_dataclass(self):
        """SeasonalEventデータクラステスト"""
        event = SeasonalEvent(
            name="テストイベント",
            start_date="01-01",
            end_date="01-07",
            categories=["cat1", "cat2"],
            weight=1.5,
            enabled=True
        )
        
        assert event.name == "テストイベント"
        assert event.start_date == "01-01"
        assert event.end_date == "01-07"
        assert event.categories == ["cat1", "cat2"]
        assert event.weight == 1.5
        assert event.enabled == True
    
    def test_post_style_dataclass(self):
        """PostStyleデータクラステスト"""
        style = PostStyle(
            name="テストスタイル",
            tone="親しみやすい",
            format="短文",
            length_limit=280,
            language="日本語",
            enabled=True
        )
        
        assert style.name == "テストスタイル"
        assert style.tone == "親しみやすい"
        assert style.format == "短文"
        assert style.length_limit == 280
        assert style.language == "日本語"
        assert style.enabled == True 