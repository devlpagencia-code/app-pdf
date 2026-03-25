import os
import json

redis_url = os.getenv('REDIS_URL')

if redis_url:
    import redis
    redis_client = redis.Redis.from_url(redis_url)

    def push_event(event):
        redis_client.lpush('events_queue', json.dumps(event))

    def pop_event(timeout=1):
        result = redis_client.brpop('events_queue', timeout=timeout)
        if result:
            return json.loads(result[1])
        return None
else:
    queued_events = []

    def push_event(event):
        queued_events.append(event)

    def pop_event(timeout=1):
        if queued_events:
            return queued_events.pop(0)
        return None
