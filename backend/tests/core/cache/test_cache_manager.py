import pytest
import time
import json
from pathlib import Path
from core.cache.cache_manager import CacheManager, get_cache_manager

@pytest.fixture
def test_cache_dir(tmp_path):
    """テスト用のキャッシュディレクトリを作成"""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir

@pytest.fixture
def cache_manager(test_cache_dir):
    """テスト用のキャッシュマネージャーを作成"""
    return CacheManager(str(test_cache_dir))

def test_cache_manager_initialization(cache_manager, test_cache_dir):
    """キャッシュマネージャーの初期化テスト"""
    assert cache_manager.cache_dir == test_cache_dir
    assert cache_manager.memory_cache == {}
    assert cache_manager._cleanup_interval == 3600

def test_set_and_get(cache_manager):
    """キャッシュの設定と取得のテスト"""
    # キャッシュの設定と取得のテスト
    cache_manager.set("test_key", "test_value", ttl=3600)
    assert cache_manager.get("test_key") == "test_value"
    
    # 別のキーでのテスト
    cache_manager.set("file_key", "file_value", ttl=3600)
    assert cache_manager.get("file_key") == "file_value"
    
    # 両方のキャッシュのテスト
    cache_manager.set("both_key", "both_value", ttl=3600)
    assert cache_manager.get("both_key") == "both_value"

def test_ttl_expiration(cache_manager):
    """TTLによる期限切れのテスト"""
    # 短いTTLでキャッシュを設定
    cache_manager.set("expire_key", "expire_value", ttl=1)
    assert cache_manager.get("expire_key") == "expire_value"
    
    # TTLが切れるまで待機
    time.sleep(1.1)
    assert cache_manager.get("expire_key") is None

def test_delete(cache_manager):
    """キャッシュの削除テスト"""
    # メモリキャッシュとファイルキャッシュの両方を設定
    cache_manager.set("delete_key", "delete_value", ttl=3600)
    
    # キャッシュが存在することを確認
    assert cache_manager.get("delete_key") == "delete_value"
    
    # キャッシュを削除
    cache_manager.delete("delete_key")
    
    # キャッシュが削除されたことを確認
    assert cache_manager.get("delete_key") is None
    assert not cache_manager._get_cache_path("delete_key").exists()

def test_clear(cache_manager):
    """キャッシュの全削除テスト"""
    # 複数のキャッシュを設定
    cache_manager.set("key1", "value1", ttl=3600)
    cache_manager.set("key2", "value2", ttl=3600)
    
    # キャッシュが存在することを確認
    assert cache_manager.get("key1") == "value1"
    assert cache_manager.get("key2") == "value2"
    
    # キャッシュを全削除
    cache_manager.clear()
    
    # キャッシュが削除されたことを確認
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") is None
    assert len(list(cache_manager.cache_dir.glob("*.json"))) == 0

def test_cleanup_expired(cache_manager):
    """期限切れキャッシュのクリーンアップテスト"""
    # 期限切れのキャッシュを設定
    cache_manager.set("expired_key", "expired_value", ttl=1)
    time.sleep(1.1)
    
    # クリーンアップを実行
    cache_manager._cleanup_interval = 0  # クリーンアップを強制的に実行
    cache_manager._cleanup_expired()
    
    # キャッシュが削除されたことを確認
    assert cache_manager.get("expired_key") is None
    assert not cache_manager._get_cache_path("expired_key").exists()

def test_get_stats(cache_manager):
    """統計情報の取得テスト"""
    # キャッシュを設定
    cache_manager.set("key1", "value1", ttl=3600)
    cache_manager.set("key2", "value2", ttl=3600)
    
    # 統計情報を取得
    stats = cache_manager.get_stats()
    
    # 統計情報を検証
    assert stats["memory_cache_size"] == 2
    assert stats["file_cache_size"] == 2
    assert "memory_cache_keys" in stats
    assert "file_cache_keys" in stats

def test_singleton_pattern():
    """シングルトンパターンのテスト"""
    manager1 = get_cache_manager()
    manager2 = get_cache_manager()
    assert manager1 is manager2

def test_error_handling(cache_manager):
    """エラーハンドリングのテスト"""
    # 不正なJSONファイルの作成
    invalid_cache_file = cache_manager._get_cache_path("invalid_key")
    invalid_cache_file.write_text("invalid json")
    
    # 不正なJSONファイルの読み込み
    assert cache_manager.get("invalid_key") is None
    
    # 存在しないキーの取得
    assert cache_manager.get("non_existent_key") is None
    assert cache_manager.get("non_existent_key", default="default_value") == "default_value" 