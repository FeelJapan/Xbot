import pytest
import json
from pathlib import Path
from core.config.config_manager import ConfigManager, get_config_manager
from core.error_handling.error_handler import ConfigError

@pytest.fixture
def test_config_dir(tmp_path):
    """テスト用の設定ディレクトリを作成"""
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def config_manager(test_config_dir):
    """テスト用の設定マネージャーを作成"""
    return ConfigManager(str(test_config_dir))

def test_config_manager_initialization(config_manager, test_config_dir):
    """設定マネージャーの初期化テスト"""
    assert config_manager.config_dir == test_config_dir
    assert config_manager.config_file == test_config_dir / "config.json"
    assert config_manager.backup_dir == test_config_dir / "backups"
    assert config_manager._config == {}

def test_save_and_load_config(config_manager, test_config_dir):
    """設定の保存と読み込みのテスト"""
    test_config = {
        "api_keys": {
            "twitter": "test_key",
            "youtube": "test_key"
        },
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "logging": {
            "level": "INFO"
        }
    }
    
    # 設定を保存
    config_manager._config = test_config
    config_manager.save_config()
    
    # 設定ファイルが作成されているか確認
    assert config_manager.config_file.exists()
    
    # 設定を読み込み
    config_manager._config = {}
    config_manager.load_config()
    
    # 設定が正しく読み込まれているか確認
    assert config_manager._config == test_config

def test_get_set_delete(config_manager):
    """設定の取得、設定、削除のテスト"""
    # 設定を設定
    config_manager.set("test_key", "test_value")
    assert config_manager.get("test_key") == "test_value"
    
    # デフォルト値のテスト
    assert config_manager.get("non_existent_key", "default") == "default"
    
    # 設定を削除
    config_manager.delete("test_key")
    assert config_manager.get("test_key") is None

def test_get_all(config_manager):
    """全設定の取得テスト"""
    test_config = {
        "key1": "value1",
        "key2": "value2"
    }
    config_manager._config = test_config
    
    all_config = config_manager.get_all()
    assert all_config == test_config
    assert all_config is not test_config  # コピーが返されていることを確認

def test_backup_and_restore(config_manager):
    """バックアップと復元のテスト"""
    # 初期設定を保存
    initial_config = {"key": "value"}
    config_manager._config = initial_config
    config_manager.save_config()
    
    # 設定を変更
    new_config = {"key": "new_value"}
    config_manager._config = new_config
    config_manager.save_config()
    
    # バックアップの一覧を取得
    backups = config_manager.list_backups()
    assert len(backups) == 1
    
    # バックアップから復元
    config_manager.restore_backup(backups[0])
    assert config_manager._config == initial_config

def test_validate_config(config_manager):
    """設定の検証テスト"""
    # 必須項目が不足している場合
    assert not config_manager.validate_config()
    
    # 必須項目が揃っている場合
    config_manager._config = {
        "api_keys": {},
        "database": {},
        "logging": {}
    }
    assert config_manager.validate_config()

def test_singleton_pattern():
    """シングルトンパターンのテスト"""
    manager1 = get_config_manager()
    manager2 = get_config_manager()
    assert manager1 is manager2

def test_error_handling(config_manager):
    """エラーハンドリングのテスト"""
    # 存在しないバックアップファイルの復元
    with pytest.raises(ConfigError):
        config_manager.restore_backup("non_existent_backup.json")
    
    # 不正なJSONファイルの読み込み
    invalid_json_file = config_manager.config_file
    invalid_json_file.write_text("invalid json")
    
    with pytest.raises(ConfigError):
        config_manager.load_config() 