from sqlalchemy.orm import Session
from . import models, schemas


def create_movement(db: Session, movement: schemas.MovementCreate):
    """Grava uma nova entrada ou saída no histórico do armazém"""
    db_movement = models.Movement(**movement.model_dump())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement


def get_all_movements(db: Session, skip: int = 0, limit: int = 100):
    """Retorna o histórico de toda a fábrica, do mais recente para o mais antigo"""
    return (
        db.query(models.Movement)
        .order_by(models.Movement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_movements_by_product(db: Session, product_id: int):
    """Retorna o histórico de entradas e saídas de um único produto"""
    return (
        db.query(models.Movement)
        .filter(models.Movement.product_id == product_id)
        .order_by(models.Movement.created_at.desc())
        .all()
    )