from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 1. Base: Propriedades comuns a todos os Schemas de Produto
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50, description="Código único do produto")
    name: str = Field(..., min_length=3, max_length=100, description="Nome do produto")
    description: Optional[str] = None

    price: float = Field(..., gt=0, description="Preço unitário em reais") # Validação igual ao database 

# 2. Schema de Criação (O que o usuário envia via POST)
# Herda tudo do Base. Não pedimos o ID, pois o banco quem gera.
class ProductCreate(ProductBase):
    pass

# 3. Schema de Resposta (O que nós devolvemos para o usuário via GET)
class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pydantic v2: Isso permite que o Pydantic leia dados direto de um Objeto SQLAlchemy
        from_attributes = True