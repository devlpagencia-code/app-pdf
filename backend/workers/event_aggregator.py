import logging
from datetime import datetime, timedelta
from repositories.event_repo import EventRepo
from repositories.analytics_repo import AnalyticsRepo
from repositories.document_repo import DocumentRepo
from models.event import Event
from services.storage_service import StorageService
from database.db import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventAggregator:
    """Agregador de eventos: calcula estatísticas e limpa dados brutos."""

    def __init__(self):
        self.event_repo = EventRepo()
        self.analytics_repo = AnalyticsRepo()
        self.document_repo = DocumentRepo()
        self.storage = StorageService()

    def aggregate_and_cleanup(self, days_to_keep=7, cleanup_documents=False, document_retention_days=90):
        """
        Calcula estatísticas de eventos do últimos N dias,
        salva em page_analytics e deleta eventos originais.
        Opcionalmente limpa documentos antigos.
        """
        db = SessionLocal()
        try:
            # Data limite: apenas eventos anteriores a N dias
            cutoff_timestamp = int((datetime.utcnow() - timedelta(days=days_to_keep)).timestamp() * 1000)
            
            # Buscar eventos para agregar
            events = db.query(Event).filter(Event.timestamp < cutoff_timestamp).all()
            
            if not events:
                logger.info(f"Nenhum evento para agregar (cutoff: {cutoff_timestamp})")
                return {'aggregated': 0, 'deleted_events': 0, 'deleted_documents': 0}

            # Agrupar por (document_id, session_id, page)
            aggregates = {}
            for event in events:
                key = (event.document_id, event.session_id, event.page)
                if key not in aggregates:
                    aggregates[key] = {
                        'total_duration_ms': 0,
                        'page_views': 0,
                        'first_visit': event.timestamp,
                        'last_visit': event.timestamp,
                    }
                
                # Somar tempo se for evento de page_time
                if event.event_type == 'page_time':
                    metadata = event.metadata_json or {}
                    duration = metadata.get('duration_ms', 0) or 0
                    aggregates[key]['total_duration_ms'] += int(duration)
                
                # Contar visualizações
                if event.event_type in ['page_view', 'page_time']:
                    aggregates[key]['page_views'] += 1
                
                # Atualizar timestamps
                aggregates[key]['first_visit'] = min(aggregates[key]['first_visit'], event.timestamp)
                aggregates[key]['last_visit'] = max(aggregates[key]['last_visit'], event.timestamp)

            # Salvar agregações
            aggregated_count = 0
            for (doc_id, sess_id, page), stats in aggregates.items():
                self.analytics_repo.upsert_page_analytics(
                    document_id=doc_id,
                    session_id=sess_id,
                    page=page,
                    total_duration_ms=stats['total_duration_ms'],
                    page_views=stats['page_views'],
                    first_visit=stats['first_visit'],
                    last_visit=stats['last_visit'],
                )
                aggregated_count += 1

            # Deletar eventos já agregados
            deleted_events = db.query(Event).filter(Event.timestamp < cutoff_timestamp).delete()
            db.commit()

            deleted_documents = 0
            if cleanup_documents:
                deleted_documents = self._cleanup_old_documents(document_retention_days)

            logger.info(f"Agregados: {aggregated_count} registros | Eventos deletados: {deleted_events} | Documentos deletados: {deleted_documents}")
            return {'aggregated': aggregated_count, 'deleted_events': deleted_events, 'deleted_documents': deleted_documents}

        except Exception as e:
            db.rollback()
            logger.error(f"Erro na agregação: {str(e)}")
            raise
        finally:
            db.close()

    def _cleanup_old_documents(self, retention_days):
        """Remove documentos não acessados há mais de N dias."""
        db = SessionLocal()
        try:
            # Data limite para documentos
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Buscar documentos sem eventos recentes
            old_docs = db.query(self.document_repo.model).filter(
                ~db.query(Event).filter(
                    Event.document_id == self.document_repo.model.token,
                    Event.timestamp >= int(cutoff_date.timestamp() * 1000)
                ).exists()
            ).all()
            
            deleted_count = 0
            for doc in old_docs:
                # Deletar arquivo físico
                filename = f"{doc.token}.pdf"
                self.storage.delete_file(filename)
                
                # Deletar do banco
                db.delete(doc)
                deleted_count += 1
            
            db.commit()
            logger.info(f"Documentos antigos removidos: {deleted_count}")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao limpar documentos: {str(e)}")
            return 0
        finally:
            db.close()



def run_aggregation(days_to_keep=7, cleanup_documents=False, document_retention_days=90):
    """Função simples para disparo em cron ou job agendado."""
    aggregator = EventAggregator()
    result = aggregator.aggregate_and_cleanup(
        days_to_keep=days_to_keep,
        cleanup_documents=cleanup_documents,
        document_retention_days=document_retention_days
    )
    return result
