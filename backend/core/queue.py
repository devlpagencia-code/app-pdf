import os
import json

redis_url = os.getenv('REDIS_URL')
if redis_url:
    import redis
    redis_client = redis.Redis.from_url(redis_url)
    def push_event(event):
        redis_client.lpush('events_queue', json.dumps(event))
else:
    queued_events = []
    def push_event(event):
        queued_events.append(event)
