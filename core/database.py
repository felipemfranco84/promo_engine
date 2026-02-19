import logging
from sqlalchemy import Column, String, Float, DateTime, create_engine, delete
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger("DatabaseModule")
Base = declarative_base()

class PromoModel(Base):
    """Representação das ofertas capturadas."""
    __tablename__ = "promotions"
    id = Column(String, primary_key=True, index=True)
    titulo = Column(String)
    preco = Column(Float)
    link = Column(String)
    fonte = Column(String)
    data_captura = Column(DateTime, default=datetime.utcnow)

class ConfigModel(Base):
    """Configurações dinâmicas de filtros e canais."""
    __tablename__ = "system_configs"
    id = Column(String, primary_key=True, default="global")
    keywords = Column(String, default="iphone,celular,cupom")
    channels = Column(String, default="gafanhotopromocoes,pelando,cupomonline")

# Configuração de Engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_old_promos(days: int = 7):
    """
    Remove promoções mais antigas que o limite de dias especificado.
    Motivo: Manter a performance do SQLite e do Dashboard Web.
    """
    db = SessionLocal()
    try:
        limit_date = datetime.utcnow() - timedelta(days=days)
        stmt = delete(PromoModel).where(PromoModel.data_captura < limit_date)
        result = db.execute(stmt)
        db.commit()
        if result.rowcount > 0:
            logger.info(f"🧹 Limpeza: {result.rowcount} ofertas antigas removidas do banco.")
    except Exception as e:
        logger.error(f"❌ Erro na limpeza do banco: {e}")
        db.rollback()
    finally:
        db.close()

def init_db():
    """Inicializa tabelas e executa rotina de manutenção."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("🗄️ Tabelas verificadas/inicializadas.")
        cleanup_old_promos() # Roda a limpeza no boot
    except Exception as e:
        logger.error(f"❌ Falha no init_db: {e}")

if __name__ == "__main__":
    init_db()
