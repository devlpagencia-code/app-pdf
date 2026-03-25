#!/usr/bin/env python3
"""
Script para migrar PDFs de storage local para S3.
Execute uma vez quando migrar para produção com S3.

Uso:
    python -m workers.migrate_storage
"""

import os
import logging
from services.storage_service import StorageService
from repositories.document_repo import DocumentRepo
from database.db import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_to_s3():
    """Migra todos os PDFs locais para S3 e atualiza banco."""
    storage = StorageService()
    repo = DocumentRepo()

    if storage.storage_type != 's3':
        logger.error("Storage type não é S3. Configure STORAGE_TYPE=s3 no .env")
        return

    db = SessionLocal()
    try:
        # Busca todos os documentos
        documents = db.query(repo.model).all()
        migrated = 0

        for doc in documents:
            if doc.file_path.startswith('storage/') and os.path.exists(doc.file_path):
                # Lê arquivo local
                with open(doc.file_path, 'rb') as f:
                    file_content = f.read()

                # Salva no S3
                filename = os.path.basename(doc.file_path)
                s3_path = storage.save_file(file_content, filename)

                # Atualiza banco
                doc.file_path = s3_path
                db.commit()

                # Remove arquivo local
                os.remove(doc.file_path)
                migrated += 1
                logger.info(f"Migrado: {filename}")

        logger.info(f"Migração concluída: {migrated} arquivos migrados para S3")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro na migração: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_to_s3()
