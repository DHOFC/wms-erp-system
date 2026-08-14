from sqlalchemy.orm import Session
from fastapi import HTTPException

# O nosso Gerente(Services) precisa conversar com todos os departamentos:
from movements import crud as movement_crud
from movements import schemas as movement_schemas
from inventory import crud as inventory_crud
from inventory import schemas as inventory_schemas
from locations import models as location_models

def execute_movement(db: Session, movement: movement_schemas.MovementCreate):
    """
    Orquestra a regra de negócio completa: 
    Valida a prateleira, calcula o saldo, atualiza o estoque e grava o histórico.
    """

    location = db.query(location_models.Location).filter(location_models.Location.id == movement.location_id).first()

    if not location:
        raise HTTPException(status_code=404, detail="Prateleira não encontrada")
    
    if not location.is_active:
        raise HTTPException(
            status_code=400,
            detail="Operação negada: Esta prateleira está desativada por motivos de manutenção ou bloqueio."
        )

    # DESCOBRIENDO O SALDO ATUAL

    inventory_record = inventory_crud.get_inventory_by_product_and_location(
        db, product_id=movement.product_id, location_id=movement.location_id
    )

    current_qty = inventory_record.quantity if inventory_record else 0

    if movement.movement_type =="IN":
        new_qty = current_qty + movement.quantity
    elif movement.movement_type == "OUT":
        if current_qty < movement.quantity:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")
        new_qty = current_qty - movement.quantity

    # SALVANDO NO DATABASE

    if inventory_record:
        inventory_crud.update_inventory_quantity(db, inventory_id=inventory_record.id, new_quantity=new_qty)
    else:
        new_inv = inventory_schemas.InventoryCreate(
            product_id=movement.product_id,
            location_id=movement.location_id,
            quantity=new_qty
        )
        inventory_crud.create_inventory(db, new_inv)

    return movement_crud.create_movement(db, movement)
