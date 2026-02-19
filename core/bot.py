import logging
import re
import hashlib
from telethon import TelegramClient, events
from config import settings
from core.database import SessionLocal, PromoModel

# Logger específico para o Motor de Captura
logger = logging.getLogger("BotWorker")

class PromotionBot:
    """
    Docstring: Motor principal de captura e filtragem de mensagens.
    O motivo desta lógica existir é transformar mensagens de texto não estruturadas
    em objetos de dados prontos para o banco e para o seu grupo.
    """
    def __init__(self):
        # Usamos um nome de sessão fixo para evitar re-login constante
        self.client = TelegramClient('promo_engine_session', settings.API_ID, settings.API_HASH)

    def generate_id(self, text: str) -> str:
        """Gera um hash único para evitar duplicados."""
        return hashlib.md5(text.encode()).hexdigest()

    def extract_price(self, text: str) -> float:
        """Tenta extrair o preço da mensagem usando Regex."""
        try:
            match = re.search(r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', text)
            if match:
                # Converte "1.299,00" para 1299.00
                return float(match.group(1).replace('.', '').replace(',', '.'))
        except Exception as e:
            logger.debug(f"Falha na extração de preço: {e}")
        return 0.0

    async def start(self):
        """Inicia a escuta nos canais alvo."""
        logger.info("Iniciando escuta nos canais do Telegram...")
        
        @self.client.on(events.NewMessage(chats=settings.TARGET_CHANNELS))
        async def my_event_handler(event):
            db = SessionLocal() # Sessão local por evento para evitar deadlocks
            try:
                msg_text = event.message.message
                if not msg_text: return
                
                msg_id = self.generate_id(msg_text)

                # Verificação de duplicidade
                exists = db.query(PromoModel).filter(PromoModel.id == msg_id).first()
                if exists:
                    logger.debug(f"Oferta duplicada ignorada: {msg_id}")
                    return

                # Extração de dados
                preco = self.extract_price(msg_text)
                primeira_linha = msg_text.split('\n')[0][:100]
                
                # Criando o registro
                new_promo = PromoModel(
                    id=msg_id,
                    titulo=primeira_linha,
                    preco=preco,
                    link=f"https://t.me/{event.chat.username}/{event.message.id}",
                    fonte=f"Telegram - {event.chat.username}",
                    loja="Identificação pendente" # Expansível com novas regex
                )

                db.add(new_promo)
                db.commit()
                
                # Encaminhamento para o seu grupo privado
                await self.client.send_message(settings.MY_PRIVATE_GROUP_ID, event.message)
                logger.info(f"Nova oferta capturada: {primeira_linha}")

            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            finally:
                db.close()

        await self.client.start(phone=settings.PHONE_NUMBER)
        await self.client.run_until_disconnected()

bot_worker = PromotionBot()