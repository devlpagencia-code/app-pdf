import json
import os

class DocumentRepo:
    def __init__(self):
        self.file = 'storage/documents.json'
        os.makedirs('storage', exist_ok=True)
        if not os.path.exists(self.file):
            with open(self.file, 'w') as f:
                json.dump([], f)

    def _read_all(self):
        with open(self.file, 'r') as f:
            return json.load(f)

    def _write_all(self, docs):
        with open(self.file, 'w') as f:
            json.dump(docs, f)

    def create(self, token, file_path):
        docs = self._read_all()
        docs.append({'token': token, 'file_path': file_path})
        self._write_all(docs)

    def get_by_token(self, token):
        docs = self._read_all()
        for d in docs:
            if d.get('token') == token:
                return d
        raise ValueError('Document not found')
