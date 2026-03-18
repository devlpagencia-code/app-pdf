from fastapi import APIRouter, HTTPException
from services.event_service import handle_event

router = APIRouter()

@router.post('/events')
def receive_events(events: list):
    processed = []
    try:
        for e in events:
            processed.append(handle_event(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao processar evento")
    return {"status": "queued", "processed": processed}
