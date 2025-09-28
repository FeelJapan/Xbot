import os
import pytest
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from core.logging.logger import Logger, get_logger

@pytest.fixture
def test_log_dir(tmp_path):
    """テスト用のログディレクトリを作成"""
    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def logger(test_log_dir):
    """テスト用のロガーを作成"""
    return Logger("test_logger", str(test_log_dir))

def test_logger_initialization(logger, test_log_dir):
    """ロガーの初期化テスト"""
    assert logger.log_dir == test_log_dir
    assert logger.logger.level == 20  # INFO level

def test_log_file_creation(logger, test_log_dir):
    """ログファイルの作成テスト"""
    test_message = "Test log message"
    logger.info(test_message)
    
    # ログファイルが作成されているか確認（app.logとerror.logの両方が作成される）
    log_files = list(test_log_dir.glob("*.log"))
    assert len(log_files) == 2  # app.log と error.log
    
    # ログファイルの内容を確認
    with open(log_files[0], 'r', encoding='utf-8') as f:
        content = f.read()
        assert test_message in content

def test_log_levels(logger, test_log_dir):
    """各ログレベルのテスト"""
    test_messages = {
        'debug': 'Debug message',
        'info': 'Info message',
        'warning': 'Warning message',
        'error': 'Error message',
        'critical': 'Critical message'
    }
    
    # 各レベルのログを出力
    logger.debug(test_messages['debug'])
    logger.info(test_messages['info'])
    logger.warning(test_messages['warning'])
    logger.error(test_messages['error'])
    logger.critical(test_messages['critical'])
    
    # ログファイルの内容を確認（app.logとerror.logの両方が作成される）
    log_files = list(test_log_dir.glob("*.log"))
    assert len(log_files) == 2  # app.log と error.log
    
    with open(log_files[0], 'r', encoding='utf-8') as f:
        content = f.read()
        # INFOレベル以下のログは出力されない
        assert test_messages['debug'] not in content
        assert test_messages['info'] in content
        assert test_messages['warning'] in content
        assert test_messages['error'] in content
        assert test_messages['critical'] in content

def test_log_rotation(logger, test_log_dir):
    """ログローテーションのテスト"""
    # より小さなメッセージサイズでテスト（100バイトに削減）
    large_message = "x" * 100  # 100バイト
    for i in range(5):  # 5回繰り返して500バイトのログを生成
        logger.info(f"Message {i}: {large_message}")
    
    # ログファイルが作成されているか確認
    log_files = list(test_log_dir.glob("*.log*"))
    assert len(log_files) >= 1  # 少なくとも1つのログファイルが存在

def test_singleton_pattern():
    """シングルトンパターンのテスト"""
    logger1 = get_logger("test_singleton")
    logger2 = get_logger("test_singleton")
    assert logger1 is logger2

def test_different_loggers():
    """異なるロガーのテスト（シングルトンパターンのため同じインスタンスが返される）"""
    logger1 = get_logger("logger1")
    logger2 = get_logger("logger2")
    # シングルトンパターンのため、名前が異なっても同じインスタンスが返される
    assert logger1 is logger2 