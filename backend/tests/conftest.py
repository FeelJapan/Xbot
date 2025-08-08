"""
pytest configuration and fixtures
"""
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPYTHONPATHに追加
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    return TestClient(app)

# テスト用のダミーAPIキーを設定
@pytest.fixture(autouse=True)
def setup_test_environment():
    """テスト環境の自動設定"""
    # テスト用のダミーAPIキーを環境変数に設定
    test_env_vars = {
        "X_API_KEY": "test_x_api_key",
        "X_API_SECRET": "test_x_api_secret", 
        "X_ACCESS_TOKEN": "test_x_access_token",
        "YOUTUBE_API_KEY": "test_youtube_api_key",
        "GEMINI_API_KEY": "test_gemini_api_key",
        "X_ACCESS_TOKEN_SECRET": "test_x_access_token_secret",
        "OPENAI_API_KEY": "test_openai_api_key",
        "GEMINI_API_KEY": "test_gemini_api_key",
        "GOOGLE_API_KEY": "test_google_api_key",
        "DATABASE_URL": "sqlite:///test.db",
        "TEST_MODE": "true"
    }
    
    # 既存の環境変数を保存
    original_env = {}
    for key in test_env_vars:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    # テスト用環境変数を設定
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    yield
    
    # テスト後に元の環境変数を復元
    for key in test_env_vars:
        if key in original_env:
            os.environ[key] = original_env[key]
        elif key in os.environ:
            del os.environ[key]

@pytest.fixture
def mock_api_responses():
    """APIレスポンスのモック"""
    with patch('backend.core.api_client.APIClient') as mock_client:
        # ダミーのAPIレスポンスを設定
        mock_client.return_value.post.return_value = {
            "status": "success",
            "data": {"result": "test_response"}
        }
        mock_client.return_value.get.return_value = {
            "status": "success", 
            "data": {"items": []}
        }
        yield mock_client

@pytest.fixture
def temp_cache_dir(tmp_path):
    """一時的なキャッシュディレクトリ"""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir

@pytest.fixture
def temp_config_dir(tmp_path):
    """一時的な設定ディレクトリ"""
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def sample_config_data():
    """サンプル設定データ"""
    return {
        "api_keys": {
            "openai": "test_openai_key",
            "gemini": "test_gemini_key",
            "google": "test_google_key"
        },
        "settings": {
            "theme": "dark",
            "language": "ja",
            "timezone": "Asia/Tokyo"
        },
        "features": {
            "image_generation": True,
            "video_generation": True,
            "trend_analysis": True
        }
    } 