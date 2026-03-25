from sqlalchemy import Column, Integer, String, BigInteger, JSON
from database.db import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    document_id = Column(String, nullable=True)
    timestamp = Column(BigInteger, nullable=False)
    page = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)
