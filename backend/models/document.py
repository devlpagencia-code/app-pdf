# app/models/document.py

from sqlalchemy import Column, Integer, String
from app.database.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    file_path = Column(String)