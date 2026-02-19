import logging
import os
from pydantic_settings import BaseSettings
from typing import List

# Garante que o diretório de logs exista
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "engine.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConfigModule")

class Settings(BaseSettings):
    """
    Docstring: Centralização de configurações e segredos.
    O motivo desta lógica existir é prover ao sistema acesso às credenciais
    do Telegram e ao caminho do banco de dados SQLite.
    """
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    MY_PRIVATE_GROUP_ID: int
    
    # Atributo que estava faltando:
    DATABASE_URL: str = "sqlite:///./promo_engine.db"
    
    TARGET_CHANNELS: List[str] = ["gafanhotopromocoes", "pelando", "cupomonline"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

try:
    settings = Settings()
    logger.info("Configurações carregadas com sucesso.")
except Exception as e:
    logger.error(f"Erro ao carregar Settings: {e}")
    raise