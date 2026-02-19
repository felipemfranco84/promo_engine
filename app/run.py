import asyncio
import uvicorn
import logging
import sys
import os

# Força a raiz do projeto no sys.path de forma absoluta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    # Agora o Python encontrará 'config' na raiz e 'core.database'
    import config
    from core.database import init_db
    from core.bot import bot_worker
    from app.main import app
    print("✅ Todos os módulos e configurações carregados com sucesso!")
except ImportError as e:
    print(f"❌ Erro de Importação: {e}")
    print(f"PATH atual: {sys.path}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemRunner")

async def start_fastapi():
    """Configurado para porta 8002 (Nginx)"""
    cfg = uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="info")
    server = uvicorn.Server(cfg)
    await server.serve()

async def main():
    try:
        init_db()
        logger.info("Banco de dados SQLite pronto.")
        # Inicia Bot e API
        await asyncio.gather(
            start_fastapi(),
            bot_worker.start()
        )
    except Exception as e:
        logger.error(f"Erro na orquestração: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sistema encerrado.")