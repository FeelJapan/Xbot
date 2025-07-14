"""
テーマ設定管理サービス
投稿テーマの設定を管理する機能
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from backend.core.logging.logger import get_logger

logger = get_logger("theme_config_manager")

class ConfigError(Exception):
    """設定関連のエラー"""
    pass

@dataclass
class Category:
    """カテゴリ情報"""
    name: str
    priority: int
    keywords: List[str]
    seasonal_weight: float
    enabled: bool = True

@dataclass
class SeasonalEvent:
    """季節イベント情報"""
    name: str
    start_date: str
    end_date: str
    categories: List[str]
    weight: float
    enabled: bool = True

@dataclass
class PostStyle:
    """投稿スタイル情報"""
    name: str
    tone: str
    format: str
    length_limit: int
    language: str
    enabled: bool = True

class ThemeConfigManager:
    """テーマ設定管理クラス"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.theme_config_file = self.config_dir / "theme_config.json"
        self.categories: Dict[str, Category] = {}
        self.seasonal_events: Dict[str, SeasonalEvent] = {}
        self.post_styles: Dict[str, PostStyle] = {}
        self.load_config()
        
    def load_config(self) -> None:
        """設定を読み込み"""
        try:
            if self.theme_config_file.exists():
                with open(self.theme_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # カテゴリの読み込み
                self.categories = {
                    name: Category(**cat_data)
                    for name, cat_data in data.get("categories", {}).items()
                }
                
                # 季節イベントの読み込み
                self.seasonal_events = {
                    name: SeasonalEvent(**event_data)
                    for name, event_data in data.get("seasonal_events", {}).items()
                }
                
                # 投稿スタイルの読み込み
                self.post_styles = {
                    name: PostStyle(**style_data)
                    for name, style_data in data.get("post_styles", {}).items()
                }
                
                logger.info("テーマ設定を読み込みました")
            else:
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"テーマ設定の読み込みに失敗しました: {str(e)}")
            self._create_default_config()
    
    def save_config(self) -> None:
        """設定を保存"""
        try:
            data = {
                "categories": {
                    name: asdict(category)
                    for name, category in self.categories.items()
                },
                "seasonal_events": {
                    name: asdict(event)
                    for name, event in self.seasonal_events.items()
                },
                "post_styles": {
                    name: asdict(style)
                    for name, style in self.post_styles.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.theme_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info("テーマ設定を保存しました")
            
        except Exception as e:
            logger.error(f"テーマ設定の保存に失敗しました: {str(e)}")
            raise ConfigError(f"テーマ設定の保存に失敗しました: {str(e)}")
    
    def _create_default_config(self) -> None:
        """デフォルト設定を作成"""
        # デフォルトカテゴリ
        self.categories = {
            "entertainment": Category(
                name="エンターテイメント",
                priority=3,
                keywords=["面白い", "笑える", "感動", "驚き"],
                seasonal_weight=1.0
            ),
            "technology": Category(
                name="テクノロジー",
                priority=2,
                keywords=["AI", "技術", "革新", "未来"],
                seasonal_weight=0.8
            ),
            "lifestyle": Category(
                name="ライフスタイル",
                priority=2,
                keywords=["日常", "生活", "便利", "工夫"],
                seasonal_weight=1.2
            ),
            "culture": Category(
                name="文化",
                priority=1,
                keywords=["文化", "伝統", "歴史", "芸術"],
                seasonal_weight=1.5
            )
        }
        
        # デフォルト季節イベント
        self.seasonal_events = {
            "christmas": SeasonalEvent(
                name="クリスマス",
                start_date="12-01",
                end_date="12-25",
                categories=["entertainment", "lifestyle"],
                weight=1.5
            ),
            "new_year": SeasonalEvent(
                name="お正月",
                start_date="01-01",
                end_date="01-07",
                categories=["culture", "lifestyle"],
                weight=1.3
            ),
            "valentine": SeasonalEvent(
                name="バレンタイン",
                start_date="02-14",
                end_date="02-14",
                categories=["entertainment", "lifestyle"],
                weight=1.4
            )
        }
        
        # デフォルト投稿スタイル
        self.post_styles = {
            "casual": PostStyle(
                name="カジュアル",
                tone="親しみやすい",
                format="短文",
                length_limit=280,
                language="日本語"
            ),
            "humorous": PostStyle(
                name="ユーモア",
                tone="面白い",
                format="短文",
                length_limit=280,
                language="日本語"
            ),
            "informative": PostStyle(
                name="情報提供",
                tone="丁寧",
                format="中程度",
                length_limit=500,
                language="日本語"
            )
        }
        
        self.save_config()
        logger.info("デフォルトテーマ設定を作成しました")
    
    def add_category(self, name: str, category: Category) -> None:
        """カテゴリを追加"""
        try:
            self.categories[name] = category
            self.save_config()
            logger.info(f"カテゴリを追加しました: {name}")
            
        except Exception as e:
            logger.error(f"カテゴリの追加に失敗しました: {str(e)}")
            raise ConfigError(f"カテゴリの追加に失敗しました: {str(e)}")
    
    def update_category(self, name: str, **kwargs) -> None:
        """カテゴリを更新"""
        try:
            if name not in self.categories:
                raise ConfigError(f"カテゴリが見つかりません: {name}")
                
            category = self.categories[name]
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)
                    
            self.save_config()
            logger.info(f"カテゴリを更新しました: {name}")
            
        except Exception as e:
            logger.error(f"カテゴリの更新に失敗しました: {str(e)}")
            raise ConfigError(f"カテゴリの更新に失敗しました: {str(e)}")
    
    def delete_category(self, name: str) -> None:
        """カテゴリを削除"""
        try:
            if name not in self.categories:
                raise ConfigError(f"カテゴリが見つかりません: {name}")
                
            del self.categories[name]
            self.save_config()
            logger.info(f"カテゴリを削除しました: {name}")
            
        except Exception as e:
            logger.error(f"カテゴリの削除に失敗しました: {str(e)}")
            raise ConfigError(f"カテゴリの削除に失敗しました: {str(e)}")
    
    def get_categories(self) -> Dict[str, Category]:
        """カテゴリ一覧を取得"""
        return self.categories
    
    def get_enabled_categories(self) -> Dict[str, Category]:
        """有効なカテゴリ一覧を取得"""
        return {
            name: category
            for name, category in self.categories.items()
            if category.enabled
        }
    
    def add_seasonal_event(self, name: str, event: SeasonalEvent) -> None:
        """季節イベントを追加"""
        try:
            self.seasonal_events[name] = event
            self.save_config()
            logger.info(f"季節イベントを追加しました: {name}")
            
        except Exception as e:
            logger.error(f"季節イベントの追加に失敗しました: {str(e)}")
            raise ConfigError(f"季節イベントの追加に失敗しました: {str(e)}")
    
    def get_current_seasonal_events(self) -> List[SeasonalEvent]:
        """現在の季節イベントを取得"""
        current_date = datetime.now()
        current_events = []
        
        for event in self.seasonal_events.values():
            if not event.enabled:
                continue
                
            start_date = datetime.strptime(f"{current_date.year}-{event.start_date}", "%Y-%m-%d")
            end_date = datetime.strptime(f"{current_date.year}-{event.end_date}", "%Y-%m-%d")
            
            # 年をまたぐイベントの処理
            if start_date > end_date:
                if current_date.month >= start_date.month:
                    start_date = start_date.replace(year=current_date.year)
                    end_date = end_date.replace(year=current_date.year + 1)
                else:
                    start_date = start_date.replace(year=current_date.year - 1)
                    end_date = end_date.replace(year=current_date.year)
            
            if start_date <= current_date <= end_date:
                current_events.append(event)
                
        return current_events
    
    def get_category_priority(self, category_name: str) -> float:
        """カテゴリの優先度を取得（季節イベントを考慮）"""
        if category_name not in self.categories:
            return 1.0
            
        category = self.categories[category_name]
        base_priority = category.priority
        
        # 季節イベントの重みを適用
        seasonal_weight = category.seasonal_weight
        current_events = self.get_current_seasonal_events()
        
        for event in current_events:
            if category_name in event.categories:
                seasonal_weight *= event.weight
                
        return base_priority * seasonal_weight
    
    def get_recommended_categories(self, limit: int = 5) -> List[str]:
        """推奨カテゴリを取得"""
        category_scores = []
        
        for name, category in self.get_enabled_categories().items():
            priority = self.get_category_priority(name)
            category_scores.append((name, priority))
            
        # 優先度順にソート
        category_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, _ in category_scores[:limit]]
    
    def add_post_style(self, name: str, style: PostStyle) -> None:
        """投稿スタイルを追加"""
        try:
            self.post_styles[name] = style
            self.save_config()
            logger.info(f"投稿スタイルを追加しました: {name}")
            
        except Exception as e:
            logger.error(f"投稿スタイルの追加に失敗しました: {str(e)}")
            raise ConfigError(f"投稿スタイルの追加に失敗しました: {str(e)}")
    
    def get_post_styles(self) -> Dict[str, PostStyle]:
        """投稿スタイル一覧を取得"""
        return self.post_styles
    
    def get_enabled_post_styles(self) -> Dict[str, PostStyle]:
        """有効な投稿スタイル一覧を取得"""
        return {
            name: style
            for name, style in self.post_styles.items()
            if style.enabled
        }
    
    def validate_config(self) -> List[str]:
        """設定の検証"""
        errors = []
        
        # カテゴリの検証
        for name, category in self.categories.items():
            if not category.name:
                errors.append(f"カテゴリ '{name}' の名前が空です")
            if category.priority < 1 or category.priority > 5:
                errors.append(f"カテゴリ '{name}' の優先度が無効です: {category.priority}")
                
        # 季節イベントの検証
        for name, event in self.seasonal_events.items():
            if not event.name:
                errors.append(f"季節イベント '{name}' の名前が空です")
            try:
                datetime.strptime(f"2024-{event.start_date}", "%Y-%m-%d")
                datetime.strptime(f"2024-{event.end_date}", "%Y-%m-%d")
            except ValueError:
                errors.append(f"季節イベント '{name}' の日付形式が無効です")
                
        # 投稿スタイルの検証
        for name, style in self.post_styles.items():
            if not style.name:
                errors.append(f"投稿スタイル '{name}' の名前が空です")
            if style.length_limit < 1:
                errors.append(f"投稿スタイル '{name}' の文字数制限が無効です: {style.length_limit}")
                
        return errors 