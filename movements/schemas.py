from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class MovementBase(BaseModel):
    quantity:int = Field(..., gt=0, title="Quantidade Movimentada")
    movement_type: Literal["IN", "OUT"] = Field(..., title="Tipo (IN = Entrada, OUT = Saída)")

class MovementCreate(MovementBase):
    product_id: int = Field(..., title="ID do Produto")
    location_id: int = Field(..., title="ID do Local (Prateleira)")

class MovementResponse(MovementBase):
    id: int
    product_id: int
    location_id: int
    created_at: datetime

    model_config = {"from_attributes": True}