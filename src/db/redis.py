# ioredis is our async io base client for redis
import redis.asyncio as aioredis
# it allows us to interact with redis from our python side by using different methods
from src.config import Config

# here we will set up our redis client object

# this is our config for redis which is an obj created from redis, and it will connect us to redis
token_blocklist = aioredis.from_url(Config.REDIS_URL)

JTI_EXPIRY = 3600


# we will store jti instead of tokens
# this functions add the token to our blocklist
async def add_jti_to_blocklist(jti: str) -> None:
    # set method stores value in the db
    # we send a key, a value and the expiry(the time we want that value to expire). note that this is how redis simply works
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

# this function checks if that token exists in our blocklist
async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti) # get method gets the key and returns it to us
    return jti is not None # this line returns True or False depending on whether jti is None or not
