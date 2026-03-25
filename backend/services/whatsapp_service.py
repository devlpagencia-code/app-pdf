import os
from twilio.rest import Client
from repositories.analytics_repo import AnalyticsRepo

class WhatsAppService:
    def __init__(self):
        self.client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
        self.from_number = 'whatsapp:+14155238886'  # Twilio sandbox number

    def send_analytics_message(self, to_number: str, session_id: str, document_id: str = None, top_n: int = 3):
        """Envia mensagem formatada com resumo da sessão e top páginas opcionais."""
        try:
            repo = AnalyticsRepo()
            summary = repo.get_session_time_summary(session_id)
            total_time_seconds = summary['total_time_ms'] / 1000

            top_pages_text = ''
            if document_id:
                top_pages = repo.get_top_pages(document_id, limit=top_n)
                if top_pages:
                    top_pages_text = '\n\n🏆 Top páginas:\n'
                    for idx, p in enumerate(top_pages, 1):
                        top_pages_text += f"{idx}. Página {p.page}: {p.page_views} visitas ({p.total_duration_ms/1000:.1f}s)\n"

            message = f"""
📊 Relatório de Visualização de PDF

Sessão: {summary['session_id']}
⏱️ Tempo total: {total_time_seconds:.1f} segundos
📄 Páginas visualizadas: {summary['total_pages']}{top_pages_text}

Obrigado por usar nosso visualizador! 😊
            """

            self.client.messages.create(
                body=message.strip(),
                from_=self.from_number,
                to=f'whatsapp:{to_number}'
            )
            return True
        except Exception as e:
            print(f"Erro ao enviar WhatsApp: {e}")
            return False