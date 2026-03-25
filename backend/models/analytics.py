from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from database.db import Base


class PageAnalytics(Base):
    __tablename__ = 'page_analytics'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    page = Column(Integer, nullable=True, index=True)
    total_duration_ms = Column(BigInteger, default=0)
    page_views = Column(Integer, default=0)
    first_visit = Column(BigInteger, nullable=True)
    last_visit = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
