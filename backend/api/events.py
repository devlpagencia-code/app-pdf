from typing import Optional
import os
import json
from fastapi import APIRouter, HTTPException, Request
from services.whatsapp_service import WhatsAppService
from repositories.event_repo import EventRepo
from database.db import SessionLocal

router = APIRouter(prefix='/api')


@router.post('/events')
async def receive_events(request: Request):
    db = SessionLocal()

    try:
        print("[API] Recebendo evento...")

        try:
            events = await request.json()
        except Exception:
            body = await request.body()
            events = json.loads(body)

        repo = EventRepo(db)

        processed = []
        whatsapp_sent = []

        for e in events:
            print(f"[API] Processando evento: {e}")

            # 🔥 VALIDAÇÃO MÍNIMA (evita 400/500)
            if not isinstance(e, dict):
                raise ValueError("Evento inválido")

            if not e.get("event_type") or not e.get("session_id") or not e.get("timestamp"):
                raise ValueError("Campos obrigatórios ausentes")

            # 🔥 garantir metadata_json
            metadata = e.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}

            e["metadata_json"] = metadata

            # 🔥 salvar no banco
            repo.create(e)

            processed.append(e)

            # 🔥 WhatsApp protegido (NUNCA quebra API)
            if e.get('event_type') == 'document_close':
                try:
                    whatsapp = WhatsAppService()
                    user_number = os.getenv('USER_WHATSAPP_NUMBER', '+5511999999999')

                    success = whatsapp.send_analytics_message(
                        to_number=user_number,
                        session_id=e.get('session_id'),
                        document_id=e.get('document_id'),
                        top_n=int(os.getenv('WHATSAPP_TOP_N', 3)),
                    )

                    whatsapp_sent.append({
                        'session_id': e.get('session_id'),
                        'sent': success
                    })

                except Exception as err:
                    print("Erro ao enviar WhatsApp:", err)

                    whatsapp_sent.append({
                        'session_id': e.get('session_id'),
                        'sent': False
                    })

        db.commit()

        print("[API] Eventos processados com sucesso.")

        return {
            'status': 'ok',
            'processed': len(processed),
            'whatsapp_sent': whatsapp_sent
        }

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        db.rollback()
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


# ✅ ROTA FORA DO POST (CORRETO)
@router.get('/analytics/page-times')
def page_time_summary(document_id: Optional[str] = None, session_id: Optional[str] = None):
    db = SessionLocal()

    try:
        repo = EventRepo(db)
        data = repo.get_page_time_summary(document_id, session_id)
        return {'metrics': data}

    finally:
        db.close()