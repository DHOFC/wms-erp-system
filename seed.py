import requests
import random
import time

# O nosso robô vai conversar com a nossa API
API_URL = "http://127.0.0.1:8000"

# Um catálogo realista de produtos de TI
produtos = [
    {"sku": "LAP-01", "name": "Notebook Dell Inspiron", "description": "15 polegadas, 16GB RAM", "price": 4500.00},
    {"sku": "LAP-02", "name": "MacBook Air M2", "description": "Apple Silicon, 8GB RAM", "price": 7500.00},
    {"sku": "MON-01", "name": "Monitor LG UltraWide", "description": "29 polegadas, 75Hz", "price": 1200.00},
    {"sku": "MON-02", "name": "Monitor Dell Ultrasharp", "description": "27 polegadas, 4K", "price": 3200.00},
    {"sku": "TEC-01", "name": "Teclado Mecânico Keychron", "description": "Switch Brown, sem fio", "price": 650.00},
    {"sku": "MOU-01", "name": "Mouse Logitech MX Master 3S", "description": "Mouse ergonômico", "price": 550.00},
    {"sku": "CAD-01", "name": "Cadeira Herman Miller Aeron", "description": "Ergonômica Preta", "price": 8500.00},
    {"sku": "CAB-01", "name": "Cabo HDMI 2.1", "description": "2 metros, trançado", "price": 45.00},
    {"sku": "HUB-01", "name": "Hub USB-C Baseus", "description": "7 em 1 com rede e HDMI", "price": 180.00},
    {"sku": "SSD-01", "name": "SSD NVMe Kingston 1TB", "description": "Leitura 3500MB/s", "price": 420.00},
]

# Prateleiras de um galpão logístico organizado
prateleiras = [
    {"code": "COR-A-01", "description": "Corredor A, Nível 1 - Pesados"},
    {"code": "COR-A-02", "description": "Corredor A, Nível 2 - Pesados"},
    {"code": "COR-B-01", "description": "Corredor B, Nível 1 - Eletrônicos"},
    {"code": "COR-B-02", "description": "Corredor B, Nível 2 - Eletrônicos"},
    {"code": "COFRE-01", "description": "Sala Cofre - Alto Valor"},
]

print("🚀 Iniciando o Robô de Enriquecimento (Seeding)...")

# 1. Cadastrando os Produtos
print("\n📦 1/3: Cadastrando Produtos...")
for p in produtos:
    res = requests.post(f"{API_URL}/products/", json=p)
    if res.status_code in [200, 201]:
        print(f"  ✅ {p['sku']} cadastrado com sucesso.")
    else:
        print(f"  ⚠️ {p['sku']} ignorado (Provavelmente já existe).")

# 2. Cadastrando as Prateleiras
print("\n🏗️ 2/3: Cadastrando Prateleiras...")
for loc in prateleiras:
    res = requests.post(f"{API_URL}/locations/", json=loc)
    if res.status_code in [200, 201]:
        print(f"  ✅ Prateleira {loc['code']} cadastrada.")
    else:
        print(f"  ⚠️ Prateleira {loc['code']} ignorada.")

# 3. Gerando Movimentações de Estoque (Entradas)
print("\n⚙️ 3/3: Gerando Entradas de Estoque Aleatórias...")
# O robô vai na API descobrir quais IDs foram gerados no banco
prod_res = requests.get(f"{API_URL}/products/").json()
loc_res = requests.get(f"{API_URL}/locations/").json()

if isinstance(prod_res, list) and isinstance(loc_res, list) and len(prod_res) > 0 and len(loc_res) > 0:
    for _ in range(30): # Vai gerar 30 movimentações simuladas
        p_id = random.choice(prod_res)["id"]
        l_id = random.choice(loc_res)["id"]
        qtd = random.randint(10, 100) # Recebendo entre 10 e 100 caixas
        
        payload = {
            "product_id": p_id,
            "location_id": l_id,
            "quantity": qtd,
            "movement_type": "IN"
        }
        res = requests.post(f"{API_URL}/movements/", json=payload)
        if res.status_code == 201:
            print(f"  📥 +{qtd} unidades do Produto ID {p_id} guardadas na Prateleira {l_id}")
        time.sleep(0.05) # Pausa milissegundos para não sobrecarregar a API
else:
    print("  ❌ Não foi possível carregar os produtos ou prateleiras do banco.")

print("\n🎉 Seeding Concluído! O seu WMS agora tem uma operação real rolando!")