import logging
from datetime import datetime, timedelta
from sqlalchemy import func, case, Integer

from database.db import SessionLocal
from models.event import Event
from repositories.analytics_repo import AnalyticsRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventAggregator:

    def aggregate_last_5_minutes(self):
        db = SessionLocal()

        try:
            cutoff = int((datetime.utcnow() - timedelta(minutes=5)).timestamp() * 1000)

            base_query = db.query(Event).filter(
                Event.processed == False,
                Event.timestamp <= cutoff,
                Event.document_id.isnot(None),
                Event.session_id.isnot(None),
                Event.event_type.in_(["page_view", "page_time"])
            )

            results = db.query(
                Event.document_id,
                Event.session_id,
                Event.page,

                func.sum(
                    case(
                        (
                            Event.event_type == 'page_time',
                            func.coalesce(
                                Event.metadata_json['duration_ms'].as_string().cast(Integer),
                                0
                            )
                        ),
                        else_=0
                    )
                ).label("total_duration_ms"),

                func.sum(
                    case(
                        (
                            Event.event_type.in_(["page_view", "page_time"]),
                            1
                        ),
                        else_=0
                    )
                ).label("page_views"),

                func.min(Event.timestamp).label("first_visit"),
                func.max(Event.timestamp).label("last_visit")

            ).filter(
                Event.processed == False,
                Event.timestamp <= cutoff,
                Event.document_id.isnot(None),
                Event.session_id.isnot(None),
                Event.event_type.in_(["page_view", "page_time"])
            ).group_by(
                Event.document_id,
                Event.session_id,
                Event.page
            ).all()

            if not results:
                logger.info("Nenhum evento para agregar")
                return {"processed": 0}

            analytics_repo = AnalyticsRepo(db)

            for row in results:
                if not row.document_id or not row.session_id:
                    continue

                analytics_repo.upsert_page_analytics(
                    document_id=row.document_id,
                    session_id=row.session_id,
                    page=row.page,
                    total_duration_ms=row.total_duration_ms or 0,
                    page_views=row.page_views or 0,
                    first_visit=row.first_visit,
                    last_visit=row.last_visit,
                )

            updated = base_query.update(
                {Event.processed: True},
                synchronize_session=False
            )
            
            delete_cutoff = int((datetime.utcnow() - timedelta(days=7)).timestamp() * 1000)

            deleted = db.query(Event).filter(
                Event.timestamp < delete_cutoff
            ).delete(synchronize_session=False)

            db.commit()

            logger.info(f"Eventos processados: {updated} | Eventos deletados: {deleted}")

            return {
                "processed": updated,
                "deleted": deleted
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Erro na agregação: {str(e)}")
            raise

        finally:
            db.close()

def run_aggregation():
    aggregator = EventAggregator()
    return aggregator.aggregate_last_5_minutes()