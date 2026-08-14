import os
import psycopg2
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

def testar_conexao():
    try:
        print("Iniciando conexão com o banco WMS...")
        
        # 2. Estabelece a conexão usando as variáveis de ambiente
        conexao = psycopg2.connect(
            host=os.getenv("DB_HOST"), # O Python vai ler isso e trocar por 'localhost'
            port=os.getenv("DB_PORT"), # Vai trocar por '5432'
            database=os.getenv("DB_NAME"), # Vai trocar por 'wms_erp_db'
            user=os.getenv("DB_USER"), # Vai trocar por 'admin_wms'
            password=os.getenv("DB_PASS") # Vai trocar pela sua senha real
        )
        
        cursor = conexao.cursor()
        print("✅ Conexão bem-sucedida ao PostgreSQL!\n")
        
        # 3. Executa um SELECT na tabela que criamos
        print("Buscando produtos no estoque...")
        cursor.execute("SELECT id, sku, name, price FROM products;")
        produtos = cursor.fetchall()
        
        # 4. Exibe os resultados formatados
        print("-" * 50)
        for prod in produtos:
            print(f"ID: {prod[0]} | SKU: {prod[1]} | Produto: {prod[2]} | Preço: R${prod[3]}")
        print("-" * 50)
        
        # 5. Fecha as portas de conexão por segurança
        cursor.close()
        conexao.close()
        print("\nConexão encerrada com sucesso.")

    except Exception as e:
        print(f"❌ Erro ao conectar no banco de dados:\n{e}")

if __name__ == "__main__":
    testar_conexao()