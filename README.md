# 📦 WMS Enterprise System (Warehouse Management System)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-1.0+-009688.svg?logo=fastapi&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-UI-ff69b4.svg?logo=flutter&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?logo=sqlite&logoColor=white)
![PowerBI](https://img.shields.io/badge/Power_BI-Analytics-F2C811.svg?logo=powerbi&logoColor=black)

Um sistema completo de Gestão de Armazéns (WMS) focado em performance, segurança e análise de dados. Este projeto foi desenvolvido com uma arquitetura moderna, separando completamente o Front-end (Flet) do Back-end (FastAPI), comunicando-se exclusivamente via API RESTful com autenticação.

---

## 🚀 Principais Funcionalidades

*   **📊 Executive Dashboard (Tempo Real):** Painel interativo com KPIs financeiros e operacionais. Atualização assíncrona (Background Threads) sem travar a interface do usuário.
*   **🏭 Terminal de Operação:** Registro de entradas e saídas (IN/OUT) com cálculo dinâmico de valor de estoque físico real.
*   **🛡️ Segurança Nível API (RBAC):** Proteção de rotas sensíveis (Criação, Atualização e Exclusão) utilizando validação por **API Key Header**. Modos de Leitura (Público) e Escrita (Restrito).
*   **📈 Pipeline de Dados (ETL):** Robô extrator integrado que consome a própria API para gerar relatórios `.csv` formatados e prontos para consumo em ferramentas de Business Intelligence (Power BI).

---

## 🏗️ Arquitetura do Sistema

O sistema foi desenhado com foco em escalabilidade:

1.  **Back-end:** Construído com `FastAPI` e `SQLAlchemy` (ORM), garantindo documentação automática (Swagger) e validação de dados rígida via Pydantic.
2.  **Front-end:** Construído com `Flet` (baseado em Flutter), gerando uma interface Desktop/Web fluida, responsiva e com gráficos nativos (ECharts style).
3.  **Data Analytics:** Script `export_bi.py` que atua como um microsserviço de Engenharia de Dados, transformando JSON em dados tabulares para o Power BI.

---

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior.

### Passo 1: Configuração do Back-end (API)
```bash
# Clone o repositório
git clone [https://github.com/DHOFC/wms-erp-system.git](https://github.com/SEU_USUARIO/wms-erp-system.git)
cd wms-erp-system

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor FastAPI
uvicorn main:app --reload