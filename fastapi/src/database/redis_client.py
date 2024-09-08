from redis.asyncio import Redis
from typing import Optional

class RedisClient:
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis: Optional[Redis] = None

    async def init(self):
        self._redis = await Redis.from_url(self._redis_url, decode_responses=True)

    async def close(self):
        if self._redis:
            await self._redis.close()

    @property
    def redis(self) -> Redis:
        if not self._redis:
            raise RuntimeError("Redis client not initialized.")
        return self._redis

redis_client = RedisClient(redis_url="redis://redis")
