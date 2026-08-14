from sqlalchemy.orm import Session
from . import models, schemas

def get_location_by_code(db: Session, code: str):
    """Busca um local pelo seu código único"""
    return db.query(models.Location).filter(models.Location.code == code).first()


def get_locations(db: Session, skip: int = 0, limit = 100):
    """Retorna uma lista de locais cadastrados"""
    return db.query(models.Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: schemas.LocationCreate):
    """Cria um novo local de armazenagem"""
    db_location = models.Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def update_location(db: Session, code: str, location_data: schemas.LocationCreate):
    """Atualiza a descrição ou código de um local existente"""
    db_location = get_location_by_code(db, code=code)
    if not db_location:
        return None

    update_data = location_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_location, key, value)
        
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, code: str):
    """Desativa um local em vez de excluí-lo fisicamente (Soft Delete)"""
    db_location = get_location_by_code(db, code=code)
    if not db_location:
        return False

    db_location.is_active = False

    db.commit()
    return True
