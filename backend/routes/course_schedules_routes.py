from flask import Blueprint, request, jsonify
from database.db import get_connection

course_schedule_routes = Blueprint("course_schedule_routes", __name__)

# Crear un horario para un curso
@course_schedule_routes.route("/api/course-schedules", methods=["POST"])
def create_course_schedule():
    data = request.json
    course_id = data.get("course_id")
    day = data.get("day")
    schedule = data.get("schedule")  # formato esperado: "08:00 - 10:00"
    classroom = data.get("classroom")

    if not course_id or not day or not schedule or not classroom:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO course_schedules (course_id, day, schedule, classroom)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (course_id, day, schedule, classroom))
        schedule_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "id": schedule_id, "message": "Horario creado correctamente"}), 201

    except Exception as e:
        print("❌ Error al crear horario:", e)
        return jsonify({"success": False, "error": str(e)}), 500