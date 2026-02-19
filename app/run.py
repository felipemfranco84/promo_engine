import asyncio
import uvicorn
import logging
import sys
import os

# Força o diretório atual no PATH do Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from core.database import init_db
    from core.bot import bot_worker
    from app.main import app
    print("Módulos carregados com sucesso!")
except ImportError as e:
    print(f"Erro crítico de importação: {e}")
    print(f"Diretório atual: {BASE_DIR}")
    print(f"Conteúdo do diretório: {os.listdir(BASE_DIR)}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemRunner")

async def start_fastapi():
    """Inicia o servidor na porta 8002 para o Nginx."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    try:
        init_db()
        logger.info("Banco de dados pronto.")
        
        logger.info("Iniciando API e Bot (Porta 8002)...")
        await asyncio.gather(
            start_fastapi(),
            bot_worker.start()
        )
    except Exception as e:
        logger.error(f"Falha na orquestração: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Encerrado.")