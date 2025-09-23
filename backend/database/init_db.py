import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .db import get_connection
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def crear_base_si_no_existe():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Base de datos '{DB_NAME}' creada correctamente.")
        else:
            print(f"ℹ️ La base de datos '{DB_NAME}' ya existe.")

        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error al verificar o crear la base de datos:", e)


def ejecutar_init_sql():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "init.sql"), "r") as f:
            sql = f.read()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tablas creadas correctamente.")
    except Exception as e:
        print("❌ Error al ejecutar init.sql:", e)


if __name__ == "__main__":
    crear_base_si_no_existe()
    ejecutar_init_sql()