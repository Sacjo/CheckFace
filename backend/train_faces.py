# backend/train_faces.py

import os
import sys
import cv2
import json
import numpy as np
from deepface import DeepFace
from detection.yoloface import detect_faces
from recognition.helpers import (
    robust_mean,
    calcular_distancia_promedio
)

RAW_DIR = "backend/recognition/raw_faces"
PROCESSED_DIR = "backend/recognition/known_faces"
EMBEDDINGS_DIR = "backend/recognition/embeddings"
CENTROIDS_PATH = os.path.join(EMBEDDINGS_DIR, "centroids.json")


def recortar_y_guardar(ci):
    print(f"✂️ Recortando rostros para {ci} con YOLOv8...")
    raw_path = os.path.join(RAW_DIR, ci)
    processed_path = os.path.join(PROCESSED_DIR, ci)

    if not os.path.isdir(raw_path):
        print(f"❌ No se encontró el directorio {raw_path}")
        return

    os.makedirs(processed_path, exist_ok=True)

    for file in os.listdir(raw_path):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(raw_path, file)
        save_path  = os.path.join(processed_path, file)

        if os.path.exists(save_path):
            continue

        img = cv2.imread(image_path)
        boxes = detect_faces(img)

        if not boxes:
            print(f"⚠️ No se detectó rostro en {file}, se salta.")
            continue

        x, y, w, h = boxes[0]
        face_crop = img[y:y+h, x:x+w]
        face_crop = cv2.resize(face_crop, (160, 160))
        cv2.imwrite(save_path, face_crop)
        print(f"✅ Recortado: {save_path}")


def generar_embeddings(ci):
    print(f"🧬 Generando embeddings para {ci}...")
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    # Cargar centroides anteriores si existen
    if os.path.exists(CENTROIDS_PATH):
        with open(CENTROIDS_PATH, "r") as f:
            centroids_index = json.load(f)
    else:
        centroids_index = {}

    person_path = os.path.join(PROCESSED_DIR, ci)
    if not os.path.isdir(person_path):
        print(f"❌ No existe el directorio procesado de {ci}")
        return

    new_embeddings = []

    for file in os.listdir(person_path):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(person_path, file)
        try:
            rep = DeepFace.represent(
                img_path=img_path,
                model_name="ArcFace",
                enforce_detection=False,
                detector_backend="skip"
            )[0]
            emb = np.array(rep["embedding"], dtype=np.float32)
            new_embeddings.append(emb.tolist())
            print(f"🧠 Embedding generado: {file}")
        except Exception as e:
            print(f"⚠️ Error en {file}: {e}")

    if not new_embeddings:
        print("⚠️ No se generaron nuevos embeddings")
        return

    # Guardar los embeddings nuevos en su propio archivo JSON
    emb_file_path = os.path.join(EMBEDDINGS_DIR, f"{ci}.json")
    with open(emb_file_path, "w") as f:
        json.dump(new_embeddings, f, indent=2)

    # Calcular centroid y distancia promedio
    emb_np = np.array(new_embeddings, dtype=np.float32)
    centroid = robust_mean(emb_np)
    intra_avg = calcular_distancia_promedio(new_embeddings)

    # Actualizar solo los datos necesarios en centroids.json
    centroids_index[ci] = {
        "centroid": centroid.tolist(),
        "count": len(new_embeddings),
        "intra_dist_avg": intra_avg
    }

    with open(CENTROIDS_PATH, "w") as f:
        json.dump(centroids_index, f, indent=2)

    print(f"\n✅ Embeddings guardados en {emb_file_path}")
    print(f"✅ Centroides actualizados en {CENTROIDS_PATH}")
    print(f"📏 Distancia promedio interna para {ci}: {intra_avg:.4f}")

def entrenar(ci):
    recortar_y_guardar(ci)
    generar_embeddings(ci)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Debe indicar el CI como argumento.")
        print("Ejemplo: python backend/train_faces.py 5144692")
        exit(1)

    ci = sys.argv[1]
    entrenar(ci)