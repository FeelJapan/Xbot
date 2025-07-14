import pytest
import asyncio
from datetime import datetime
from backend.core.database.db_manager import DBManager, get_db_manager

@pytest.fixture
async def db_manager():
    """テスト用のデータベースマネージャーインスタンスを作成"""
    db_manager = get_db_manager()
    yield db_manager
    await db_manager.close()

@pytest.fixture
async def test_table(db_manager):
    """テスト用のテーブルを作成"""
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            value INTEGER,
            created_at TIMESTAMP
        )
    """)
    yield
    await db_manager.execute("DROP TABLE IF EXISTS test_table")

async def test_db_manager_initialization(db_manager):
    """データベースマネージャーの初期化テスト"""
    assert db_manager is not None
    assert hasattr(db_manager, 'pool')
    assert hasattr(db_manager, 'config')

async def test_db_manager_singleton():
    """シングルトンパターンのテスト"""
    manager1 = get_db_manager()
    manager2 = get_db_manager()
    assert manager1 is manager2

async def test_execute_query(db_manager):
    """クエリ実行のテスト"""
    result = await db_manager.execute("SELECT 1 as test_value")
    assert result is not None

async def test_fetch_query(db_manager):
    """クエリ結果取得のテスト"""
    result = await db_manager.fetch("SELECT 1 as test_value, 'test' as test_string")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['test_value'] == 1
    assert result[0]['test_string'] == 'test'

async def test_fetchrow_query(db_manager):
    """単一行取得のテスト"""
    result = await db_manager.fetchrow("SELECT 1 as test_value, 'test' as test_string")
    assert isinstance(result, dict)
    assert result['test_value'] == 1
    assert result['test_string'] == 'test'

async def test_fetchrow_empty_result(db_manager):
    """空の結果のテスト"""
    result = await db_manager.fetchrow("SELECT 1 WHERE FALSE")
    assert result is None

async def test_table_operations(db_manager, test_table):
    """テーブル操作のテスト"""
    # データの挿入
    await db_manager.execute("""
        INSERT INTO test_table (name, value, created_at) 
        VALUES ($1, $2, $3)
    """, "test_name", 100, datetime.now())
    
    # データの取得
    result = await db_manager.fetch("SELECT * FROM test_table WHERE name = $1", "test_name")
    assert len(result) == 1
    assert result[0]['name'] == "test_name"
    assert result[0]['value'] == 100
    
    # データの更新
    await db_manager.execute("""
        UPDATE test_table SET value = $1 WHERE name = $2
    """, 200, "test_name")
    
    # 更新結果の確認
    result = await db_manager.fetchrow("SELECT value FROM test_table WHERE name = $1", "test_name")
    assert result['value'] == 200
    
    # データの削除
    await db_manager.execute("DELETE FROM test_table WHERE name = $1", "test_name")
    
    # 削除結果の確認
    result = await db_manager.fetchrow("SELECT * FROM test_table WHERE name = $1", "test_name")
    assert result is None 