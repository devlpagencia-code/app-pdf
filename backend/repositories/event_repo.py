from database.db import SessionLocal
from models.event import Event
import logging

logger = logging.getLogger(__name__)

class EventRepo:

    def __init__(self, db):
        self.db = db

    def _validate_payload(self, payload):
        payload = payload.copy()

        required = ["event_type", "document_id", "session_id"]

        for field in required:
            if field not in payload:
                raise ValueError(f"Missing field: {field}")

        # validar tipo de evento
        allowed_types = ["page_view", "page_time", "document_open", "document_close"]
        if payload["event_type"] not in allowed_types:
            raise ValueError("Invalid event_type")

        metadata = payload.get("metadata_json", {})

        if not isinstance(metadata, dict):
            metadata = {}

        duration = metadata.get("duration_ms", 0)

        try:
            duration = int(duration)
        except (ValueError, TypeError):
            duration = 0

        duration = max(0, min(duration, 600000))

        payload["metadata_json"] = {
            "duration_ms": duration
        }

        return payload

    def create(self, payload):
        try:
            payload = self._validate_payload(payload)

            event = Event(**payload)
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)

            return event

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao salvar evento: {str(e)}")
            raise

    def get_page_time_summary(self, document_id=None, session_id=None):
        query = self.db.query(Event).filter(Event.event_type == 'page_time')
        if document_id:
            query = query.filter(Event.document_id == document_id)
        if session_id:
            query = query.filter(Event.session_id == session_id)

        summary = {}
        for event in query.all():
            duration = 0
            metadata = event.metadata_json or {}
            if isinstance(metadata, dict):
                duration = metadata.get('duration_ms', 0)
                if duration is None:
                    duration = 0
            try:
                duration = int(duration)
            except Exception:
                duration = 0

            page = event.page if event.page is not None else 'unknown'
            k = (page, event.session_id, event.document_id)
            if k not in summary:
                summary[k] = 0
            summary[k] += duration

        result = []
        for (page, session, document), total in summary.items():
            result.append({
                'document_id': document,
                'session_id': session,
                'page': page,
                'total_duration_ms': total,
            })

        # sort by document, session, page for consistent output
        return sorted(result, key=lambda x: (str(x['document_id']), str(x['session_id']), str(x['page'])))
