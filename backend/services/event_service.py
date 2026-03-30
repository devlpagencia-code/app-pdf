import json
from datetime import datetime
from core.queue import push_event
from repositories.event_repo import EventRepo

EVENT_LOG = "event_log.json"


def log_event(event):
    """Salva evento localmente para debug e auditoria."""
    try:
        record = {
            "received_at": datetime.utcnow().isoformat() + "Z",
            "event": event,
        }
        with open(EVENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def handle_event(event, db):
    """Processa evento: valida, normaliza, salva no DB e envia para fila."""

    if not isinstance(event, dict):
        raise ValueError("Evento inválido: deve ser um objeto JSON")

    required = ["event_type", "session_id", "timestamp"]
    for field in required:
        if field not in event or event.get(field) is None:
            raise ValueError(f"Campo obrigatório ausente: {field}")

    event_type = str(event.get("event_type"))
    session_id = str(event.get("session_id"))

    document_id = event.get("document_id")
    document_id = str(document_id) if document_id else None

    try:
        timestamp = int(event.get("timestamp"))
    except Exception:
        raise ValueError("Timestamp inválido")

    page = event.get("page")
    try:
        page = int(page) if page is not None else None
    except Exception:
        page = None

    metadata = event.get("metadata")

    if not isinstance(metadata, dict):
        metadata = {}

    try:
        metadata = json.loads(json.dumps(metadata))
    except Exception:
        metadata = {}

    event_payload = {
        "event_type": event_type,
        "session_id": session_id,
        "document_id": document_id,
        "timestamp": timestamp,
        "page": page,
        "metadata_json": metadata,
    }

    print("EVENT NORMALIZADO:", event_payload)

    repo = EventRepo(db)
    saved_event = repo.create(event_payload)

    log_event(event_payload)

    push_event(event_payload)

    return {
        "id": saved_event.id,
        "event_type": saved_event.event_type,
        "session_id": saved_event.session_id,
        "document_id": saved_event.document_id,
        "timestamp": saved_event.timestamp,
        "page": saved_event.page,
        "metadata": saved_event.metadata_json,
    }

