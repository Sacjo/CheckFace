import json
import numpy as np
from deepface import DeepFace
import tempfile
import cv2
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_PATH = os.path.join(BASE_DIR, "embeddings.json")


# Cargar los embeddings una sola vez al iniciar
try:
    with open(EMBEDDING_PATH, "r") as f:
        embeddings = json.load(f)
except FileNotFoundError:
    print(f"❌ Archivo de embeddings no encontrado en {EMBEDDING_PATH}")
    embeddings = []

def recognize_face_embedding(cropped_face):
    try:
        # Guardar temporalmente la imagen recibida (recorte facial)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name

        cv2.imwrite(temp_path, cropped_face)

        # Obtener embedding del rostro recortado usando ArcFace
        result = DeepFace.represent(img_path=temp_path, model_name="ArcFace", enforce_detection=False)
        os.remove(temp_path)

        if not result or "embedding" not in result[0]:
            return "Desconocido", 0

        rep = np.array(result[0]["embedding"])

        # Comparar con embeddings conocidos
        min_dist = float("inf")
        identity = "Desconocido"

        for entry in embeddings:
            db_vec = np.array(entry["embedding"])
            dist = np.linalg.norm(rep - db_vec)
            if dist < min_dist:
                min_dist = dist
                identity = entry["name"]

        # Convertir la distancia a "porcentaje" de similitud
        similarity = max(0, 100 - min_dist * 18)

        # Umbral para considerar desconocido
        if min_dist > 3.5:
            return "Desconocido", 0

        return identity, similarity

    except Exception as e:
        print("⚠️ Error en reconocimiento:", e)
        return "Desconocido", 0
