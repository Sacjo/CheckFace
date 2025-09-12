from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from detection.yoloface import detect_faces
from recognition.face_recognizer import recognize_faces_from_crops, load_embeddings

# Cargar embeddings al inicio
load_embeddings()

recognition_routes = Blueprint("recognition_routes", __name__)

@recognition_routes.route("/api/recognize", methods=["POST"])
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No se proporcionó imagen"}), 400

    image = request.files['image']

    try:
        np_img = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Imagen inválida")

        # 1. Detectar rostros con YOLO
        boxes = detect_faces(img)
        if not boxes:
            return jsonify([]), 200

        # 2. Recortar los rostros
        cropped_faces = []
        for (x, y, w, h) in boxes:
            cropped = img[y:y+h, x:x+w]
            cropped_faces.append(cropped)

        # 3. Reconocer cada rostro recortado
        results = recognize_faces_from_crops(cropped_faces)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar la imagen: {str(e)}"}), 500