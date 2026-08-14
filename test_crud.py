from database import SessionLocal
from products import crud, schemas
import random

def testar_operador_crud():
    print("🚜 Iniciando Teste de Integração do Operador CRUD...\n")
    
    # 1. Abre a sessão (Pega a chave do cofre)
    db = SessionLocal()
    
    try:
        # 2. Criamos o DTO Validado
        # Dica de Sênior: Usamos um SKU aleatório para que o banco de dados 
        # não bloqueie o teste por "SKU Duplicado" se rodarmos o script várias vezes.
        sku_teste = f"TESTE-{random.randint(1000, 9999)}"
        
        caixa_aprovada = schemas.ProductCreate(
            sku=sku_teste,
            name="Engrenagem de Teste Automatizado",
            description="Peça criada pelo script test_crud.py",
            price=45.99
        )
        
        print(f"▶️ PASSO 1: Mandando o CRUD criar o produto (SKU: {sku_teste})...")
        # 3. A Injeção de Dependência: Entregamos a conexão (db) e os dados (caixa_aprovada)
        produto_criado = crud.create_product(db=db, product=caixa_aprovada)
        
        print(f"✅ SUCESSO: Produto salvo! O Banco gerou o ID físico: {produto_criado.id}")
        
        print(f"\n▶️ PASSO 2: Mandando o CRUD buscar o produto na prateleira...")
        # 4. Validamos se a função de leitura também funciona
        produto_buscado = crud.get_product_by_sku(db=db, sku=sku_teste)
        
        if produto_buscado:
            print(f"✅ SUCESSO: O CRUD encontrou a '{produto_buscado.name}' perfeitamente!")
            print(f"   Preço registrado no banco: R${produto_buscado.price}")
        else:
            print("❌ FALHA: O produto foi salvo, mas o CRUD não conseguiu achá-lo.")
            
    except Exception as e:
        print(f"❌ OCORREU UM ERRO GRAVE NO BANCO DE DADOS: {e}")
        # Se algo explodir, nós desfazemos a transação para não corromper o banco
        db.rollback()
        
    finally:
        # 5. Sempre devolvemos a chave do cofre
        db.close()
        print("\nSessão do banco fechada com segurança.")

if __name__ == "__main__":
    testar_operador_crud()