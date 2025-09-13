import os
import json
from redis import asyncio as aioredis
from redis import Redis
from typing import Dict, Any

# --- Connection Pooling for Performance ---
# Create the pool once when the module is loaded.
# Serverless functions may reuse this instance across invocations.
def get_redis_pool(sync: bool = False):
    """
    Returns a Redis connection pool (sync or async) configured from Vercel KV env vars.
    """
    try:
        url = os.environ.get("KV_URL")
        if not url:
            print("⚠️ KV_URL environment variable not set. KV features will not work.")
            return None
        # The `decode_responses=True` argument makes the client return strings instead of bytes.
        return Redis.from_url(url, decode_responses=True) if sync else aioredis.from_url(url, decode_responses=True)
    except Exception as e:
        print(f"❌ Could not create Redis pool: {e}")
        return None

async_pool = get_redis_pool()
sync_pool = get_redis_pool(sync=True)

async def set_progress(file_id: str, data: Dict[str, Any]):
    """Asynchronously sets progress data in KV."""
    if async_pool:
        async with aioredis.Redis(connection_pool=async_pool) as redis:
            await redis.set(file_id, json.dumps(data), ex=3600) # Expire after 1 hour

def set_progress_sync(file_id: str, data: Dict[str, Any]):
    """Synchronously sets progress data in KV. Useful for non-async callbacks."""
    if sync_pool:
        with Redis(connection_pool=sync_pool) as redis:
            redis.set(file_id, json.dumps(data), ex=3600)

async def get_progress_from_kv(file_id: str):
    """Asynchronously gets progress data from KV."""
    if async_pool:
        async with aioredis.Redis(connection_pool=async_pool) as redis:
            data = await redis.get(file_id)
            return json.loads(data) if data else None
    return None