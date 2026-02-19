import logging
from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from config import settings

logger = logging.getLogger("DatabaseModule")

# Padrão SQLAlchemy 2.0 para eliminar Warnings
Base = declarative_base()

class PromoModel(Base):
    __tablename__ = "promotions"
    id = Column(String, primary_key=True)
    titulo = Column(String)
    preco = Column(Float)
    link = Column(String)
    fonte = Column(String)
    data_captura = Column(DateTime, default=datetime.utcnow)

class ConfigModel(Base):
    __tablename__ = "system_configs"
    id = Column(String, primary_key=True, default="global")
    keywords = Column(String, default="iphone,celular,cupom,monitor,cerveja")
    channels = Column(String, default="gafanhotopromocoes,pelando,cupomonline")

# Bloco try/except com verificação de atributo
try:
    # Verificação forçada do atributo DATABASE_URL
    db_url = getattr(settings, 'DATABASE_URL', "sqlite:///./promo_engine.db")
    
    engine = create_engine(
        db_url, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info(f"Engine configurada com: {db_url}")
except Exception as e:
    logger.error(f"Erro fatal ao configurar Engine: {e}")
    raise

def init_db():
    """Cria as tabelas se não existirem."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas inicializadas com sucesso (v7.2.2).")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    init_db()