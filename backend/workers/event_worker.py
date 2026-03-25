# backend/workers/event_worker.py

import time
import json
from core.queue import pop_event

# Worker loop: process any queued events (in-memory fallback) and log them.
while True:
    event = pop_event()
    if event:
        print("Processed event:", json.dumps(event, ensure_ascii=False))
    time.sleep(1)