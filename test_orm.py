from database import SessionLocal
from products.models import Product

def testar_leitura_orm():
    print("Iniciando conexão via SQLAlchemy ORM...")

    db = SessionLocal() # Cria uma sessão de conexão com o banco

    try:

        print("Buscando produtos")
        produtos_do_banco = db.query(Product).all() # SELECT * FROM products;

        print("-" * 50)
        for prod in produtos_do_banco:
            print(f"ID: {prod.id} | SKU: {prod.sku} | Produto: {prod.name} | Preço: R${prod.price}")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Erro ao conectar no banco de dados via ORM:\n{e}")

    finally:
        db.close() # Fecha a sessão de conexão com o banco
        print("\nConexão encerrada com sucesso.")

if __name__ == "__main__":
    testar_leitura_orm()