import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from ..logging.logger import get_logger
import threading

logger = get_logger("cache_manager")

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # クリーンアップ関連の初期化
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # 1時間
        
        # キャッシュクリーンアップスレッドの開始
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def _get_cache_path(self, key: str) -> Path:
        """キャッシュファイルのパスを取得"""
        return self.cache_dir / f"{key}.json"
    
    def _is_expired(self, expiry: float) -> bool:
        """キャッシュが期限切れかどうかを判定"""
        return time.time() > expiry
    
    def _cleanup_expired(self) -> None:
        """期限切れのキャッシュを削除"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # メモリキャッシュのクリーンアップ
        expired_keys = [
            key for key, data in self.memory_cache.items()
            if not self._is_valid(data)
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # ファイルキャッシュのクリーンアップ
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not self._is_valid(data):
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"キャッシュファイルのクリーンアップに失敗: {str(e)}")
        
        self._last_cleanup = current_time
    
    def get(self, key: str, default: Any = None) -> Any:
        """キャッシュから値を取得"""
        # メモリキャッシュの確認
        with self.lock:
            if key in self.memory_cache:
                cache_data = self.memory_cache[key]
                if self._is_valid(cache_data):
                    return cache_data["value"]
                else:
                    del self.memory_cache[key]
        
        # ファイルキャッシュの確認
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if self._is_valid(cache_data):
                    # メモリキャッシュに追加
                    with self.lock:
                        self.memory_cache[key] = cache_data
                    return cache_data["value"]
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"キャッシュファイルの読み込みに失敗しました: {str(e)}")
                cache_file.unlink()
        
        return default
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """キャッシュに値を設定"""
        cache_data = {
            "value": value,
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        # メモリキャッシュに保存
        with self.lock:
            self.memory_cache[key] = cache_data
        
        # ファイルキャッシュに保存
        cache_file = self._get_cache_path(key)
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"キャッシュファイルの保存に失敗しました: {str(e)}")
    
    def delete(self, key: str) -> None:
        """キャッシュから値を削除"""
        # メモリキャッシュから削除
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
        
        # ファイルキャッシュから削除
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"キャッシュファイルの削除に失敗しました: {str(e)}")
    
    def clear(self) -> None:
        """キャッシュをクリア"""
        # メモリキャッシュをクリア
        with self.lock:
            self.memory_cache.clear()
        
        # ファイルキャッシュをクリア
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception as e:
            logger.error(f"キャッシュファイルのクリアに失敗しました: {str(e)}")
    
    def _is_valid(self, cache_data: Dict[str, Any]) -> bool:
        """キャッシュデータが有効かどうかを確認"""
        if "expires_at" not in cache_data:
            return False
        
        try:
            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            return datetime.now() < expires_at
        except Exception:
            return False
    
    def _cleanup_loop(self) -> None:
        """定期的なキャッシュクリーンアップ"""
        while True:
            try:
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"キャッシュクリーンアップに失敗しました: {str(e)}")
            time.sleep(3600)  # 1時間ごとに実行
    
    def _cleanup_expired_cache(self) -> None:
        """期限切れのキャッシュをクリーンアップ"""
        # メモリキャッシュのクリーンアップ
        with self.lock:
            expired_keys = [
                key for key, data in self.memory_cache.items()
                if not self._is_valid(data)
            ]
            for key in expired_keys:
                del self.memory_cache[key]
        
        # ファイルキャッシュのクリーンアップ
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                    if not self._is_valid(cache_data):
                        cache_file.unlink()
                except Exception:
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"ファイルキャッシュのクリーンアップに失敗しました: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュの統計情報を取得"""
        stats = {
            "memory_cache_size": len(self.memory_cache),
            "file_cache_size": len(list(self.cache_dir.glob("*.json"))),
            "memory_cache_keys": list(self.memory_cache.keys()),
            "file_cache_keys": [f.stem for f in self.cache_dir.glob("*.json")]
        }
        return stats

# シングルトンインスタンス
_cache_manager_instance = None

def get_cache_manager() -> CacheManager:
    """キャッシュマネージャーのインスタンスを取得"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance 