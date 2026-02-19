import logging
from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from core.database import SessionLocal, PromoModel, ConfigModel
from fastapi.responses import RedirectResponse

logger = logging.getLogger("WebDashboard")

app = FastAPI(title="PromoEngine Dashboard")

# Configurações de Template e Estáticos
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Dependência do Banco de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    """Lista todas as promoções salvas no banco."""
    promos = db.query(PromoModel).order_by(PromoModel.data_captura.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "promos": promos})

@app.get("/admin")
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    """Carrega o painel de configuração de filtros e canais."""
    config = db.query(ConfigModel).filter(ConfigModel.id == "global").first()
    if not config:
        config = ConfigModel(id="global")
        db.add(config)
        db.commit()
        db.refresh(config)
    return templates.TemplateResponse("admin.html", {"request": request, "config": config})

@app.post("/admin/save")
async def save_configs(
    keywords: str = Form(...), 
    channels: str = Form(...), 
    db: Session = Depends(get_db)
):
    """Salva as novas configurações enviadas pela web."""
    try:
        config = db.query(ConfigModel).filter(ConfigModel.id == "global").first()
        config.keywords = keywords.lower().strip()
        config.channels = channels.lower().replace("@", "").replace(" ", "").strip()
        db.commit()
        logger.info("Configurações atualizadas via Painel Web.")
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        logger.error(f"Falha ao salvar configurações: {e}")
        db.rollback()
        return {"error": "Falha ao salvar"}