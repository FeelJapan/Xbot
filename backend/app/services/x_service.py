import tweepy
from backend.app.core.config import settings

class XService:
    """
    X（旧Twitter）の投稿を管理するサービスクラス
    
    Attributes:
        client (tweepy.Client): X APIクライアント
    """
    def __init__(self):
        """
        XServiceの初期化
        X APIクライアントを設定します
        """
        self.client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET
        )

    async def post_tweet(self, content: str) -> bool:
        """
        Xに投稿を送信する
        
        Args:
            content (str): 投稿内容
            
        Returns:
            bool: 投稿が成功した場合はTrue、失敗した場合はFalse
        """
        try:
            self.client.create_tweet(text=content)
            return True
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False

x_service = XService() 