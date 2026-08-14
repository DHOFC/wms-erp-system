from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LocationBase(BaseModel):
    
    code: str = Field(..., title="Código do local", min_length=3, max_length=20)
    description: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


    # model_config: É a chave mágica do Pydantic V2.
    # "from_attributes": True ensina o Pydantic a ler o objeto do SQLAlchemy diretamente.
    model_config = {"from_attributes": True}