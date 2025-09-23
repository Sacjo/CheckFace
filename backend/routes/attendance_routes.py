from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime

attendance_routes = Blueprint("attendance_routes", __name__)

@attendance_routes.route("/api/asistencia", methods=["POST"])
def registrar_asistencia():
    data = request.json
    names = data.get("names", [])
    course_id = data.get("course_id")

    if not names or not course_id:
        return jsonify({"success": False, "message": "Nombres y course_id requeridos"}), 400

    try:

        data = request.get_json()
        print("📥 Recibido en backend:", data)

        conn = get_connection()
        cursor = conn.cursor()

        for name in names:
            # Buscar usuario por nombre
            cursor.execute("SELECT id FROM users WHERE ci = %s", (name,))
            user = cursor.fetchone()
            if not user:
                print(f"⚠️ Usuario no encontrado: {name}")
                continue

            user_id = user[0]

            # Validar pertenencia al curso
            cursor.execute(
                "SELECT 1 FROM user_courses WHERE user_id = %s AND course_id = %s",
                (user_id, course_id)
            )
            if not cursor.fetchone():
                print(f"⚠️ Usuario {name} no pertenece al curso {course_id}")
                continue

            # Registrar asistencia
            cursor.execute(
                "INSERT INTO attendances (user_id, course_id, date) VALUES (%s, %s, NOW())",
                (user_id, course_id)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Asistencias registradas"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@attendance_routes.route("/api/asistencias", methods=["GET"])
def obtener_asistencias():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.name, a.timestamp
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.timestamp DESC
        """)
        rows = cursor.fetchall()

        asistencias = [{"name": row[0], "timestamp": row[1].isoformat()} for row in rows]

        cursor.close()
        conn.close()

        return jsonify(asistencias), 200

    except Exception as e:
        print("❌ Error al obtener asistencias:", e)
        return jsonify({"error": str(e)}), 500


@attendance_routes.route("/api/asistencias/resumen", methods=["GET"])
def resumen_asistencias():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DATE(timestamp) AS fecha, COUNT(*) AS cantidad
            FROM attendance
            GROUP BY DATE(timestamp)
            ORDER BY fecha DESC
        """)
        rows = cursor.fetchall()

        resultados = [{"fecha": str(row[0]), "cantidad": row[1]} for row in rows]

        cursor.close()
        conn.close()
        return jsonify(resultados), 200

    except Exception as e:
        print("Error en resumen_asistencias:", e)
        return jsonify({"error": str(e)}), 500
