from database.db import get_connection

def ejecutar_init_sql():
    with open("database/init.sql", "r") as f:
        sql = f.read()

    try:
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
    ejecutar_init_sql()
