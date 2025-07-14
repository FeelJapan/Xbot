from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta
import logging
from .error_handling import AuthenticationError

logger = logging.getLogger(__name__)

class JWTAuth:
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes

    def create_service_token(self, service_name: str, permissions: Optional[list[str]] = None) -> str:
        """
        サービス間通信用のJWTトークンを生成
        """
        try:
            payload = {
                "sub": service_name,
                "type": "service",
                "permissions": permissions or [],
                "exp": datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
            }
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise AuthenticationError("Failed to create service token")

    def verify_token(self, token: str) -> Dict:
        """
        JWTトークンを検証
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def get_service_headers(self, service_name: str, permissions: Optional[list[str]] = None) -> Dict[str, str]:
        """
        サービス間通信用のヘッダーを生成
        """
        token = self.create_service_token(service_name, permissions)
        return {
            "Authorization": f"Bearer {token}",
            "X-Service-Name": service_name
        } 