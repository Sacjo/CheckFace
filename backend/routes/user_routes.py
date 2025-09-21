# backend/routes/student_routes.py
import os
import shutil
from flask import Blueprint, request, jsonify
from database.db import get_connection
from werkzeug.utils import secure_filename
from train_faces import entrenar

user_routes = Blueprint("user_routes", __name__)

# Directorios base
RAW_DIR   = os.path.join(os.getcwd(), 'backend', 'recognition', 'raw_faces')
KNOWN_DIR = os.path.join(os.getcwd(), 'backend', 'recognition', 'known_faces')
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(KNOWN_DIR, exist_ok=True)


# =============== Helpers ===============

def _safe_name(name: str) -> str:
    return secure_filename(name or '').strip()

def _student_dir_raw(name: str) -> str:
    return os.path.join(RAW_DIR, _safe_name(name))

def _student_dir_known(name: str) -> str:
    return os.path.join(KNOWN_DIR, _safe_name(name))

def _count_photos_in_raw(name: str) -> int:
    d = _student_dir_raw(name)
    if not os.path.isdir(d):
        return 0
    return sum(f.lower().endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(d))

def _get_student_name_by_id(student_id: int):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT name FROM students WHERE id = %s", (student_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else None


# =============== Endpoints ===============

# POST /api/students  (crear y subir varias imágenes -> raw_faces/<name>/)
@user_routes.route("/api/users", methods=["POST"])
def register_student():
    data = request.form
    name     = data.get("name")
    ci       = data.get("ci")
    email    = data.get("email")
    password = data.get("password")
    role_id  = data.get("role_id")
    course_id = data.get("course_id")
    images   = request.files.getlist("images")


    if not all([name, ci, email, password, role_id, course_id]) or not images:
        return jsonify({"error": "Todos los campos y al menos una imagen son requeridos"}), 400


    conn = get_connection()
    cur = conn.cursor()
    
    # Verifica CI duplicado
    cur.execute("SELECT id FROM users WHERE ci = %s", (ci,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({"error": "CI ya registrado"}), 409

    try:
        # Verifica si el curso existe
        cur.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
        if not cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "Curso no encontrado"}), 404

        # Verifica si el rol existe
        cur.execute("SELECT id FROM roles WHERE id = %s", (role_id,))
        if not cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "Rol no encontrado"}), 404
        
        # Insertar usuario
        cur.execute("""
            INSERT INTO users (name, ci, email, password, role_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (name, ci, email, password, role_id))
        user_id = cur.fetchone()[0]

        # Asignar curso
        cur.execute("""
            INSERT INTO user_courses (user_id, course_id)
            VALUES (%s, %s)
        """, (user_id, course_id))

        conn.commit()
        cur.close(); conn.close()

        # Guardar imágenes en raw_faces/<ci>/
        ci_safe = secure_filename(ci)
        ci_path = os.path.join(RAW_DIR, ci_safe)
        os.makedirs(ci_path, exist_ok=True)

        start_idx = len(os.listdir(ci_path)) + 1
        for i, img in enumerate(images, start=start_idx):
            filename = f"{i}_{secure_filename(img.filename)}"
            img.save(os.path.join(ci_path, filename))

        # Ejecutar entrenamiento
        import subprocess
        subprocess.run(["python", "backend/train_faces.py", ci])

        return jsonify({"success": True, "message": "Usuario registrado y modelo actualizado"}), 201

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500
