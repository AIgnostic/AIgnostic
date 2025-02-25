import redis.asyncio as redis

async def connect_to_redis(url: str):
    print("Connecting to Redis...")
    redis_client = redis.Redis.from_url(url)
    # Attempt to connect to Redis
    await redis_client.ping()
    return redis_client