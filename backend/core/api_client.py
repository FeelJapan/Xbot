from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        共通のAPIリクエストメソッド
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", endpoint, data=data)

    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        return await self.request("DELETE", endpoint)

    async def close(self):
        await self.client.aclose() 