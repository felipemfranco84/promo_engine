from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class PromoItem(BaseModel):
    """
    Docstring: Modelo unificado para representar uma oferta.
    Garante que dados de diferentes fontes (Telegram, API, Web) 
    sejam normalizados antes de chegarem ao seu painel ou grupo.
    """
    id: str = Field(..., description="Hash MD5 do link ou ID único da mensagem")
    titulo: str
    preco: Optional[float] = None
    link: str
    loja: Optional[str] = "Não identificada"
    fonte: str  # Ex: 'Telegram - Gafanhoto'
    data_postagem: datetime = Field(default_factory=datetime.now)
    cupom: Optional[str] = None
    imagem_url: Optional[str] = None
    
    class Config:
        from_attributes = True