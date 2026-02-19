import logging
import os
from pydantic_settings import BaseSettings
from typing import List

# Docstring: Garante a infraestrutura de logs antes da carga de configs.
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
    Docstring: Esquema de configurações do sistema.
    O motivo desta lógica existir é centralizar o acesso a variáveis de ambiente
    e parâmetros globais do banco de dados e Telegram.
    """
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    MY_PRIVATE_GROUP_ID: int
    
    # Campo obrigatório para persistência - DEVE ESTAR AQUI
    DATABASE_URL: str = "sqlite:///./promo_engine.db"
    
    TARGET_CHANNELS: List[str] = ["gafanhotopromocoes", "pelando", "cupomonline"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

try:
    settings = Settings()
    logger.info("Configurações validadas e carregadas.")
except Exception as e:
    logger.error(f"Falha crítica na validação das configurações: {e}")
    raise