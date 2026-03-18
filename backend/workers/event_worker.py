# app/workers/event_worker.py

import time
import json
import redis
from app.database.db import SessionLocal
from app.repositories.event_repo import EventRepo

r = redis.Redis()

while True:

    event = r.brpop("events_queue")

    if event:

        data = json.loads(event[1])

        db = SessionLocal()

        EventRepo(db).create(data)

        db.close()