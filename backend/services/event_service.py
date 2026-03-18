import json
from datetime import datetime
from core.queue import push_event

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
        # Falha de log não deve bloquear o fluxo
        pass


def handle_event(event):
    """Processa evento: faz validação básica, log e adiciona na fila."""
    if not isinstance(event, dict):
        raise ValueError("Evento inválido: deve ser um objeto JSON")

    # Campos básicos esperados
    required = ["event_type", "session_id", "timestamp"]
    if not all(field in event for field in required):
        raise ValueError(f"Evento faltando campos obrigatórios: {required}")

    # Normaliza e marca dados se necessário
    event_payload = {
        "event_type": str(event.get("event_type")),
        "session_id": str(event.get("session_id")),
        "document_id": str(event.get("document_id", "")),
        "timestamp": event.get("timestamp"),
        "page": int(event.get("page", 0)) if event.get("page") is not None else None,
        "metadata": event.get("metadata", {}),
    }

    log_event(event_payload)
    push_event(event_payload)
    return event_payload
