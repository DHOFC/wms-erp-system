# 📦 WMS Enterprise System (Warehouse Management System)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-1.0+-009688.svg?logo=fastapi&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-UI-ff69b4.svg?logo=flutter&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1.svg?logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7.svg?logo=render&logoColor=white)
![PowerBI](https://img.shields.io/badge/Power_BI-Analytics-F2C811.svg?logo=powerbi&logoColor=black)

Um sistema completo de Gestão de Armazéns (WMS) focado em performance, segurança e análise de dados. Desenvolvido com uma arquitetura moderna, separando completamente o Front-end (Flet Web) do Back-end (FastAPI) e hospedado 100% na Nuvem.

---

## 🌐 Demonstração ao Vivo (Live Demo)

Acesse o sistema completo rodando em produção na nuvem:

* 🖥️ **Dashboard & Interface Web:** [https://wms-erp-dashboard.onrender.com](https://wms-erp-dashboard.onrender.com)
* ⚡ **API Restful (Documentação Swagger):** [https://wms-erp-system.onrender.com/docs](https://wms-erp-system.onrender.com/docs)

---

## 🚀 Principais Funcionalidades

*   **📊 Executive Dashboard (Tempo Real):** Painel interativo e responsivo (Mobile-First) com KPIs financeiros e operacionais. Atualização assíncrona (Background Threads) sem travar a interface.
*   **🏭 Terminal de Operação:** Registro de entradas e saídas (IN/OUT) com cálculo dinâmico de valor de estoque físico real.
*   **🛡️ Segurança Nível API (RBAC):** Proteção de rotas sensíveis (Criação, Atualização e Exclusão) utilizando validação por **API Key Header** (`X-API-Key`). Modos de Leitura (Público) e Escrita (Restrito).
*   **📱 Design Responsivo:** Interface reativa construída com `ResponsiveRow`, ajustando os gráficos e cards automaticamente para telas de computador e smartphones.
*   **📈 Pipeline de Dados (ETL):** Robô extrator integrado que consome a própria API para gerar relatórios `.csv` formatados e prontos para consumo em ferramentas de Business Intelligence (Power BI).

---

## 🏗️ Arquitetura do Sistema

O sistema foi desenhado com foco em escalabilidade e microsserviços na nuvem:

1.  **Back-end (FastAPI):** Lógica de negócios, schemas Pydantic e ORM SQLAlchemy hospedados no Render Web Service.
2.  **Database (PostgreSQL):** Banco de dados relacional hospedado em ambiente gerenciado na nuvem.
3.  **Front-end (Flet Web App):** Aplicação executável compilada para a Web, rodando assincronamente e consumindo a API REST.
4.  **Data Analytics:** Script de automação (`povoar_nuvem.py` e `export_bi.py`) para geração de massa de dados e extração tabular para Power BI.

---

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior.

### Passo 1: Configuração do Back-end (API)
```bash
# Clone o repositório
git clone [https://github.com/DHOFC/wms-erp-system.git](https://github.com/DHOFC/wms-erp-system.git)
cd wms-erp-system

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor FastAPI localmente
uvicorn main:app --reload
