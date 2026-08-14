from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Base, engine
from products import crud, schemas, models

from locations import crud as location_crud
from locations import schemas as location_schemas
from locations import models as location_models

from inventory import crud as inventory_crud
from inventory import schemas as inventory_schemas
from inventory import models as inventory_models

from movements import crud as movement_crud
from movements import schemas as movement_schemas
from movements import models as movement_models
from movements import services as movement_services

location_models.Base.metadata.create_all(bind=engine)
inventory_models.Base.metadata.create_all(bind=engine)
movement_models.Base.metadata.create_all(bind=engine)


# --- SISTEMA DE SEGURANÇA ---
CHAVE_MESTRA = "wms-secreto-2024" # Em um sistema real, isso ficaria no arquivo .env
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verificar_permissao(api_key: str = Security(api_key_header)):
    if api_key != CHAVE_MESTRA:
        raise HTTPException(status_code=403, detail="Acesso Negado: Chave Inválida")
    return api_key



app = FastAPI(
    title="WMS ERP System",
    description="API para gestão de armazém e estoque",
    version="1.0.0"
)

# ENDPOINTS
# ROTA DE PRODUTOS


@app.post("/products/", response_model=schemas.ProductResponse, status_code=201, dependencies=[Depends(verificar_permissao)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Cria um novo produto no catalogo do WMS (Requer API Key)"""
    produto_existente = crud.get_product_by_sku(db, sku=product.sku)
    if produto_existente:
        raise HTTPException(status_code=400, detail="SKU já cadastrado no sistema.")
    return crud.create_product(db=db, product=product)



@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna a lista de produtos com paginação"""
    produtos = crud.get_products(db, skip=skip, limit=limit)
    return produtos


@app.get("/products/{sku}", response_model=schemas.ProductResponse)
def read_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Busca um único produto usando o Código de Barras (SKU)"""
    db_product = crud.get_product_by_sku(db, sku=sku)
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
        
    return db_product



@app.put("/products/{sku}", response_model=schemas.ProductResponse, dependencies=[Depends(verificar_permissao)])
def update_product(sku: str, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Atualiza os dados de um produto existente (Requer API Key)"""
    db_product = crud.update_product(db=db, sku=sku, product_data=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado para atualização.")
    return db_product



@app.delete("/products/{sku}", status_code=204, dependencies=[Depends(verificar_permissao)])
def delete_product(sku: str, db: Session = Depends(get_db)):
    """Remove um produto do catálogo do WMS (Requer API Key)"""
    sucesso = crud.delete_product(db=db, sku=sku)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Produto não encontrado para exclusão.")
    return None


# ROTAS DE LOCAIS DE ARMAZENAGEM (Prateleiras, Corredores, etc.)

@app.post("/locations/", response_model=location_schemas.LocationResponse, status_code=201, dependencies=[Depends(verificar_permissao)])
def create_location(location: location_schemas.LocationCreate, db: Session = Depends(get_db)):
    """Cadastra uma nova prateleira/corredor no WMS (Requer API Key)"""
    db_location = location_crud.get_location_by_code(db, code=location.code)
    if db_location:
        raise HTTPException(status_code=400, detail="Código de prateleira já cadastrado no sistema.")
    return location_crud.create_location(db=db, location=location)


@app.get("/locations/", response_model=List[location_schemas.LocationResponse])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os locais de armazenagem cadastrados"""
    return location_crud.get_locations(db, skip=skip, limit=limit)


@app.get("/locations/{code}", response_model=location_schemas.LocationResponse)
def read_location_by_code(code: str, db: Session = Depends(get_db)):
    """Busca os detalhes de uma prateleira específica pelo código"""
    db_location = location_crud.get_location_by_code(db, code=code)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Local de armazenagem não encontrado.")
    return db_location


@app.delete("/locations/{code}", status_code=204, dependencies=[Depends(verificar_permissao)])
def delete_location(code: str, db: Session = Depends(get_db)):
    """Desativa uma prateleira (Soft Delete) (Requer API Key)"""
    sucesso = location_crud.delete_location(db=db, code=code)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Local não encontrado para exclusão.")
    return None
    

# ROTAS DE ESTOQUE (Armazenagem física)

@app.post("/inventory/", response_model=inventory_schemas.InventoryResponse, status_code=201, dependencies=[Depends(verificar_permissao)])
def create_inventory(inventory: inventory_schemas.InventoryCreate, db: Session = Depends(get_db)):
    """Adiciona um produto a uma preteleira pela primeira vez (Requer API Key)"""
    db_inventory = inventory_crud.get_inventory_by_product_and_location(
        db, product_id=inventory.product_id, location_id=inventory.location_id
    )
    if db_inventory:
        raise HTTPException(
            status_code=400,
            detail="Este produto já possui um registro nesta prateleira. Atualize a quantidade existente"
        )
    try:
        return inventory_crud.create_inventory(db=db, inventory=inventory)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Erro de Integridade: O ID do Produto ou o ID do Local não existem no banco de dados."
        )
    

@app.get("/inventory/product/{product_id}", response_model=List[inventory_schemas.InventoryResponse])
def read_inventory_bu_product(product_id: int, db: Session = Depends(get_db)):
    """Descobre em quais prateleiras um produto específico está guardado"""
    return inventory_crud.get_inventory_by_product(db, product_id=product_id)


@app.get("/inventory/location/{location_id}", response_model=List[inventory_schemas.InventoryResponse])
def read_inventory_by_location(location_id: int, db: Session = Depends(get_db)):
    """Descobre todos os produtos guardados em uma prateleira específica"""
    return inventory_crud.get_inventory_by_location(db, location_id=location_id)

# ROTAS MOVEMENTS 

#POST com verificação em services
@app.post("/movements/", response_model=movement_schemas.MovementResponse, status_code=201, dependencies=[Depends(verificar_permissao)])
def create_movement(movement: movement_schemas.MovementCreate, db: Session = Depends(get_db)):
    """Registra uma entrada (IN) ou saída (OUT) e atualiza o saldo do Estoque automaticamente (Requer API Key)"""
    try:
        return movement_services.execute_movement(db=db, movement=movement)
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"ERRO REAL DO BANCO: {str(e)}"
        )

@app.get("/movements/", response_model=List[movement_schemas.MovementResponse])
def read_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna o histórico geral da fábrica (com paginação)"""
    return movement_crud.get_all_movements(db, skip=skip, limit=limit)


@app.get("/movements/product/{product_id}", response_model=List[movement_schemas.MovementResponse])
def read_movements_by_product(product_id: int, db: Session = Depends(get_db)):
    """Retorna todo o histórico de entradas e saídas de um produto específico"""
    return movement_crud.get_movements_by_product(db, product_id=product_id)