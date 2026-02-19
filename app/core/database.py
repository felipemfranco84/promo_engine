import logging
from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from config import settings

logger = logging.getLogger("DatabaseModule")

# Padrão SQLAlchemy 2.0 para evitar Warnings
Base = declarative_base()

class PromoModel(Base):
    """Representa a tabela de promoções capturadas."""
    __tablename__ = "promotions"
    id = Column(String, primary_key=True)
    titulo = Column(String)
    preco = Column(Float)
    link = Column(String)
    fonte = Column(String)
    data_captura = Column(DateTime, default=datetime.utcnow)

class ConfigModel(Base):
    """Representa a tabela de configurações web (Filtros e Canais)."""
    __tablename__ = "system_configs"
    id = Column(String, primary_key=True, default="global")
    keywords = Column(String, default="iphone,celular,cupom,monitor,cerveja")
    channels = Column(String, default="gafanhotopromocoes,pelando,cupomonline")

# Bloco try/except conforme padrão Arquiteto Python
try:
    # Verificação defensiva antes de instanciar a engine
    if not hasattr(settings, 'DATABASE_URL'):
        raise AttributeError("A configuração 'DATABASE_URL' não foi encontrada no objeto settings.")
        
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Conexão com SQLite preparada.")
except Exception as e:
    logger.error(f"Erro fatal ao configurar Engine: {e}")
    raise

def init_db():
    """Inicializa as tabelas no arquivo .db."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas inicializadas com sucesso (v7.2.1).")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    init_db()