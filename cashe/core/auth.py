from ..main import redis
import json

async def cache_user(user):
    try:
        user_data = {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
        }
        await redis.set(f"user:{user.id}", json.dumps(user_data), ex=3600)
    except Exception as e:
        print("Cache error:", e)


async def get_cached_user(user_id):
    user_data = await redis.get(f"user:{user_id}")
    if user_data:
        return json.loads(user_data)
    return None

async def blacklist_token(token: str):
    await redis.set(f"blacklist:{token}", "true", ex=86400)  

async def is_token_blacklisted(token: str):
    result = await redis.get(f"blacklist:{token}")
    return result == "true"
