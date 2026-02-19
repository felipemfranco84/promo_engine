import logging
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Logger específico para o módulo de banco de dados
logger = logging.getLogger("DatabaseModule")

Base = declarative_base()

class PromoModel(Base):
    """
    Docstring: Representação física da tabela de promoções.
    O motivo desta lógica existir é garantir a persistência das ofertas
    e permitir a busca histórica via FastAPI.
    """
    __tablename__ = "promotions"

    id = Column(String, primary_key=True, index=True)  # Hash único da oferta
    titulo = Column(String, nullable=False)
    preco = Column(Float, nullable=True)
    link = Column(String, nullable=False)
    loja = Column(String, default="Desconhecida")
    fonte = Column(String, nullable=False)
    cupom = Column(String, nullable=True)
    imagem_url = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

# Configuração do Engine e Sessão
try:
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Necessário para SQLite + FastAPI
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Conexão com SQLite estabelecida com sucesso.")
except Exception as e:
    logger.error(f"Erro ao conectar ao banco de dados: {e}")
    raise

def init_db():
    """
    Docstring: Cria as tabelas no banco de dados se não existirem.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados inicializadas/verificadas.")
    except Exception as e:
        logger.error(f"Falha na inicialização das tabelas: {e}")
        raise