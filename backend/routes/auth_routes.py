from flask import Blueprint, request, jsonify
from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash

auth_routes = Blueprint('auth_routes', __name__)

# 🔑 Login
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role_id FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[2], password):
        return jsonify({"message": "Login successful", "user": {"id": user[0], "username": user[1], "role_id": user[3]}})
    return jsonify({"error": "Invalid credentials"}), 401


# 🆕 Registro externo (crear usuario inicial)
@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id', 1)  # por defecto rol 1 (ej: estudiante)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s) RETURNING id",
                (username, hashed_pw, role_id))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "User created successfully", "id": new_id}), 201
