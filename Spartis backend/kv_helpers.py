import os
import json
from redis import asyncio as aioredis
from redis import Redis
from typing import Dict, Any

def get_redis_client(sync: bool = False):
    """
    Returns a Redis client (sync or async) configured from Vercel KV environment variables.
    """
    try:
        url = os.environ.get("KV_URL")
        if not url:
            print("⚠️ KV_URL environment variable not set. KV features will not work.")
            return None
        
        if sync:
            return Redis.from_url(url)
        return aioredis.from_url(url)
    except Exception as e:
        print(f"❌ Could not create Redis client: {e}")
        return None

async def set_progress(file_id: str, data: Dict[str, Any]):
    """Asynchronously sets progress data in KV."""
    redis = get_redis_client()
    if redis:
        await redis.set(file_id, json.dumps(data), ex=3600) # Expire after 1 hour
        await redis.close()

def set_progress_sync(file_id: str, data: Dict[str, Any]):
    """Synchronously sets progress data in KV. Useful for non-async callbacks."""
    redis = get_redis_client(sync=True)
    if redis:
        redis.set(file_id, json.dumps(data), ex=3600)
        redis.close()

async def get_progress_from_kv(file_id: str):
    """Asynchronously gets progress data from KV."""
    redis = get_redis_client()
    if redis:
        data = await redis.get(file_id)
        await redis.close()
        return json.loads(data) if data else None
    return None