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
    
    

# Listar horarios (opcionalmente filtrado por course_id)
@course_schedule_routes.route("/api/course-schedules", methods=["GET"])
def list_course_schedules():
    course_id = request.args.get("course_id", type=int)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if course_id:
            cursor.execute(
                """
                SELECT id, course_id, day, schedule, classroom
                FROM course_schedules
                WHERE course_id = %s
                ORDER BY
                  CASE day
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                    ELSE 8
                  END,
                  schedule
                """,
                (course_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, course_id, day, schedule, classroom
                FROM course_schedules
                ORDER BY course_id,
                  CASE day
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                    ELSE 8
                  END,
                  schedule
                """
            )

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "id": r[0],
                "course_id": r[1],
                "day": r[2],
                "schedule": r[3],
                "classroom": r[4],
            }
            for r in rows
        ]
        return jsonify(data), 200

    except Exception as e:
        print("❌ Error al listar horarios:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Actualizar un horario (requiere todos los campos, como en create)
@course_schedule_routes.route("/api/course-schedules/<int:schedule_id>", methods=["PUT"])
def update_course_schedule(schedule_id):
    data = request.json
    course_id = data.get("course_id")
    day = data.get("day")
    schedule = data.get("schedule")
    classroom = data.get("classroom")

    if not course_id or not day or not schedule or not classroom:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE course_schedules
            SET course_id = %s, day = %s, schedule = %s, classroom = %s
            WHERE id = %s
            """,
            (course_id, day, schedule, classroom, schedule_id),
        )
        updated = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if updated == 0:
            return jsonify({"success": False, "message": "Horario no encontrado"}), 404

        return jsonify({"success": True, "message": "Horario actualizado correctamente"}), 200

    except Exception as e:
        print("❌ Error al actualizar horario:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Eliminar un horario
@course_schedule_routes.route("/api/course-schedules/<int:schedule_id>", methods=["DELETE"])
def delete_course_schedule(schedule_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_schedules WHERE id = %s", (schedule_id,))
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if deleted == 0:
            return jsonify({"success": False, "message": "Horario no encontrado"}), 404

        return jsonify({"success": True, "message": "Horario eliminado correctamente"}), 200

    except Exception as e:
        print("❌ Error al eliminar horario:", e)
        return jsonify({"success": False, "error": str(e)}), 500
