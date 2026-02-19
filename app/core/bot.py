import logging
import re
import hashlib
import asyncio
from telethon import TelegramClient, events
from config import settings
from core.database import SessionLocal, PromoModel, ConfigModel

logger = logging.getLogger("BotWorker")

class PromotionBot:
    """
    Docstring: Motor de captura inteligente com filtros dinâmicos via DB.
    O motivo desta lógica existir é permitir que o Arquiteto gerencie o bot
    totalmente via interface web, filtrando ruído e mantendo a produtividade.
    """
    def __init__(self):
        self.client = TelegramClient('promo_engine_session', settings.API_ID, settings.API_HASH)

    def generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def extract_price(self, text: str) -> float:
        try:
            match = re.search(r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', text)
            if match:
                return float(match.group(1).replace('.', '').replace(',', '.'))
        except Exception:
            pass
        return 0.0

    async def start(self):
        logger.info("Iniciando motor de captura silencioso (v7.1.0)...")
        
        @self.client.on(events.NewMessage())
        async def my_event_handler(event):
            db = SessionLocal()
            try:
                # 1. Carrega configurações dinâmicas do banco
                sys_config = db.query(ConfigModel).filter(ConfigModel.id == "global").first()
                if not sys_config: return
                
                target_channels = sys_config.channels.split(',')
                keywords = sys_config.keywords.split(',')

                # Verifica se a mensagem vem de um dos canais monitorados
                if event.chat and hasattr(event.chat, 'username'):
                    if event.chat.username not in target_channels:
                        return
                else:
                    return

                msg_text = event.message.message
                if not msg_text: return
                
                # Evita duplicatas
                msg_id = self.generate_id(msg_text)
                if db.query(PromoModel).filter(PromoModel.id == msg_id).first():
                    return

                # 2. Persistência no Banco (Dashboard Web)
                preco = self.extract_price(msg_text)
                new_promo = PromoModel(
                    id=msg_id,
                    titulo=msg_text.split('\n')[0][:100],
                    preco=preco,
                    link=f"https://t.me/{event.chat.username}/{event.message.id}",
                    fonte=f"Telegram - {event.chat.username}"
                )
                db.add(new_promo)
                db.commit()

                # 3. Filtro de Interesse para envio ao Telegram do Arquiteto
                texto_low = msg_text.lower()
                match_keywords = any(kw.strip() in texto_low for kw in keywords if kw.strip())

                if match_keywords:
                    await self.client.send_message(settings.MY_PRIVATE_GROUP_ID, event.message)
                    logger.info(f"✅ Notificação enviada (Filtro Web): {new_promo.titulo}")
                else:
                    logger.debug(f"📁 Apenas arquivado no DB: {new_promo.titulo}")

            except Exception as e:
                logger.error(f"Erro no processamento do bot: {e}", exc_info=True)
                db.rollback()
            finally:
                db.close()

        await self.client.start(phone=settings.PHONE_NUMBER)
        await self.client.run_until_disconnected()

bot_worker = PromotionBot()