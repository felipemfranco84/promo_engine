import logging
import re
import hashlib
import asyncio
from telethon import TelegramClient, events
from config import settings
from core.database import SessionLocal, PromoModel, ConfigModel

# Docstring: O motivo desta lógica existir é centralizar o motor de captura.
# Ele transforma mensagens brutas do Telegram em dados estruturados no SQLite
# e aplica filtros de interesse em tempo real.
logger = logging.getLogger("BotWorker")

class PromotionBot:
    def __init__(self):
        """Inicializa o cliente Telethon usando as configurações do Pydantic."""
        self.client = TelegramClient(
            'promo_engine_session', 
            settings.API_ID, 
            settings.API_HASH
        )

    def generate_id(self, text: str) -> str:
        """Gera um hash MD5 único para evitar duplicidade de ofertas."""
        return hashlib.md5(text.encode()).hexdigest()

    def extract_price(self, text: str) -> float:
        """Extrai preços no formato R$ 0,00 ou R$0.00."""
        try:
            match = re.search(r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', text)
            if match:
                return float(match.group(1).replace('.', '').replace(',', '.'))
        except Exception as e:
            logger.debug(f"Falha ao extrair preço: {e}")
        return 0.0

    def extract_link(self, text: str) -> str:
        """Extrai a primeira URL encontrada na mensagem."""
        try:
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, text)
            return urls[0] if urls else "Link não encontrado"
        except:
            return "Erro na extração de link"

    async def start(self):
        """Inicia o ciclo de vida do Bot."""
        logger.info("🚀 BotWorker: Iniciando escuta nos canais do Telegram...")

        @self.client.on(events.NewMessage())
        async def message_handler(event):
            # Criamos uma nova sessão de banco para cada thread/evento (Thread-safe)
            db = SessionLocal()
            try:
                # 1. Identificação da Origem
                chat_username = event.chat.username if hasattr(event.chat, 'username') else "Unknown"
                
                # 2. Carga Dinâmica de Filtros do Banco (Clean Code: Sem hardcode)
                conf = db.query(ConfigModel).first() or ConfigModel()
                target_channels = [c.strip() for c in conf.channels.split(',')]
                keywords = [k.strip().lower() for k in conf.keywords.split(',')]

                # 3. Filtro de Canal
                if chat_username not in target_channels:
                    return # Silencioso para canais não monitorados

                msg_text = event.message.message
                if not msg_text:
                    return

                logger.info(f"📩 Mensagem recebida de: @{chat_username}")

                # 4. Filtro de Duplicidade
                msg_id = self.generate_id(msg_text)
                if db.query(PromoModel).filter(PromoModel.id == msg_id).first():
                    logger.warning(f"♻️ Oferta duplicada ignorada (ID: {msg_id[:8]})")
                    return

                # 5. Extração de Dados
                titulo = msg_text.split('\n')[0][:100]
                preco = self.extract_price(msg_text)
                link = self.extract_link(msg_text)

                # 6. Persistência no Banco (Dashboard)
                new_promo = PromoModel(
                    id=msg_id,
                    titulo=titulo,
                    preco=preco,
                    link=link,
                    fonte=f"@{chat_username}"
                )
                db.add(new_promo)
                db.commit()
                logger.info(f"📥 Salva no Dashboard: {titulo[:30]}...")

                # 7. Filtro de Palavras-Chave e Encaminhamento Privado
                match_keywords = [kw for kw in keywords if kw and kw in msg_text.lower()]
                if match_keywords:
                    logger.info(f"🔥 MATCH! Palavra-chave encontrada: {match_keywords[0]}")
                    await self.client.send_message(
                        settings.MY_PRIVATE_GROUP_ID, 
                        event.message
                    )
                    logger.info(f"🚀 Encaminhada para o Grupo Privado.")
                else:
                    logger.debug("📌 Sem palavras-chave de interesse. Apenas armazenada.")

            except Exception as e:
                logger.error(f"❌ Erro no BotWorker: {e}", exc_info=True)
            finally:
                db.close()

        # Inicia a conexão oficial
        await self.client.start(phone=settings.PHONE_NUMBER)
        logger.info("✅ Conexão estabelecida com o Telegram.")
        await self.client.run_until_disconnected()

# Instância exportada para o run.py
bot_worker = PromotionBot()
