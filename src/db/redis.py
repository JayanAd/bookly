import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600  # 1 hour in seconds

token_blocklist = redis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(jti, "", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    token = await token_blocklist.get(jti)
    return token is not None
