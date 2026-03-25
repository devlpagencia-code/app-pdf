from typing import Optional
import os
from fastapi import APIRouter, Body, HTTPException, Request
from services.event_service import handle_event
from services.whatsapp_service import WhatsAppService
from repositories.event_repo import EventRepo

router = APIRouter(prefix='/api')


@router.post('/events')
async def receive_events(request: Request):
    try:
        print("[API] Recebendo evento...")
        try:
            events = await request.json()
        except Exception:
            # fallback para text/plain
            body = await request.body()
            import json
            events = json.loads(body)
        processed = []
        whatsapp_sent = []
        for e in events:
            print(f"[API] Processando evento: {e}")
            print("Simulando Handle envent")
            processed.append(handle_event(e))
            # Enviar WhatsApp se for document_close
            if e.get('event_type') == 'document_close':
                whatsapp = WhatsAppService()
                user_number = os.getenv('USER_WHATSAPP_NUMBER', '+5511999999999')  # Exemplo
                success = whatsapp.send_analytics_message(
                    to_number=user_number,
                    session_id=e.get('session_id'),
                    document_id=e.get('document_id'),
                    top_n=int(os.getenv('WHATSAPP_TOP_N', 3)),
                )
                whatsapp_sent.append({'session_id': e.get('session_id'), 'sent': success})
        print("[API] Eventos processados com sucesso.")
        return {'status': 'queued', 'processed': processed, 'whatsapp_sent': whatsapp_sent}
    except ValueError as e:
        print("[API] ValueError:", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("[API] Erro inesperado:", e)
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail='Erro interno ao processar evento')

@router.get('/analytics/page-times')
def page_time_summary(document_id: Optional[str] = None, session_id: Optional[str] = None):
    data = EventRepo().get_page_time_summary(document_id=document_id, session_id=session_id)
    return {'metrics': data}
