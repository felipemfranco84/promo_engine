import logging
import os
from pydantic_settings import BaseSettings
from typing import List

# Configuração de Log de Depuração (Obrigatório conforme protocolo)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConfigModule")

class Settings(BaseSettings):
    """
    Docstring: Gerencia todas as variáveis sensíveis e constantes do sistema.
    O motivo desta lógica existir é centralizar o estado de configuração e 
    garantir que o sistema não inicie sem as credenciais necessárias.
    """
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    DATABASE_URL: str = "sqlite:///./promo_engine.db"
    
    # Canais para monitorar (Baseado no seu print do Telegram)
    TARGET_CHANNELS: List[str] = [
        "gafanhotopromocoes", 
        "pelando", 
        "cupomonline", 
        "mercadolivre"
    ]
    
    # Grupo de destino (Onde o bot enviará para você)
    MY_PRIVATE_GROUP_ID: int

    class Config:
        env_file = ".env"

try:
    settings = Settings()
    logger.info("Configurações carregadas com sucesso.")
except Exception as e:
    logger.error(f"Erro crítico ao carregar configurações: {e}")
    raise