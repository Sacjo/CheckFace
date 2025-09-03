from flask import Blueprint, request, jsonify
from database.db import get_connection

attendance_routes = Blueprint("attendance_routes", __name__)

@attendance_routes.route("/api/asistencia", methods=["POST"])
def registrar_asistencia():
    data = request.json
    nombre = data.get("name")

    if not nombre:
        return jsonify({"success": False, "message": "Nombre requerido"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el estudiante ya existe
        cursor.execute("SELECT id FROM students WHERE name = %s", (nombre,))
        row = cursor.fetchone()

        if row:
            student_id = row[0]
        else:
            # Insertar nuevo estudiante
            cursor.execute("INSERT INTO students (name) VALUES (%s) RETURNING id", (nombre,))
            student_id = cursor.fetchone()[0]

        # Registrar asistencia
        cursor.execute("INSERT INTO attendance (student_id) VALUES (%s)", (student_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Asistencia registrada"}), 200

    except Exception as e:
        print("Error al registrar asistencia:", e)
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
