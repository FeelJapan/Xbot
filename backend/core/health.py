from typing import Dict, List
import logging
from datetime import datetime
import asyncio
from .api_client import APIClient
from .error_handling import ServiceError

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self, service_name: str, dependencies: List[Dict[str, str]] = None):
        self.service_name = service_name
        self.dependencies = dependencies or []
        self.status = "healthy"
        self.last_check = None
        self.dependency_status = {}

    async def check_dependency(self, name: str, url: str) -> Dict:
        """
        依存サービスのヘルスチェックを実行
        """
        try:
            client = APIClient(url)
            response = await client.get("/health")
            status = "healthy" if response.get("status") == "healthy" else "unhealthy"
            return {
                "name": name,
                "status": status,
                "last_check": datetime.utcnow().isoformat(),
                "details": response
            }
        except Exception as e:
            logger.error(f"Health check failed for {name}: {str(e)}")
            return {
                "name": name,
                "status": "unhealthy",
                "last_check": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        finally:
            await client.close()

    async def check_all(self) -> Dict:
        """
        すべての依存関係のヘルスチェックを実行
        """
        self.last_check = datetime.utcnow()
        tasks = []
        
        for dep in self.dependencies:
            tasks.append(self.check_dependency(dep["name"], dep["url"]))
        
        results = await asyncio.gather(*tasks)
        
        self.dependency_status = {result["name"]: result for result in results}
        
        # すべての依存関係が健全な場合のみ、このサービスも健全と判断
        self.status = "healthy" if all(
            result["status"] == "healthy" for result in results
        ) else "unhealthy"
        
        return self.get_status()

    def get_status(self) -> Dict:
        """
        現在のヘルスステータスを取得
        """
        return {
            "service": self.service_name,
            "status": self.status,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "dependencies": self.dependency_status
        } 