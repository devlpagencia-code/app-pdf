from sqlalchemy import Column, Integer, String
from database.db import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    file_path = Column(String, nullable=False)
