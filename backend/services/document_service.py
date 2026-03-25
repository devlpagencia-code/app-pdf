import uuid
import os
from services.storage_service import StorageService

class DocumentService:
    def __init__(self, repo):
        self.repo = repo
        self.storage = StorageService()

    def upload(self, file):
        token = uuid.uuid4().hex
        filename = f"{token}.pdf"
        
        # Lê conteúdo do arquivo
        file_content = file.file.read()
        
        # Salva usando storage service (local ou S3)
        storage_path = self.storage.save_file(file_content, filename)
        
        # Salva metadados no banco
        doc = self.repo.create(token, storage_path)
        
        return {
            "token": doc.token,
            "link": f"http://localhost:5173/?doc={doc.token}"
        }

    def get_by_token(self, token):
        doc = self.repo.get_by_token(token)
        return {
            "token": doc.token,
            "file_path": doc.file_path,
            "url": self.storage.get_file_url(f"{token}.pdf")
        }


