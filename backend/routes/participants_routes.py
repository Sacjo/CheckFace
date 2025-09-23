from flask import Blueprint, request, jsonify
from database.db import get_connection

participants_routes = Blueprint("participants_routes", __name__)

# POST: Crear nuevo participante
@participants_routes.route("/api/participants", methods=["POST"])
def create_participant():
    data = request.json
    full_name = data.get("full_name")
    ci = data.get("ci")
    occupation = data.get("occupation")
    user_id = data.get("user_id")

    if not full_name or not ci or not occupation or not user_id:
        return jsonify({"success": False, "message": "Todos los campos son requeridos."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Validar CI único por usuario
        cursor.execute("SELECT id FROM participants WHERE ci = %s", (ci,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "El CI ya está registrado."}), 409

        # Insertar nuevo participante
        cursor.execute("""
            INSERT INTO participants (full_name, ci, occupation, user_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (full_name, ci, occupation, user_id))

        participant_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Participante creado exitosamente.",
            "id": participant_id
        }), 201

    except Exception as e:
        print("❌ Error al crear participante:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# GET: Obtener todos los participantes
@participants_routes.route("/api/participants", methods=["GET"])
def get_participants():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, full_name, ci, occupation, user_id
            FROM participants
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()

        participants = [
            {
                "id": row[0],
                "full_name": row[1],
                "ci": row[2],
                "occupation": row[3],
                "user_id": row[4]
            } for row in rows
        ]

        cursor.close()
        conn.close()

        return jsonify(participants), 200

    except Exception as e:
        print("❌ Error al obtener participantes:", e)
        return jsonify({"error": str(e)}), 500