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