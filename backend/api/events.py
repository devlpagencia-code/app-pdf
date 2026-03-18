from fastapi import APIRouter, Body, HTTPException
from services.event_service import handle_event

router = APIRouter(prefix='/api')

@router.post('/events')
def receive_events(events: list = Body(...)):
    processed = []
    try:
        for e in events:
            processed.append(handle_event(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail='Erro interno ao processar evento')
    return {'status': 'queued', 'processed': processed}
