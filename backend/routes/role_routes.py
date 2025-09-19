from flask import Blueprint, request, jsonify
from database.db import get_connection

role_routes = Blueprint("role_routes", __name__)

# Crear un rol
@role_routes.route("/api/roles", methods=["POST"])
def create_role():
    data = request.json
    description = data.get("description")

    if not description:
        return jsonify({"success": False, "message": "Descripción requerida"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO roles (description) VALUES (%s) RETURNING id", (description,))
        role_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "id": role_id, "message": "Rol creado"}), 201

    except Exception as e:
        print("❌ Error al crear rol:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Obtener todos los roles
@role_routes.route("/api/roles", methods=["GET"])
def get_roles():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, description FROM roles ORDER BY id ASC")
        rows = cursor.fetchall()

        roles = [{"id": row[0], "description": row[1]} for row in rows]

        cursor.close()
        conn.close()

        return jsonify(roles), 200

    except Exception as e:
        print("❌ Error al obtener roles:", e)
        return jsonify({"error": str(e)}), 500


# Obtener un rol por ID
@role_routes.route("/api/roles/<int:role_id>", methods=["GET"])
def get_role(role_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, description FROM roles WHERE id = %s", (role_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return jsonify({"id": row[0], "description": row[1]}), 200
        else:
            return jsonify({"error": "Rol no encontrado"}), 404

    except Exception as e:
        print("❌ Error al obtener rol:", e)
        return jsonify({"error": str(e)}), 500


# Actualizar un rol
@role_routes.route("/api/roles/<int:role_id>", methods=["PUT"])
def update_role(role_id):
    data = request.json
    description = data.get("description")

    if not description:
        return jsonify({"success": False, "message": "Descripción requerida"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE roles SET description = %s WHERE id = %s RETURNING id", (description, role_id))
        updated = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if updated:
            return jsonify({"success": True, "message": "Rol actualizado"}), 200
        else:
            return jsonify({"success": False, "message": "Rol no encontrado"}), 404

    except Exception as e:
        print("❌ Error al actualizar rol:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# Eliminar un rol
@role_routes.route("/api/roles/<int:role_id>", methods=["DELETE"])
def delete_role(role_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM roles WHERE id = %s RETURNING id", (role_id,))
        deleted = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if deleted:
            return jsonify({"success": True, "message": "Rol eliminado"}), 200
        else:
            return jsonify({"success": False, "message": "Rol no encontrado"}), 404

    except Exception as e:
        print("❌ Error al eliminar rol:", e)
        return jsonify({"success": False, "error": str(e)}), 500