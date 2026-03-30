from database.db import SessionLocal
from models.analytics import PageAnalytics


class AnalyticsRepo:
    def __init__(self, db=None):
        self.db = db or SessionLocal()

    def upsert_page_analytics(self, document_id, session_id, page, total_duration_ms, page_views, first_visit, last_visit):
        """Insere ou atualiza registro de analytics."""
        existing = self.db.query(PageAnalytics).filter(
            PageAnalytics.document_id == document_id,
            PageAnalytics.session_id == session_id,
            PageAnalytics.page == page,
        ).first()

        if existing:
            existing.total_duration_ms += total_duration_ms
            existing.page_views += page_views
            existing.last_visit = max(existing.last_visit, last_visit) if existing.last_visit else last_visit
            self.db.commit()
            return existing
        else:
            analytics = PageAnalytics(
                document_id=document_id,
                session_id=session_id,
                page=page,
                total_duration_ms=total_duration_ms,
                page_views=page_views,
                first_visit=first_visit,
                last_visit=last_visit,
            )
            self.db.add(analytics)
            self.db.commit()
            self.db.refresh(analytics)
            return analytics

    def get_analytics_by_document(self, document_id):
        """Retorna analytics agregadas de um documento."""
        return self.db.query(PageAnalytics).filter(
            PageAnalytics.document_id == document_id
        ).all()

    def get_analytics_by_session(self, session_id):
        """Retorna analytics agregadas de uma sessão."""
        return self.db.query(PageAnalytics).filter(
            PageAnalytics.session_id == session_id
        ).all()

    def get_top_pages(self, document_id, limit=10):
        """Retorna páginas mais acessadas de um documento."""
        return self.db.query(PageAnalytics).filter(
            PageAnalytics.document_id == document_id
        ).order_by(PageAnalytics.page_views.desc()).limit(limit).all()

    def get_session_time_summary(self, session_id):
        """Retorna tempo total gasto em uma sessão."""
        result = self.db.query(PageAnalytics).filter(
            PageAnalytics.session_id == session_id
        ).all()
        total_time_ms = sum(a.total_duration_ms for a in result)
        total_pages = sum(a.page_views for a in result)
        return {'session_id': session_id, 'total_time_ms': total_time_ms, 'total_pages': total_pages}
