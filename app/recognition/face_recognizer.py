import json
import numpy as np
from deepface import DeepFace
import tempfile
import cv2
import os

# Ruta del archivo de embeddings generados con train_faces.py
EMBEDDING_PATH = "app/recognition/embeddings.json"

# Cargar los embeddings una sola vez
with open(EMBEDDING_PATH, "r") as f:
    embeddings = json.load(f)

def recognize_face_embedding(cropped_face):
    try:
        # Crear archivo temporal cerrado
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name

        # Guardar el recorte facial como imagen temporal
        cv2.imwrite(temp_path, cropped_face)

        # Obtener el embedding del rostro recortado
        rep = DeepFace.represent(img_path=temp_path, model_name="ArcFace", enforce_detection=False)[0]["embedding"]

        # Eliminar el archivo temporal
        os.remove(temp_path)

        # Comparar con todos los embeddings conocidos
        min_dist = float("inf")
        identity = "Desconocido"

        for entry in embeddings:
            db_vec = np.array(entry["embedding"])
            dist = np.linalg.norm(np.array(rep) - db_vec)
            if dist < min_dist:
                min_dist = dist
                identity = entry["name"]

        #Convierte la distancia (min_dist) en un número que se parezca a un porcentaje de similitud.
        similarity = max(0, 100 - min_dist * 18)  # (18) mientras mas bajos son los valores mas similares son los rostros

        # Umbral: Aunque el rostro se parezca, si la distancia es demasiado alta, mejor no me arriesgo y digo que es ‘Desconocido’.
        if min_dist > 3.5:  # Si supera el umbral, se considera desconocido
            identity = "Desconocido"
            similarity = 0

        return identity, similarity

    except Exception as e:
        print("⚠️ Error en reconocimiento:", e)
        return "Desconocido", 0
