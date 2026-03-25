from database.db import SessionLocal
from models.event import Event

class EventRepo:
    def __init__(self, db=None):
        self.db = db or SessionLocal()

    def create(self, payload):
        # Usa SessionLocal já importado do database.db
        with SessionLocal() as session:
            try:
                event = Event(**payload)
                session.add(event)
                session.commit()
                session.refresh(event)
                return event
            except Exception as e:
                session.rollback()
                print("Erro ao salvar evento:", e)
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
