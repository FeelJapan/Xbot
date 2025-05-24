import tweepy
from app.core.config import settings

class XService:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET
        )

    async def post_tweet(self, content: str) -> bool:
        try:
            self.client.create_tweet(text=content)
            return True
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False

x_service = XService() 