import os
from pathlib import Path


def load_env_file(path: str = '.env') -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    with env_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    if not (POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_HOST and POSTGRES_PORT and POSTGRES_DB):
        raise ValueError(
            'Configuração de banco de dados incompleta. ' 
            'Defina DATABASE_URL ou todas as variáveis POSTGRES_* no .env ou ambiente.'
        )
    DATABASE_URL = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# Configuração de storage
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')  # 'local' ou 's3'
STORAGE_LOCAL_PATH = os.getenv('STORAGE_LOCAL_PATH', 'storage/pdfs')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
