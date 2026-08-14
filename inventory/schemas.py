from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class InventoryBase(BaseModel):

    quantity: int = Field(default=0, ge=0, title="Quantidade Físico")

class InventoryCreate(InventoryBase):
    
    product_id: int = Field(..., title="ID do produto")
    location_id: int = Field(..., title="ID do local (Prateleira)")

class InventoryResponse(InventoryBase):

    id: int
    product_id: int
    location_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

