"""
Database migration management module for Xbot
"""
import os
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..logging.logger import get_logger
from ..error_handling.error_handler import XbotError, handle_errors
from .db_manager import get_db_manager, DatabaseError

logger = get_logger("migration_manager")

class MigrationError(DatabaseError):
    """マイグレーション関連のエラー"""
    pass

class MigrationManager:
    def __init__(self, migrations_dir: str = "migrations"):
        self.db = get_db_manager()
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_migration_table()

    async def _ensure_migration_table(self) -> None:
        """マイグレーション履歴テーブルの作成"""
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.db.execute(query)

    async def get_applied_migrations(self) -> List[str]:
        """適用済みのマイグレーション一覧を取得"""
        query = "SELECT name FROM migrations ORDER BY id"
        results = await self.db.fetch(query)
        return [row["name"] for row in results]

    async def get_pending_migrations(self) -> List[str]:
        """未適用のマイグレーション一覧を取得"""
        applied = set(await self.get_applied_migrations())
        all_migrations = [f.name for f in self.migrations_dir.glob("*.sql")]
        return [m for m in all_migrations if m not in applied]

    @handle_errors(error_types=MigrationError)
    async def apply_migration(self, migration_file: str) -> None:
        """マイグレーションの適用"""
        migration_path = self.migrations_dir / migration_file
        if not migration_path.exists():
            raise MigrationError(f"マイグレーションファイルが見つかりません: {migration_file}")

        try:
            # マイグレーションSQLの読み込み
            with open(migration_path, "r", encoding="utf-8") as f:
                sql = f.read()

            # トランザクション内でマイグレーションを実行
            async with self.db.transaction() as tr:
                await tr.execute(sql)
                await tr.execute(
                    "INSERT INTO migrations (name) VALUES ($1)",
                    migration_file
                )

            logger.info(f"マイグレーションを適用しました: {migration_file}")
        except Exception as e:
            logger.error(f"マイグレーションの適用に失敗: {str(e)}")
            raise MigrationError(f"マイグレーションの適用に失敗: {str(e)}")

    @handle_errors(error_types=MigrationError)
    async def rollback_migration(self, migration_file: str) -> None:
        """マイグレーションのロールバック"""
        rollback_file = migration_file.replace(".sql", "_rollback.sql")
        rollback_path = self.migrations_dir / rollback_file

        if not rollback_path.exists():
            raise MigrationError(f"ロールバックファイルが見つかりません: {rollback_file}")

        try:
            # ロールバックSQLの読み込み
            with open(rollback_path, "r", encoding="utf-8") as f:
                sql = f.read()

            # トランザクション内でロールバックを実行
            async with self.db.transaction() as tr:
                await tr.execute(sql)
                await tr.execute(
                    "DELETE FROM migrations WHERE name = $1",
                    migration_file
                )

            logger.info(f"マイグレーションをロールバックしました: {migration_file}")
        except Exception as e:
            logger.error(f"マイグレーションのロールバックに失敗: {str(e)}")
            raise MigrationError(f"マイグレーションのロールバックに失敗: {str(e)}")

    async def migrate(self) -> None:
        """未適用のマイグレーションを全て適用"""
        pending = await self.get_pending_migrations()
        for migration in pending:
            await self.apply_migration(migration)

    async def create_migration(self, name: str) -> None:
        """新しいマイグレーションファイルを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_file = f"{timestamp}_{name}.sql"
        rollback_file = f"{timestamp}_{name}_rollback.sql"

        # マイグレーションファイルの作成
        migration_path = self.migrations_dir / migration_file
        with open(migration_path, "w", encoding="utf-8") as f:
            f.write("-- マイグレーションSQLをここに記述\n")

        # ロールバックファイルの作成
        rollback_path = self.migrations_dir / rollback_file
        with open(rollback_path, "w", encoding="utf-8") as f:
            f.write("-- ロールバックSQLをここに記述\n")

        logger.info(f"マイグレーションファイルを作成しました: {migration_file}")

# シングルトンインスタンス
_migration_manager_instance = None

def get_migration_manager() -> MigrationManager:
    """マイグレーションマネージャーのインスタンスを取得"""
    global _migration_manager_instance
    if _migration_manager_instance is None:
        _migration_manager_instance = MigrationManager()
    return _migration_manager_instance 