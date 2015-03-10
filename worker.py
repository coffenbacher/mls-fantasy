import redis
import os
redis_url = os.getenv('REDISCLOUD_URL')
conn = redis.from_url(redis_url)