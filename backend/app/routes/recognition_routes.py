from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from backend.app.recognition.face_recognizer import recognize_face_embedding

recognition_routes = Blueprint("recognition_routes", __name__)

@recognition_routes.route("/api/recognize", methods=["POST"])
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No se proporcionó imagen"}), 400

    image = request.files['image']

    # Convertir a imagen OpenCV
    np_img = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Imagen inválida"}), 400

    name, similarity = recognize_face_embedding(img)

    return jsonify({
        "name": name,
        "match": name != "Desconocido",
        "similarity": round(similarity, 2)
    })
