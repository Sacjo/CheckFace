# backend/routes/student_routes.py
import os
import shutil
from flask import Blueprint, request, jsonify
from database.db import get_connection
from werkzeug.utils import secure_filename
from train_faces import entrenar

user_routes = Blueprint("user_routes", __name__)

# GET /api/users → obtener todos los usuarios
@user_routes.route("/api/users", methods=["GET"])
def get_all_users():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.id, u.username, u.role_id, r.description AS role
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.id ASC
        """)

        cur.execute("""
            SELECT p.id, u.username, p.ci
            FROM participants p
            JOIN users u ON p.user_id = u.id
            WHERE NOT EXISTS (
                SELECT 1 FROM attendances a
                WHERE a.participant_id = p.id
            )
        """)
        rows = cur.fetchall()

        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "username": row[1],
                "role_id": row[2],
                "role": row[3]
            })

        cur.close(); conn.close()
        return jsonify(users), 200

    except Exception as e:
        print("❌ Error al obtener usuarios:", e)
        return jsonify({"error": str(e)}), 500


@user_routes.route("/api/users/available", methods=["GET"])
def get_available_users():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Usuarios que no están asociados a ningún participante
        cur.execute("""
            SELECT id, username
            FROM users
            WHERE id NOT IN (SELECT user_id FROM participants)
        """)
        users = [{"id": row[0], "username": row[1]} for row in cur.fetchall()]

        cur.close()
        conn.close()
        return jsonify(users), 200

    except Exception as e:
        print("❌ Error al obtener usuarios disponibles:", e)
        return jsonify({"error": "Error al obtener usuarios disponibles"}), 500

# GET /api/users/<id> → obtener un solo usuario
@user_routes.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.id, u.username, u.role_id, r.description AS role
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """, (user_id,))
        row = cur.fetchone()

        cur.close(); conn.close()

        if row:
            user = {
                "id": row[0],
                "username": row[1],
                "role_id": row[2],
                "role": row[3]
            }
            return jsonify(user), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        print("❌ Error al obtener usuario por ID:", e)
        return jsonify({"error": str(e)}), 500
