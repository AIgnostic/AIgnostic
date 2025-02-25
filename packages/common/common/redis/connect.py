import asyncio
import redis.asyncio as redis


async def connect_to_redis(url: str, retries: int = 20):
    for i in range(retries):  # Retry up to 10 times
        print(f"Connecting to Redis at {url}")
        try:
            redis_client = redis.Redis.from_url(url)
            # Attempt to connect to Redis
            await redis_client.ping()
            return redis_client
        except redis.ConnectionError as e:
            print(f"Connection failed due to {e}. Retrying {i+1}/{retries}...")
            await asyncio.sleep(3)
    raise Exception(f"Could not connect to Redis after {retries} attempts.")
