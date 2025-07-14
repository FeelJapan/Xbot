"""
Database access management module for Xbot
"""
import os
import logging
from typing import Any, Dict, Optional
from contextlib import contextmanager
from datetime import datetime
import asyncpg
from ..logging.logger import get_logger
from ..error_handling.error_handler import XbotError, handle_errors
from ..config.config_manager import get_config_manager

logger = get_logger("db_manager")

class DatabaseError(XbotError):
    """データベース関連のエラー"""
    pass

class DBManager:
    def __init__(self):
        self.config = get_config_manager()
        self.pool = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """コネクションプールの初期化"""
        try:
            db_config = self.config.get("database", {})
            self.pool = asyncpg.create_pool(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 5432),
                user=db_config.get("user", "postgres"),
                password=db_config.get("password", ""),
                database=db_config.get("database", "xbot"),
                min_size=db_config.get("min_connections", 1),
                max_size=db_config.get("max_connections", 10)
            )
        except Exception as e:
            logger.error(f"データベース接続の初期化に失敗: {str(e)}")
            raise DatabaseError(f"データベース接続の初期化に失敗: {str(e)}")

    @contextmanager
    async def transaction(self):
        """トランザクションコンテキストマネージャー"""
        async with self.pool.acquire() as conn:
            async with conn.transaction() as tr:
                try:
                    yield tr
                except Exception as e:
                    logger.error(f"トランザクションでエラーが発生: {str(e)}")
                    raise

    @handle_errors(error_types=DatabaseError, retry_count=3)
    async def execute(self, query: str, *args, **kwargs) -> Any:
        """クエリの実行"""
        async with self.pool.acquire() as conn:
            start_time = datetime.now()
            try:
                result = await conn.execute(query, *args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.debug(f"クエリ実行時間: {execution_time}秒")
                return result
            except Exception as e:
                logger.error(f"クエリ実行エラー: {str(e)}")
                raise DatabaseError(f"クエリ実行エラー: {str(e)}")

    @handle_errors(error_types=DatabaseError, retry_count=3)
    async def fetch(self, query: str, *args, **kwargs) -> list[Dict[str, Any]]:
        """クエリの実行と結果の取得"""
        async with self.pool.acquire() as conn:
            start_time = datetime.now()
            try:
                result = await conn.fetch(query, *args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.debug(f"クエリ実行時間: {execution_time}秒")
                return [dict(row) for row in result]
            except Exception as e:
                logger.error(f"クエリ実行エラー: {str(e)}")
                raise DatabaseError(f"クエリ実行エラー: {str(e)}")

    @handle_errors(error_types=DatabaseError, retry_count=3)
    async def fetchrow(self, query: str, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """単一行の取得"""
        async with self.pool.acquire() as conn:
            start_time = datetime.now()
            try:
                result = await conn.fetchrow(query, *args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.debug(f"クエリ実行時間: {execution_time}秒")
                return dict(result) if result else None
            except Exception as e:
                logger.error(f"クエリ実行エラー: {str(e)}")
                raise DatabaseError(f"クエリ実行エラー: {str(e)}")

    async def close(self) -> None:
        """コネクションプールのクローズ"""
        if self.pool:
            await self.pool.close()

# シングルトンインスタンス
_db_manager_instance = None

def get_db_manager() -> DBManager:
    """データベースマネージャーのインスタンスを取得"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DBManager()
    return _db_manager_instance 