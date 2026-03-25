import os
import boto3
from botocore.exceptions import NoCredentialsError
from core.config import (
    STORAGE_TYPE, STORAGE_LOCAL_PATH,
    AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
)


class StorageService:
    """Serviço abstrato para armazenamento de arquivos (local ou S3)."""

    def __init__(self):
        self.storage_type = STORAGE_TYPE
        if self.storage_type == 's3':
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            self.bucket = AWS_S3_BUCKET

    def save_file(self, file_content: bytes, filename: str) -> str:
        """Salva arquivo e retorna URL/path para acesso."""
        if self.storage_type == 'local':
            return self._save_local(file_content, filename)
        elif self.storage_type == 's3':
            return self._save_s3(file_content, filename)
        else:
            raise ValueError(f"Tipo de storage não suportado: {self.storage_type}")

    def get_file_url(self, filename: str) -> str:
        """Retorna URL para acessar arquivo."""
        if self.storage_type == 'local':
            return self._get_local_url(filename)
        elif self.storage_type == 's3':
            return self._get_s3_url(filename)
        else:
            raise ValueError(f"Tipo de storage não suportado: {self.storage_type}")

    def delete_file(self, filename: str) -> bool:
        """Deleta arquivo."""
        if self.storage_type == 'local':
            return self._delete_local(filename)
        elif self.storage_type == 's3':
            return self._delete_s3(filename)
        else:
            raise ValueError(f"Tipo de storage não suportado: {self.storage_type}")

    # Local storage methods
    def _save_local(self, file_content: bytes, filename: str) -> str:
        """Salva no filesystem local."""
        os.makedirs(STORAGE_LOCAL_PATH, exist_ok=True)
        filepath = os.path.join(STORAGE_LOCAL_PATH, filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)
        return filepath  # Retorna path absoluto

    def _get_local_url(self, filename: str) -> str:
        """Retorna URL local para arquivo."""
        return f"http://localhost:8000/api/pdf/{filename.replace('.pdf', '')}"

    def _delete_local(self, filename: str) -> bool:
        """Deleta arquivo local."""
        filepath = os.path.join(STORAGE_LOCAL_PATH, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    # S3 storage methods
    def _save_s3(self, file_content: bytes, filename: str) -> str:
        """Salva no S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=file_content,
                ContentType='application/pdf'
            )
            return f"s3://{self.bucket}/{filename}"
        except NoCredentialsError:
            raise ValueError("Credenciais AWS não configuradas")

    def _get_s3_url(self, filename: str) -> str:
        """Retorna URL pública do S3."""
        # Para arquivos públicos, gera URL pré-assinada ou assume bucket público
        return f"https://{self.bucket}.s3.{AWS_REGION}.amazonaws.com/{filename}"

    def _delete_s3(self, filename: str) -> bool:
        """Deleta arquivo do S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=filename)
            return True
        except Exception:
            return False
