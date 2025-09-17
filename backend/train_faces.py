import os
import cv2
import json
import numpy as np
from deepface import DeepFace
from detection.yoloface import detect_faces
from recognition.helpers import (
    l2_normalize,
    cosine_distance,
    robust_mean,
    calcular_distancia_promedio
)

# Directorios
RAW_DIR = "backend/recognition/raw_faces"
PROCESSED_DIR = "backend/recognition/known_faces"
EMBEDDINGS_DIR = "backend/recognition/embeddings"
CENTROIDS_PATH  = os.path.join(EMBEDDINGS_DIR, "centroids.json")

# -----------------------------
# Procesar imágenes y recortar rostros
# -----------------------------
def recortar_y_guardar():
    """Limpia y recorta rostros desde raw_faces hacia known_faces."""
    print("🧼 Limpiando rostros anteriores en known_faces/...")
    for person in os.listdir(PROCESSED_DIR):
        person_path = os.path.join(PROCESSED_DIR, person)
        if os.path.isdir(person_path):
            for file in os.listdir(person_path):
                os.remove(os.path.join(person_path, file))
            print(f"🧹 Limpiado: {person_path}")

    print("✂️ Recortando rostros con YOLOv8...")

    for person in os.listdir(RAW_DIR):
        raw_path = os.path.join(RAW_DIR, person)
        processed_path = os.path.join(PROCESSED_DIR, person)

        if not os.path.isdir(raw_path):
            continue 
        
        os.makedirs(processed_path, exist_ok=True)

        for file in os.listdir(raw_path):
            if not file.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            image_path = os.path.join(raw_path, file)
            img = cv2.imread(image_path)
            boxes = detect_faces(img)

            if not boxes:
                print(f"⚠️ No se detectó rostro en {file}, se salta.")
                continue

            x, y, w, h = boxes[0]
            face_crop = img[y:y+h, x:x+w]
            face_crop = cv2.resize(face_crop, (160, 160))

            save_path = os.path.join(processed_path, file)
            cv2.imwrite(save_path, face_crop)
            print(f"✅ Guardado: {save_path}")


# -----------------------------
# Generar embeddings y centroides
# -----------------------------
def generar_embeddings():
    """Genera embeddings y crea centroides promedio por persona."""
    print("🧬 Generando embeddings con DeepFace (ArcFace)...")
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    centroids_index = {}
    resumen_por_persona = {}

    for person in os.listdir(PROCESSED_DIR):
        person_path = os.path.join(PROCESSED_DIR, person)
        if not os.path.isdir(person_path):
            continue

        person_embeddings = []
        for file in os.listdir(person_path):
            if not file.lower().endswith((".jpg", ".png", ".jpeg")):
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
                person_embeddings.append(emb.tolist())
                print(f"🧠 Embedding generado: {person}/{file}")
            except Exception as e:
                print(f"⚠️ Error en {person}/{file}: {e}")

        if person_embeddings:
            dist_avg = calcular_distancia_promedio(person_embeddings)
            embs_np = np.array(person_embeddings, dtype=np.float32)
            centroid = robust_mean(embs_np)

            centroids_index[person] = {
                "centroid": centroid.tolist(),
                "count": len(person_embeddings),
                "intra_dist_avg": dist_avg
            }
            resumen_por_persona[person] = {
                "count": len(person_embeddings),
                "intra_dist_avg": dist_avg
            }

    with open(CENTROIDS_PATH, "w") as f:
        json.dump(centroids_index, f)

    print("\n📦 Centroides generados y guardados en:")
    print(f"🗂  {CENTROIDS_PATH}")
    for person, data in resumen_por_persona.items():
        print(f"🧍 {person}: {data['count']} embeddings - dist. interna prom: {data['intra_dist_avg']:.3f}")


# -----------------------------
# Entrenamiento completo
# -----------------------------
def entrenar():
    recortar_y_guardar()
    generar_embeddings()

if __name__ == "__main__":
    entrenar()