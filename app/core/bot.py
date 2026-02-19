import logging
import re
import hashlib
from telethon import TelegramClient, events
from config import settings
from core.database import SessionLocal, PromoModel, ConfigModel

logger = logging.getLogger("BotWorker")

class PromotionBot:
    """
    Docstring: Motor de captura com filtros dinâmicos via Banco de Dados.
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
        except: pass
        return 0.0

    async def start(self):
        logger.info("Bot iniciado. Aguardando promoções...")
        
        @self.client.on(events.NewMessage())
        async def my_event_handler(event):
            db = SessionLocal()
            try:
                # Carrega filtros do Banco
                conf = db.query(ConfigModel).first() or ConfigModel()
                target_channels = conf.channels.split(',')
                keywords = conf.keywords.split(',')

                if not event.chat or not hasattr(event.chat, 'username'): return
                if event.chat.username not in target_channels: return

                msg_text = event.message.message
                if not msg_text: return
                
                msg_id = self.generate_id(msg_text)
                if db.query(PromoModel).filter(PromoModel.id == msg_id).first(): return

                # Salva no DB para o Dashboard
                new_promo = PromoModel(
                    id=msg_id,
                    titulo=msg_text.split('\n')[0][:100],
                    preco=self.extract_price(msg_text),
                    link=f"https://t.me/{event.chat.username}/{event.message.id}",
                    fonte=f"Telegram - {event.chat.username}"
                )
                db.add(new_promo)
                db.commit()

                # Filtro para Telegram Privado
                if any(kw.strip().lower() in msg_text.lower() for kw in keywords if kw.strip()):
                    await self.client.send_message(settings.MY_PRIVATE_GROUP_ID, event.message)
            except Exception as e:
                logger.error(f"Erro no bot: {e}")
            finally:
                db.close()

        await self.client.start(phone=settings.PHONE_NUMBER)
        await self.client.run_until_disconnected()

bot_worker = PromotionBot()