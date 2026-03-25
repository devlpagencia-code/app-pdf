from typing import Optional
from fastapi import APIRouter, HTTPException
from repositories.analytics_repo import AnalyticsRepo
from workers.event_aggregator import run_aggregation

router = APIRouter(prefix='/api')


@router.get('/analytics/pages/{document_id}')
def get_document_analytics(document_id: str):
    """Retorna analytics agregadas de um documento."""
    try:
        analytics = AnalyticsRepo().get_analytics_by_document(document_id)
        if not analytics:
            return {'document_id': document_id, 'analytics': []}
        
        result = [{
            'page': a.page,
            'total_duration_ms': a.total_duration_ms,
            'page_views': a.page_views,
            'first_visit': a.first_visit,
            'last_visit': a.last_visit,
        } for a in analytics]
        
        return {'document_id': document_id, 'analytics': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/analytics/top-pages/{document_id}')
def get_top_pages(document_id: str, limit: int = 10):
    """Retorna páginas mais acessadas de um documento."""
    try:
        top_pages = AnalyticsRepo().get_top_pages(document_id, limit=limit)
        result = [{
            'page': p.page,
            'page_views': p.page_views,
            'total_duration_ms': p.total_duration_ms,
        } for p in top_pages]
        
        return {'document_id': document_id, 'limit': limit, 'top_pages': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/analytics/session/{session_id}')
def get_session_analytics(session_id: str):
    """Retorna resumo de tempo em uma sessão."""
    try:
        summary = AnalyticsRepo().get_session_time_summary(session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/maintenance/aggregate')
def trigger_aggregation(
    days_to_keep: int = 7,
    cleanup_documents: bool = False,
    document_retention_days: int = 30
):
    """
    Dispara agregação e limpeza de eventos.
    Agrupa eventos de N dias atrás em PageAnalytics e deleta brutos.
    Opcionalmente limpa documentos antigos não acessados.
    """
    try:
        result = run_aggregation(
            days_to_keep=days_to_keep,
            cleanup_documents=cleanup_documents,
            document_retention_days=document_retention_days
        )
        return {
            'status': 'success',
            'message': f'Agregados {result["aggregated"]} registros, deletados {result["deleted_events"]} eventos, {result["deleted_documents"]} documentos',
            'details': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
