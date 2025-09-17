import os
import json
import numpy as np
from deepface import DeepFace
import tempfile
import cv2
from recognition.helpers import l2_normalize, cosine_distance

# Ruta al índice de centroides generado en train_faces.py
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), "embeddings")
CENTROIDS_PATH = os.path.join(EMBEDDINGS_DIR, "centroids.json")

# -----------------------------
# Cargar centroides
# -----------------------------
def load_centroids(path=CENTROIDS_PATH):
    if not os.path.exists(path):
        print("⚠️ No existe centroids.json. Ejecutá primero train_faces.py")
        return {}

    with open(path, "r") as f:
        data = json.load(f)

    # Convertir cada centroide a np.array normalizado
    centroids = {person: l2_normalize(np.array(info["centroid"], dtype=np.float32))
                 for person, info in data.items()}

    print(f"✅ Centroides cargados: {list(centroids.keys())}")
    return centroids


# -----------------------------
# Reconocer un rostro
# -----------------------------
def recognize_face(face_crop, centroids: dict, model_name="ArcFace"):
    """
    face_crop: imagen BGR (ej. 160x160) de un rostro ya recortado.
    centroids: dict {persona: np.array(512,)} cargado con load_centroids()
    Retorna: (identity, min_dist, similarity)
    """
    # Guardar temporalmente para que DeepFace lea la imagen
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        cv2.imwrite(tmp.name, face_crop)
        rep = DeepFace.represent(
            img_path=tmp.name,
            model_name=model_name,
            enforce_detection=False,
            detector_backend="skip"
        )[0]
    os.remove(tmp.name)

    q = l2_normalize(np.array(rep["embedding"], dtype=np.float32))

    # Buscar el centroide más cercano
    min_dist = float("inf")
    identity = "Desconocido"
    for name, c in centroids.items():
        d = cosine_distance(q, c)
        if d < min_dist:
            min_dist = d
            identity = name

    # Similaridad: inversa de la distancia coseno (0 a 100 aprox)
    similarity = max(0, 100 - min_dist * 100)

    # Umbral → si min_dist es muy alto, marcar como desconocido
    if min_dist > 0.45:  # ajustable según tus pruebas
        identity = "Desconocido"
        similarity = 0

    return identity, float(min_dist), round(similarity, 2)

# -----------------------------
# Reconocer múltiples rostros
# -----------------------------
def recognize_faces_from_crops(cropped_faces, centroids: dict):
    results = []
    for crop in cropped_faces:
        identity, min_dist, similarity = recognize_face(crop, centroids)
        results.append({
            "name": identity,
            "min_dist": round(min_dist, 3),
            "similarity": similarity,
            "match": identity != "Desconocido"
        })
    return results