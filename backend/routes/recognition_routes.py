from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from recognition.face_recognizer import recognize_face_embedding, load_embeddings

# Cargar embeddings al registrar el Blueprint
load_embeddings()

recognition_routes = Blueprint("recognition_routes", __name__)

@recognition_routes.route("/api/recognize", methods=["POST"])
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No se proporcionó imagen"}), 400

    image = request.files['image']

    try:
        # Convertir imagen a OpenCV
        np_img = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Imagen inválida")

        name, similarity = recognize_face_embedding(img)

        return jsonify({
            "name": name,
            "match": name != "Desconocido",
            "similarity": round(similarity, 2)
        })

    except Exception as e:
        return jsonify({"error": f"Error al procesar la imagen: {str(e)}"}), 500