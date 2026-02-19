import asyncio
import uvicorn
import logging
from multiprocessing import Process
from app.main import app
from core.bot import bot_worker

logger = logging.getLogger("Runner")

def start_web():
    """Inicia o Dashboard Web."""
    uvicorn.run(app, host="0.0.0.0", port=8002)

async def start_bot():
    """Inicia o Motor do Telegram."""
    await bot_worker.start()

if __name__ == "__main__":
    # Inicia a Web em um processo separado
    web_process = Process(target=start_web)
    web_process.start()

    # Inicia o Bot no loop principal
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        web_process.terminate()
        logger.info("Sistema encerrado pelo usuário.")