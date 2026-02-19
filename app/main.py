import logging
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import SessionLocal, PromoModel

# Configuração de Logs conforme diretriz do Arquiteto
logger = logging.getLogger("WebPanel")

# Inicialização do FastAPI com root_path para compatibilidade com Nginx
# O root_path garante que todas as URLs geradas pelo FastAPI prefixem /promo_engine
app = FastAPI(
    title="PromoEngine Dashboard",
    description="Painel de controle para monitoramento de ofertas e promoções.",
    version="3.2.0",
    root_path="/promo_engine"
)

# Configuração dos templates Jinja2
# Certifique-se de que a pasta 'app/templates' existe no diretório do projeto
try:
    templates = Jinja2Templates(directory="app/templates")
    logger.info("Templates Jinja2 carregados com sucesso.")
except Exception as e:
    logger.error(f"Erro ao carregar diretório de templates: {e}")

# Injeção de Dependência para Sessão de Banco de Dados (SOLID)
def get_db():
    """
    Motivo: Gerenciar o ciclo de vida da conexão com o banco de dados,
    garantindo que a sessão seja fechada após cada requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Docstring: Renderiza o dashboard principal.
    A busca utiliza order_by para exibir as promoções mais recentes primeiro.
    """
    try:
        # Busca as últimas 50 promoções no SQLite
        promocoes = db.query(PromoModel).order_by(PromoModel.data_criacao.desc()).limit(50).all()
        
        logger.debug(f"Dashboard acessado via Proxy. {len(promocoes)} registros encontrados.")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "promocoes": promocoes,
            "status_worker": "Ativo"
        })
    except Exception as e:
        logger.error(f"Erro ao renderizar dashboard: {e}", exc_info=True)
        return {"error": "Falha interna ao carregar o painel. Verifique os logs do servidor."}

@app.get("/health")
def health_check():
    """
    Motivo: Endpoint para monitoramento de disponibilidade (Health Check) 
    útil para configurações de Uptime do Google Cloud.
    """
    return {
        "status": "online",
        "version": "3.2.0",
        "context": "GCP Instance behind Nginx"
    }