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
        result = run_aggregation()
        logger.info(f"Agregação concluída: {result}")
    except Exception as e:
        logger.error(f"Erro na agregação: {str(e)}")


def start_scheduler():
    """Inicia scheduler que roda agregação a cada 5 minutos."""
    schedule.every(60).seconds.do(scheduled_aggregation)
    
    logger.info("Scheduler iniciado. Aguardando próxima execução...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_scheduler()
