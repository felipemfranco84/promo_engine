import logging
from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from config import settings

logger = logging.getLogger("DatabaseModule")

# Padrão SQLAlchemy 2.0
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

# Conexão protegida por bloco try/except conforme diretriz
try:
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Engine de banco de dados configurada.")
except Exception as e:
    logger.error(f"Erro ao conectar ao banco de dados: {e}")
    raise

def init_db():
    """Cria as tabelas se não existirem."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados (re)inicializadas.")
    except Exception as e:
        logger.error(f"Falha na criação das tabelas: {e}")

if __name__ == "__main__":
    init_db()