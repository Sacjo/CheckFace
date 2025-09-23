# backend/routes/participans_routes.py
from flask import Blueprint, request, jsonify
from database.db import get_connection
import os
from werkzeug.utils import secure_filename
from train_faces import entrenar

participants_routes = Blueprint("participants_routes", __name__)

# Directorios base
RAW_DIR   = os.path.join(os.getcwd(), 'backend', 'recognition', 'raw_faces')
KNOWN_DIR = os.path.join(os.getcwd(), 'backend', 'recognition', 'known_faces')
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(KNOWN_DIR, exist_ok=True)


# POST: Crear nuevo participante
@participants_routes.route("/api/participants", methods=["POST"])
def create_participant():
    data = request.form
    full_name  = data.get("full_name")
    ci         = data.get("ci")
    occupation = data.get("occupation")
    user_id    = data.get("user_id")
    course_id  = data.get("course_id")
    images     = request.files.getlist("images")

    if not all([full_name, ci, occupation, user_id, course_id]) or not images:
        return jsonify({"error": "Todos los campos y al menos una imagen son requeridos"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si CI ya existe en participants
        cur.execute("SELECT id FROM participants WHERE ci = %s", (ci,))
        if cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "CI ya registrado"}), 409

        # Verificar existencia de usuario y curso
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404

        cur.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
        if not cur.fetchone():
            return jsonify({"error": "Curso no encontrado"}), 404

        # Insertar participante
        cur.execute("""
            INSERT INTO participants (full_name, ci, occupation, user_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (full_name, ci, occupation, user_id))
        participant_id = cur.fetchone()[0]

        # Asignar curso
        cur.execute("""
            INSERT INTO participant_courses (participant_id, course_id)
            VALUES (%s, %s)
        """, (participant_id, course_id))

        conn.commit()
        cur.close(); conn.close()

        # Guardar imágenes
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

        return jsonify({
            "success": True,
            "participant_id": participant_id,
            "ci": ci,
            "message": "Participante creado, curso asignado y modelo entrenado"
        }), 201

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500
    

@participants_routes.route("/api/participants", methods=["GET"])
def get_all_participants():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, u.username, p.ci
            FROM participants p
            JOIN users u ON p.user_id = u.id
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        participants = []
        for row in rows:
            participants.append({
                "id": row[0],
                "username": row[1],
                "ci": row[2]
            })

        return jsonify(participants), 200
    except Exception as e:
        print("❌ Error al obtener participantes:", e)
        return jsonify({"error": str(e)}), 500
    

# POST: Asignar un curso a un participante ya existente
@participants_routes.route("/api/participants/<int:participant_id>/assign-course", methods=["POST"])
def assign_course(participant_id):
    data = request.json
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"error": "Se requiere course_id"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si ya tiene asignado ese curso
        cursor.execute("""
            SELECT 1 FROM participant_courses 
            WHERE participant_id = %s AND course_id = %s
        """, (participant_id, course_id))
        if cursor.fetchone():
            return jsonify({"error": "El curso ya está asignado"}), 409

        # Asignar curso
        cursor.execute("""
            INSERT INTO participant_courses (participant_id, course_id)
            VALUES (%s, %s)
        """, (participant_id, course_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Curso asignado correctamente"}), 200

    except Exception as e:
        print("❌ Error al asignar curso:", e)
        return jsonify({"error": str(e)}), 500