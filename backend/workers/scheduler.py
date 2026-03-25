"""
Scheduler para agregação e limpeza de eventos.
Execute este script como cron job ou tarefa agendada.

Exemplo de cron (Linux):
    0 2 * * * cd /caminho/para/backend && python -m workers.scheduler

Exemplo de Task Scheduler (Windows):
    Disparar: C:\\Python\\python.exe -m workers.scheduler
    Pasta: C:\\caminho\\para\\backend
"""

import logging
import schedule
import time
from workers.event_aggregator import run_aggregation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scheduled_aggregation():
    """Função chamada periodicamente."""
    logger.info("Iniciando agregação de eventos...")
    try:
        result = run_aggregation(days_to_keep=7)
        logger.info(f"Agregação concluída: {result}")
    except Exception as e:
        logger.error(f"Erro na agregação: {str(e)}")


def start_scheduler():
    """Inicia scheduler que roda agregação todo dia às 2:00 AM."""
    schedule.every().day.at("02:00").do(scheduled_aggregation)
    
    logger.info("Scheduler iniciado. Aguardando próxima execução...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
