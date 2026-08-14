from pydantic import ValidationError
from products.schemas import ProductCreate
import json

def testar_validacoes_pydantic():
    print("🛡️ Iniciando Testes de Segurança e Validação (Pydantic)...\n")

    # ---------------------------------------------------------
    # TESTE 1: O Caminho Feliz (Dados corretos)
    # ---------------------------------------------------------
    print("▶️ TESTE 1: Inserindo dados válidos...")
    try:
        # Simulando o JSON que chegou da internet
        produto_valido = ProductCreate(
            sku="PRD-099",
            name="Sensor de Proximidade",
            description="Sensor indutivo 24V",
            price=350.75
        )
        print("✅ SUCESSO: O Pydantic aprovou os dados!")
        # .model_dump() converte o Objeto Pydantic de volta para um Dicionário Python limpo
        print(f"Dados limpos gerados: {produto_valido.model_dump()}\n")
    except ValidationError as e:
        print(f"❌ FALHA INESPERADA: {e}\n")

    # ---------------------------------------------------------
    # TESTE 2: Ataque/Erro - Preço Negativo
    # ---------------------------------------------------------
    print("▶️ TESTE 2: Tentando inserir preço negativo (R$ -10.00)...")
    try:
        produto_invalido_preco = ProductCreate(
            sku="PRD-100",
            name="Cabo de Aço",
            price=-10.00
        )
        print("❌ FALHA DE SEGURANÇA: O Pydantic deixou o erro passar!")
    except ValidationError as e:
        print("✅ SUCESSO DO SISTEMA: Pydantic bloqueou o preço negativo.")
        # Extraindo apenas a mensagem de erro formatada
        erros = json.loads(e.json())
        print(f"Motivo bloqueado: {erros[0]['msg']} (Campo: {erros[0]['loc']})\n")

    # ---------------------------------------------------------
    # TESTE 3: Ataque/Erro - Nome muito curto
    # ---------------------------------------------------------
    print("▶️ TESTE 3: Tentando inserir nome com apenas 2 letras ('Fio')...")
    try:
        produto_invalido_nome = ProductCreate(
            sku="PRD-101",
            name="Fi", # Intencionalmente menor que o min_length=3
            price=5.00
        )
        print("❌ FALHA DE SEGURANÇA: O Pydantic deixou o erro passar!")
    except ValidationError as e:
        print("✅ SUCESSO DO SISTEMA: Pydantic bloqueou o nome curto.")
        erros = json.loads(e.json())
        print(f"Motivo bloqueado: {erros[0]['msg']} (Campo: {erros[0]['loc']})\n")

if __name__ == "__main__":
    testar_validacoes_pydantic()