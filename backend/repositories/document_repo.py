from database.db import SessionLocal
from models.document import Document

class DocumentRepo:
    def __init__(self, db=None):
        self.db = db or SessionLocal()

    def create(self, token, file_path):
        doc = Document(token=token, file_path=file_path)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_token(self, token):
        doc = self.db.query(Document).filter(Document.token == token).first()
        if not doc:
            raise ValueError('Document not found')
        return doc

