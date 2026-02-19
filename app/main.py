import logging
import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import SessionLocal, PromoModel, ConfigModel
from fastapi.responses import RedirectResponse

logger = logging.getLogger("WebDashboard")
app = FastAPI(title="PromoEngine V11")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/")
async def index(request: Request, q: str = None, db: Session = Depends(get_db)):
    """Dashboard com busca."""
    query = db.query(PromoModel)
    if q:
        query = query.filter(PromoModel.titulo.contains(q))
    promos = query.order_by(PromoModel.data_captura.desc()).limit(50).all()
    return templates.TemplateResponse("index.html", {"request": request, "promos": promos, "query": q})

@app.get("/admin")
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    config = db.query(ConfigModel).first() or ConfigModel(id="global")
    return templates.TemplateResponse("admin.html", {"request": request, "config": config})

@app.post("/admin/save")
async def save_configs(keywords: str = Form(...), channels: str = Form(...), db: Session = Depends(get_db)):
    config = db.query(ConfigModel).first()
    config.keywords, config.channels = keywords.lower(), channels.lower().replace(" ", "")
    db.commit()
    return RedirectResponse(url="/promo_engine/admin", status_code=303)

@app.get("/logs")
async def view_logs(request: Request):
    """Lê as últimas 100 linhas do log do motor."""
    log_path = "logs/engine.log"
    content = "Arquivo de log não encontrado."
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            content = "".join(f.readlines()[-100:])
    return templates.TemplateResponse("logs.html", {"request": request, "content": content})