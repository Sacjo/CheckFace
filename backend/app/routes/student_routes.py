# backend/app/routes/student_routes.py
import os
import shutil
from flask import Blueprint, request, jsonify
from database.db import get_connection
from werkzeug.utils import secure_filename
from train_faces import entrenar

student_routes = Blueprint('student', __name__)

# Directorios base
RAW_DIR   = os.path.join(os.getcwd(), 'backend', 'app', 'recognition', 'raw_faces')
KNOWN_DIR = os.path.join(os.getcwd(), 'backend', 'app', 'recognition', 'known_faces')
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
@student_routes.route('/api/students', methods=['POST'])
def register_student():
    name   = request.form.get('name')
    images = request.files.getlist('images')  # múltiples

    if not name or not images:
        return jsonify({"error": "Nombre e imágenes son obligatorios"}), 400

    # Inserta alumno
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("INSERT INTO students (name) VALUES (%s) RETURNING id", (name,))
    student_id = cur.fetchone()[0]
    conn.commit()
    cur.close(); conn.close()

    # Guarda fotos en raw_faces/<nombre_seguro>/
    safe_name = _safe_name(name)
    dst_dir   = _student_dir_raw(safe_name)
    os.makedirs(dst_dir, exist_ok=True)

    start_idx = _count_photos_in_raw(safe_name) + 1
    for i, img in enumerate(images, start=start_idx):
        fn = f"{i}_{secure_filename(img.filename)}"
        img.save(os.path.join(dst_dir, fn))

    # Reentrena (recorta + embeddings)
    try:
        entrenar()
    except Exception as e:
        print("⚠️ Error entrenando:", e)

    return jsonify({
        "message": "Estudiante registrado y modelo reentrenado",
        "id": student_id,
        "photos_saved_in": f"raw_faces/{safe_name}/"
    }), 201


# GET /api/students  (lista simple)
@student_routes.route('/api/students', methods=['GET'])
def list_students():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT id, name FROM students ORDER BY id")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows]), 200
    except Exception as e:
        print("⚠️ Error list_students:", e)
        return jsonify({"error": str(e)}), 500


# GET /api/students/summary  (id, nombre, última asistencia, #fotos)
@student_routes.route('/api/students/summary', methods=['GET'])
def list_students_summary():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT s.id, s.name, MAX(a.timestamp) AS last_att
            FROM students s
            LEFT JOIN attendance a ON a.student_id = s.id
            GROUP BY s.id, s.name
            ORDER BY s.id
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()

        out = []
        for sid, name, last_att in rows:
            out.append({
                "id": sid,
                "name": name,
                "last_attendance": last_att.isoformat() if last_att else None,
                "photo_count": _count_photos_in_raw(name)
            })
        return jsonify(out), 200
    except Exception as e:
        print("⚠️ Error list_students_summary:", e)
        return jsonify({"error": str(e)}), 500


# PUT /api/students/<id>  (editar nombre y/o agregar fotos)
@student_routes.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        new_name = request.form.get('name')  # opcional
        images   = request.files.getlist('images')  # opcional

        # nombre actual
        current_name = _get_student_name_by_id(student_id)
        if not current_name:
            return jsonify({"error": "Estudiante no encontrado"}), 404

        # Renombrar en BD y en disco si cambia nombre
        if new_name and new_name != current_name:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("UPDATE students SET name = %s WHERE id = %s", (new_name, student_id))
            conn.commit()
            cur.close(); conn.close()

            old_raw, old_known = _student_dir_raw(current_name), _student_dir_known(current_name)
            new_raw, new_known = _student_dir_raw(new_name), _student_dir_known(new_name)

            if os.path.isdir(old_raw):
                os.makedirs(os.path.dirname(new_raw), exist_ok=True)
                shutil.move(old_raw, new_raw)
            if os.path.isdir(old_known):
                os.makedirs(os.path.dirname(new_known), exist_ok=True)
                shutil.move(old_known, new_known)

            current_name = new_name  # para guardar fotos con el nombre nuevo

        # Agregar nuevas fotos (si vienen)
        if images:
            dst_dir = _student_dir_raw(current_name)
            os.makedirs(dst_dir, exist_ok=True)
            start_idx = _count_photos_in_raw(current_name) + 1
            for i, img in enumerate(images, start=start_idx):
                fn = f"{i}_{secure_filename(img.filename)}"
                img.save(os.path.join(dst_dir, fn))

            # Reentrenar porque hay fotos nuevas
            try:
                entrenar()
            except Exception as e:
                print("⚠️ Error entrenando:", e)

        return jsonify({"success": True}), 200

    except Exception as e:
        print("⚠️ Error update_student:", e)
        return jsonify({"error": str(e)}), 500


# DELETE /api/students/<id>  (borra BD + carpetas raw/known + reentrena)
@student_routes.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        # Obtén el nombre para borrar carpetas
        name = _get_student_name_by_id(student_id)
        if not name:
            return jsonify({"error": "Estudiante no encontrado"}), 404

        # Borra asistencia y alumno
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM attendance WHERE student_id = %s", (student_id,))
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        cur.close(); conn.close()

        # Borra carpetas en disco
        shutil.rmtree(_student_dir_raw(name),   ignore_errors=True)
        shutil.rmtree(_student_dir_known(name), ignore_errors=True)

        # Reentrenar para actualizar embeddings
        try:
            entrenar()
        except Exception as e:
            print("⚠️ Error entrenando:", e)

        return jsonify({"success": True}), 200
    except Exception as e:
        print("⚠️ Error delete_student:", e)
        return jsonify({"error": str(e)}), 500
