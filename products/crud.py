from sqlalchemy.orm import Session
from . import models, schemas

# READ (Leitura)
def get_product_by_sku(db: Session, sku: str):
    """Busca um produto específico pelo Código de Barras (SKU)"""
    return db.query(models.Product).filter(models.Product.sku == sku).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Busca a lista de produtos com paginação (offset/limit)"""
    return db.query(models.Product).offset(skip).limit(limit).all()

    # CREATE (Criação)
def create_product(db: Session, product: schemas.ProductCreate):
    """Cria um novo produto no banco de dados"""
    
    # 1. A MÁGICA DA PONTE: 
    # Pegamos o DTO (Pydantic), extraímos o dicionário com model_dump(),
    # e desempacotamos (** kwargs) para dentro do Modelo do Banco (SQLAlchemy)
    db_product = models.Product(**product.model_dump())
    
    # 2. Adiciona o objeto na "área de preparação" (Staging / Memória)
    db.add(db_product)
    
    # 3. Executa a transação no banco de dados de fato (O INSERT no disco)
    db.commit()
    
    # 4. Atualiza o nosso objeto em memória com os dados gerados pelo banco 
    # (Ex: O banco gerou o 'id' e as datas 'created_at')
    db.refresh(db_product)
    
    return db_product

def update_product(db: Session, sku: str, product_data: schemas.ProductCreate):
    """Atualiza os dados de um produto existente buscando pelo SKU"""
    
    # 1. Busca o produto no banco
    db_product = get_product_by_sku(db, sku=sku)
    if not db_product:
        return None
        
    # 2. Pega os dados novos que vieram do Pydantic e atualiza os atributos do objeto do banco
    update_data = product_data.model_dump()
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    # 3. Salva as alterações no banco de dados
    db.commit()
    db.refresh(db_product)
    
    return db_product

def delete_product(db: Session, sku: str):
    """Remove um produto do banco de dados (DELETE)"""
    
    # 1. Verifica se a caixa está na prateleira
    db_product = get_product_by_sku(db, sku=sku)
    if not db_product:
        return False # Avisa que não achou nada
        
    # 2. Comando de exclusão física do SQLAlchemy
    db.delete(db_product)
    
    # 3. Confirma a destruição no banco
    db.commit()
    return True