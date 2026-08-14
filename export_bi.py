import requests
import csv

API_BASE_URL = "http://127.0.0.1:8000"

def extrair_endpoint_para_csv(endpoint, nome_arquivo):
    print(f"Buscando dados de /{endpoint}/...")
    try:
        # Faz uma requisição GET na nossa própria API
        resposta = requests.get(f"{API_BASE_URL}/{endpoint}/")
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            if len(dados) == 0:
                print(f"  ⚠️ O endpoint /{endpoint}/ está vazio.")
                return
                
            # Extrai o nome das colunas automaticamente da primeira linha do JSON
            colunas = dados[0].keys()
            
            # Salva no arquivo CSV
            with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas, delimiter=';')
                escritor.writeheader()
                escritor.writerows(dados)
                
            print(f"  ✅ Salvo com sucesso: {nome_arquivo}")
        else:
            print(f"  ❌ Erro da API: Status {resposta.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Erro: A API não está rodando. Ligue o uvicorn primeiro!")
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando Extrator de Dados (API -> CSV)...\n")
    
    extrair_endpoint_para_csv("products", "bi_produtos.csv")
    extrair_endpoint_para_csv("locations", "bi_prateleiras.csv")
    extrair_endpoint_para_csv("movements", "bi_movimentacoes.csv")
    
    print("\n🎉 Extração concluída! Seus arquivos estão prontos para o Power BI.")