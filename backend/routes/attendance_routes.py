from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime

attendance_routes = Blueprint("attendance_routes", __name__)

@attendance_routes.route("/api/asistencia", methods=["POST"])
def registrar_asistencia():
    data = request.get_json()
    cis = data.get("cis", [])
    course_id = data.get("course_id")
    fecha = data.get("date")
    observations = data.get("observations", None)

    if not cis or not course_id or not fecha:
        return jsonify({"success": False, "message": "Nombres, course_id y date requeridos"}), 400

    registrados, no_encontrados, fuera_curso = [], [], []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for ci in cis:
            cursor.execute("SELECT id FROM participants WHERE ci = %s", (ci,))
            user = cursor.fetchone()
            if not user:
                no_encontrados.append(ci)
                continue

            user_id = user[0]

            cursor.execute(
                "SELECT 1 FROM participant_courses WHERE participant_id = %s AND course_id = %s",
                (user_id, course_id)
            )
            if not cursor.fetchone():
                fuera_curso.append(ci)
                continue

            cursor.execute(
                """
                INSERT INTO attendances (participant_id, course_id, date, observations)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT unique_attendance_per_day
                DO UPDATE
                SET observations = EXCLUDED.observations
                """,
                (user_id, course_id, fecha, observations)
            )
            registrados.append(ci)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "registrados": registrados,
            "no_encontrados": no_encontrados,
            "fuera_curso": fuera_curso
        }), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
   
@attendance_routes.route("/api/asistencia-manual", methods=["POST"])
def registrar_asistencia_manual():
    try:
        data = request.get_json()
        print("📥 Recibido en backend:", data)

        participant_id = data.get("user_id")         # ID del participante
        course_id      = data.get("course_id")
        date           = data.get("date")
        observations   = data.get("observations", None)  # opcional

        if not participant_id or not course_id or not date:
            return jsonify({"success": False, "message": "Campos requeridos: user_id, course_id y date"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el participante existe
        cursor.execute("SELECT id FROM participants WHERE id = %s", (participant_id,))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"success": False, "message": "Participante no encontrado"}), 404

        # Verificar si el participante está asignado al curso
        cursor.execute("""
            SELECT 1 FROM participant_courses
            WHERE participant_id = %s AND course_id = %s
        """, (participant_id, course_id))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"success": False, "message": "El participante no está asignado al curso"}), 400

        # Registrar asistencia manual con fecha específica
        cursor.execute("""
            INSERT INTO attendances (participant_id, course_id, date, observations)
            VALUES (%s, %s, %s, %s)
        """, (participant_id, course_id, date, observations))

        conn.commit()
        cursor.close(); conn.close()

        return jsonify({"success": True, "message": "Asistencia manual registrada"}), 201

    except Exception as e:
        print("❌ Error en asistencia manual:", e)
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



@attendance_routes.route("/api/participants/<int:participant_id>/courses", methods=["GET"])
def obtener_cursos_de_participante(participant_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.name, c.semester, c.career
            FROM courses c
            JOIN participant_courses pc ON pc.course_id = c.id
            WHERE pc.participant_id = %s
        """, (participant_id,))

        cursos = cursor.fetchall()
        cursor.close(); conn.close()

        result = []
        for c in cursos:
            result.append({
                "id": c[0],
                "name": c[1],
                "semester": c[2],
                "career": c[3]
            })

        return jsonify(result), 200

    except Exception as e:
        print("❌ Error al obtener cursos del participante:", e)
        return jsonify({"error": str(e)}), 500
    

@attendance_routes.route("/api/asistencia/registrados", methods=["GET"])
def get_asistencias_registradas():
    course_id = request.args.get("course_id")
    fecha = request.args.get("date")

    if not course_id or not fecha:
        return jsonify({"success": False, "message": "course_id y date requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.ci, p.full_name
            FROM attendances a
            JOIN participants p ON a.participant_id = p.id
            WHERE a.course_id = %s AND a.date::date = %s::date
        """, (course_id, fecha))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        registrados = [
            {"id": row[0], "ci": row[1], "full_name": row[2]} for row in rows
        ]

        return jsonify({"success": True, "registrados": registrados}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500