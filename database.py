import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente
load_dotenv()

# 2. Resgata as chaves
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 3. Monta a Connection String (URL de Conexão do PostgreSQL)
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 4. Engine: Gerencia o pool de conexões (conexões simultâneas)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 5. SessionLocal: Fábrica de sessões. Cada vez que a API for chamada, ela cria uma sessão isolada
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Base: Classe mãe que nossos modelos (tabelas) vão herdar
Base = declarative_base()

# 7. Dependência para injeção no FastAPI (usaremos mais para frente)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()