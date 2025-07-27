# backend/app/routes/student_routes.py
import os
from flask import Blueprint, request, jsonify
from database.db import get_connection
from werkzeug.utils import secure_filename   # <<-- import necesario
from train_faces import entrenar


student_routes = Blueprint('student', __name__)

# Carpeta base donde se guardarán las fotos
UPLOAD_DIR = os.path.join(
    os.getcwd(), 'backend', 'app', 'recognition', 'raw_faces'
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@student_routes.route('/api/students', methods=['POST'])
def register_student():
    # 1. Recoge datos
    name    = request.form.get('name')
    images  = request.files.getlist('images')   # varias imágenes

    if not name or not images:
        return jsonify({"error": "Nombre e imágenes son obligatorios"}), 400

    # 2. Inserta en BD
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO students (name) VALUES (%s) RETURNING id",
        (name,)
    )
    student_id = cur.fetchone()[0]
    conn.commit()

    # 3. Crea subcarpeta con el nombre del estudiante
    safe_name   = secure_filename(name)
    student_dir = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(student_dir, exist_ok=True)

    # 4. Guarda cada foto dentro de raw_faces/<nombre>/
    for idx, img in enumerate(images, start=1):
        # limpieza de nombre de fichero original
        original_fn = secure_filename(img.filename)
        save_name   = f"{idx}_{original_fn}"
        save_path   = os.path.join(student_dir, save_name)
        img.save(save_path)

    cur.close()
    conn.close()
    
    entrenar()

    return jsonify({
        "message": "Estudiante registrado y Modelo entrenado",
        "id": student_id,
        "photos_saved_in": f"raw_faces/{safe_name}/"
    }), 201
