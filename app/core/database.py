import logging
from sqlalchemy import create_all, Column, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

logger = logging.getLogger("DatabaseModule")

Base = declarative_base()

class PromoModel(Base):
    """
    Docstring: Representa uma oferta capturada.
    O motivo desta lógica existir é garantir a persistência de todas as ofertas
    para consulta histórica via dashboard web.
    """
    __tablename__ = "promotions"

    id = Column(String, primary_key=True)
    titulo = Column(String)
    preco = Column(Float)
    link = Column(String)
    fonte = Column(String)
    data_captura = Column(DateTime, default=datetime.utcnow)

class ConfigModel(Base):
    """
    Docstring: Armazena as configurações dinâmicas do sistema.
    O motivo desta lógica existir é permitir a alteração de filtros (keywords)
    e canais alvo via interface Web, sem necessidade de restart do serviço.
    """
    __tablename__ = "system_configs"

    id = Column(String, primary_key=True, default="global")
    keywords = Column(String, default="iphone,celular,cupom,monitor,cerveja")
    channels = Column(String, default="gafanhotopromocoes,pelando,cupomonline")

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados e tabelas de configuração inicializados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")

if __name__ == "__main__":
    init_db()