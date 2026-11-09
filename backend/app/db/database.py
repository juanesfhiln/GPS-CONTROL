
import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Cargar las variables del archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Construir la dirección de conexión
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
    query={
        "sslmode": os.getenv("DB_SSLMODE", "prefer")
    }
)

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Crear sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Clase base para los modelos
class Base(DeclarativeBase):
    pass


# Función para comprobar la conexión
def probar_conexion():
    with engine.connect() as conexion:
        resultado = conexion.execute(text("SELECT 1"))
        print("Conexión exitosa:", resultado.scalar())
