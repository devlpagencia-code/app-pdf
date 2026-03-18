import uuid
import os
import json

class DocumentService:
    def __init__(self, repo):
        self.repo = repo

    def upload(self, file):
        token = uuid.uuid4().hex
        path = f"storage/pdfs/{token}.pdf"
        os.makedirs("storage/pdfs", exist_ok=True)
        with open(path, "wb") as f:
            f.write(file.file.read())
        self.repo.create(token, path)
        return {
            "token": token,
            "link": f"http://localhost:5173/?doc={token}"
        }

    def get_by_token(self, token):
        return self.repo.get_by_token(token)
