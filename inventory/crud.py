from sqlalchemy.orm import Session
from . import models, schemas

def get_inventory_by_product_and_location(db: Session, product_id: int, location_id: int):
    """Busca se um produto específico já existe em uma prateleira específica"""
    return db.query(models.Inventory).filter(
        models.Inventory.product_id == product_id,
        models.Inventory.location_id == location_id
    ).first()


def get_inventory_by_product(db: Session, product_id: int):
    """Retorna todas as prateleiras onde um determinado produto está guardado"""
    return db.query(models.Inventory).filter(models.Inventory.product_id == product_id).all()

def get_inventory_by_location(db: Session, location_id: int):
    """Retorna todos os produtos que estão guardados em uma prateleira específica"""
    return db.query(models.Inventory).filter(models.Inventory.location_id == location_id).all()

def create_inventory(db: Session, inventory: schemas.InventoryCreate):
    """Registra um produto em uma prateleira pela primeira vez"""
    db_inventory = models.Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory_quantity(db: Session, inventory_id: int, new_quantity: int):
    """Atualiza a quantidade de caixas de um registro existente"""
    db_inventory = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if db_inventory:
        db_inventory.quantity = new_quantity
        db.commit()
        db.refresh(db_inventory)
    return db_inventory

