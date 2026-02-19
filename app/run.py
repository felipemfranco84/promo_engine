import asyncio
import uvicorn
import logging
from core.database import init_db
from core.bot import bot_worker
from app.main import app

logger = logging.getLogger("SystemRunner")

async def start_fastapi():
    """
    Inicia o servidor web uvicorn na porta 8002 conforme 
    configuração do Nginx Reverse Proxy.
    """
    try:
        # ALTERADO: Porta 8080 -> 8002 para bater com o Nginx
        config = uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"Erro ao iniciar FastAPI: {e}")

async def main():
    """Orquestrador do Worker e da API."""
    try:
        init_db()
        logger.info("Banco de Dados inicializado.")

        logger.info("Iniciando Worker e API na porta 8002...")
        await asyncio.gather(
            start_fastapi(),
            bot_worker.start()
        )
    except Exception as e:
        logger.error(f"Falha crítica: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sistema encerrado pelo usuário.")