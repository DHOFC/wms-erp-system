import requests
import random
import time

# O endereço da SUA API na Nuvem
API_URL = "https://wms-erp-system.onrender.com"
HEADERS = {"X-API-Key": "wms-secreto-2024"}

produtos_iniciais = [
    {"name": "Motor Industrial V8", "sku": "MTR-880", "description": "Motor de alta potência CNC", "price": 12400.00},
    {"name": "Empilhadeira Elétrica 2T", "sku": "EQP-001", "description": "Equipamento pesado de pátio", "price": 45000.00},
    {"name": "Palete de Madeira Padrão PBR", "sku": "MAT-102", "description": "Lote com 50 unidades", "price": 1250.50},
    {"name": "Caixa de Engrenagens Aço", "sku": "MEC-045", "description": "Peça de reposição linha C", "price": 850.75},
    {"name": "Bobina de Aço Inox 500kg", "sku": "MAT-205", "description": "Matéria prima bruta", "price": 3200.00},
    {"name": "Painel Solar 400W Monocristalino", "sku": "ELE-991", "description": "Módulo fotovoltaico", "price": 1100.00},
    {"name": "Inversor de Frequência 50Hz", "sku": "ELE-442", "description": "Equipamento elétrico de controle", "price": 2300.00},
    {"name": "Tambor Óleo Lubrificante 200L", "sku": "QUI-011", "description": "Tambor industrial lacrado", "price": 1800.00},
]

locais_iniciais = [
    {"code": "A-01", "description": "Setor de Pesados - Corredor A (Chão)"},
    {"code": "A-02", "description": "Setor de Pesados - Corredor A (Rack)"},
    {"code": "B-01", "description": "Setor de Elétricos - Corredor B"},
    {"code": "C-01", "description": "Setor Químico - Área Isolada (Gaiola)"},
    {"code": "D-01", "description": "Recebimento / Triagem Doca Principal"},
]

print("🚀 Iniciando a injeção de dados na NUVEM...")

# 1. Injetar Produtos
print("\n📦 Cadastrando Produtos...")
for p in produtos_iniciais:
    res = requests.post(f"{API_URL}/products/", json=p, headers=HEADERS)
    if res.status_code == 201:
        print(f"  [+] {p['name']} inserido!")

# 2. Injetar Locais (Prateleiras)
print("\n🏢 Cadastrando Prateleiras...")
for l in locais_iniciais:
    res = requests.post(f"{API_URL}/locations/", json=l, headers=HEADERS)
    if res.status_code == 201:
        print(f"  [+] Local {l['code']} inserido!")

# 3. Buscar os IDs reais gerados pelo Banco de Dados da Nuvem
print("\n🔄 Sincronizando IDs do Banco de Dados...")
req_prod = requests.get(f"{API_URL}/products/").json()
req_loc = requests.get(f"{API_URL}/locations/").json()

ids_produtos = [p["id"] for p in req_prod]
ids_locais = [l["id"] for l in req_loc]

# 4. Gerar Movimentações Aleatórias (Simulando uma semana de trabalho)
if ids_produtos and ids_locais:
    print("\n🚚 Gerando Histórico de Operações (Empilhadeira)...")
    
    # Vamos gerar 25 entradas (IN) de estoque para dar volume financeiro
    for i in range(25):
        payload = {
            "product_id": random.choice(ids_produtos),
            "location_id": random.choice(ids_locais),
            "quantity": random.randint(5, 50),
            "movement_type": "IN"
        }
        requests.post(f"{API_URL}/movements/", json=payload, headers=HEADERS)
        print(f"  [IN] Lote de mercadoria recebido e guardado.")
        time.sleep(0.1) # Pausa dramática para a API respirar

    # E algumas saídas (OUT) para simular vendas/despachos
    for i in range(8):
        payload = {
            "product_id": random.choice(ids_produtos),
            "location_id": random.choice(ids_locais),
            "quantity": random.randint(1, 4),
            "movement_type": "OUT"
        }
        requests.post(f"{API_URL}/movements/", json=payload, headers=HEADERS)
        print(f"  [OUT] Mercadoria despachada.")

print("\n🎯 SUCESSO! Banco de dados populado com sucesso.")
print("🌐 Abra o seu Dashboard na internet e veja a mágica!")