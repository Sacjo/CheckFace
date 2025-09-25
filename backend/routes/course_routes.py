import datetime
from flask import Blueprint, request, jsonify
from database.db import get_connection

course_routes = Blueprint("course_routes", __name__)

# Crear un curso
@course_routes.route("/api/courses", methods=["POST"])
def create_course():
    data = request.json
    name = data.get("name")
    career = data.get("career")
    semester = data.get("semester")

    if not name or not career or semester is None:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO courses (name, career, semester)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (name, career, semester))
        course_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "id": course_id, "message": "Curso creado"}), 201

    except Exception as e:
        print("❌ Error al crear curso:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Obtener todos los cursos
@course_routes.route("/api/courses", methods=["GET"])
def get_courses():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, career, semester FROM courses ORDER BY id ASC")
        rows = cursor.fetchall()

        courses = [
            {"id": row[0], "name": row[1], "career": row[2], "semester": row[3]}
            for row in rows
        ]

        cursor.close()
        conn.close()

        return jsonify(courses), 200

    except Exception as e:
        print("❌ Error al obtener cursos:", e)
        return jsonify({"error": str(e)}), 500


# Obtener un curso por ID
@course_routes.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, career, semester FROM courses WHERE id = %s", (course_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return jsonify({
                "id": row[0], "name": row[1], "career": row[2], "semester": row[3]
            }), 200
        else:
            return jsonify({"error": "Curso no encontrado"}), 404

    except Exception as e:
        print("❌ Error al obtener curso:", e)
        return jsonify({"error": str(e)}), 500


# Actualizar un curso
@course_routes.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.json
    name = data.get("name")
    career = data.get("career")
    semester = data.get("semester")

    if not name or not career or semester is None:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE courses
            SET name = %s, career = %s, semester = %s
            WHERE id = %s RETURNING id
        """, (name, career, semester, course_id))
        updated = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if updated:
            return jsonify({"success": True, "message": "Curso actualizado"}), 200
        else:
            return jsonify({"success": False, "message": "Curso no encontrado"}), 404

    except Exception as e:
        print("❌ Error al actualizar curso:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Eliminar un curso
@course_routes.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM courses WHERE id = %s RETURNING id", (course_id,))
        deleted = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if deleted:
            return jsonify({"success": True, "message": "Curso eliminado"}), 200
        else:
            return jsonify({"success": False, "message": "Curso no encontrado"}), 404

    except Exception as e:
        print("❌ Error al eliminar curso:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@course_routes.route("/api/current_course", methods=["GET"])
def get_current_course():
    try:
        # 🔹 Obtener día y hora actual
        now = datetime.datetime.now()
        print("🕒 Hora actual:", now)

        current_day = now.strftime("%A")  # Ejemplo: 'Monday'
        current_time = now.strftime("%H:%M")

        # 🔹 Si tu DB guarda días en español, hacer mapeo:
        dias_map = {
            "Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday",
            "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday", "Sunday": "Sunday",
            
        }
        current_day_db = dias_map[current_day]

        conn = get_connection()
        cur = conn.cursor()

        # 🔹 Buscar curso cuyo horario cubra este rango
        cur.execute("""
            SELECT cs.id, cs.course_id, c.name, c.career, c.semester, cs.day, cs.schedule, cs.classroom
            FROM course_schedules cs
            JOIN courses c ON cs.course_id = c.id
            WHERE cs.day = %s
              AND %s::time BETWEEN split_part(cs.schedule, ' - ', 1)::time
                              AND split_part(cs.schedule, ' - ', 2)::time
        """, (current_day_db, current_time))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"message": "⚠️ No hay curso activo en este momento"}), 404

        return jsonify({
            "schedule_id": row[0],
            "course_id": row[1],
            "name": row[2],
            "career": row[3],
            "semester": row[4],
            "day": row[5],
            "schedule": row[6],
            "classroom": row[7]
        }), 200

    except Exception as e:
        print("❌ Error en /api/current_course:", e)
        return jsonify({"error": str(e)}), 500