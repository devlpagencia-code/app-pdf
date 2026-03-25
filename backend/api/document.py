from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from services.document_service import DocumentService
from repositories.document_repo import DocumentRepo

router = APIRouter(prefix='/api')

service = DocumentService(DocumentRepo())

@router.post('/upload')
def upload(file: UploadFile):
    return service.upload(file)

from fastapi import HTTPException

@router.get('/document/{token}')
def get_document(token: str):
    try:
        doc = service.get_by_token(token)
    except ValueError:
        raise HTTPException(status_code=404, detail='Document not found')

    return {
        'id': token,
        'url': doc['url']  # Agora usa URL do storage service
    }

@router.get('/pdf/{token}')
def serve_pdf(token: str):
    try:
        doc = service.get_by_token(token)
    except ValueError:
        raise HTTPException(status_code=404, detail='Document not found')

    # Se for local, serve via FileResponse
    if doc['file_path'].startswith('storage/'):
        return FileResponse(doc['file_path'], media_type='application/pdf')
    else:
        # Se for S3, redireciona para URL do S3
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=doc['url'])

