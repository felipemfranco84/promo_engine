import logging
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import SessionLocal, PromoModel

logger = logging.getLogger("WebPanel")
app = FastAPI(title="PromoEngine Dashboard")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Interface visual para auditoria das capturas em tempo real.
    """
    try:
        # Busca as últimas 50 promoções (corrigido para order_by)
        promocoes = db.query(PromoModel).order_by(PromoModel.data_criacao.desc()).limit(50).all()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "promocoes": promocoes,
            "status_worker": "Ativo"
        })
    except Exception as e:
        logger.error(f"Erro ao renderizar dashboard: {e}", exc_info=True)
        return {"error": "Falha interna no painel."}

@app.get("/health")
def health_check():
    return {"status": "online", "version": "3.1.0"}