# app/models/event.py

from sqlalchemy import Column, Integer, String, BigInteger

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    event = Column(String)
    page = Column(Integer)
    timestamp = Column(BigInteger)