from app.detection.yoloface import detect_faces
from deepface import DeepFace
import cv2
import os
import numpy as np
import json

RAW_DIR = "app/recognition/raw_faces"
PROCESSED_DIR = "app/recognition/known_faces"
EMBEDDING_PATH = "app/recognition/embeddings.json"

def recortar_y_guardar():
    print("🧼 Limpiando rostros anteriores en known_faces/...")
    for person in os.listdir(PROCESSED_DIR):
        person_path = os.path.join(PROCESSED_DIR, person)
        if os.path.isdir(person_path):
            for file in os.listdir(person_path):
                file_path = os.path.join(person_path, file)
                os.remove(file_path)
            print(f"🧹 Limpiado: {person_path}")

    print("✂️ Recortando rostros con YOLOv8...")

    for person in os.listdir(RAW_DIR):
        raw_path = os.path.join(RAW_DIR, person)
        processed_path = os.path.join(PROCESSED_DIR, person)
        os.makedirs(processed_path, exist_ok=True)

        for file in os.listdir(raw_path):
            if not file.lower().endswith((".jpg", ".png")):
                continue

            image_path = os.path.join(raw_path, file)
            img = cv2.imread(image_path)
            boxes = detect_faces(img)

            if not boxes:
                print(f"⚠️ No se detectó rostro en {file}, se salta.")
                continue

            x, y, w, h = boxes[0]
            face_crop = img[y:y+h, x:x+w]

            save_path = os.path.join(processed_path, file)
            cv2.imwrite(save_path, face_crop)
            print(f"✅ {save_path}")


def generar_embeddings():
    print("🧬 Generando embeddings con DeepFace...")
    embeddings = []

    for person in os.listdir(PROCESSED_DIR):
        person_path = os.path.join(PROCESSED_DIR, person)
        if not os.path.isdir(person_path):
            continue

        for file in os.listdir(person_path):
            if not file.lower().endswith((".jpg", ".png")):
                continue

            try:
                img_path = os.path.join(person_path, file)
                result = DeepFace.represent(img_path=img_path, model_name="Facenet", enforce_detection=False)[0]
                embeddings.append({
                    "name": person,
                    "embedding": result["embedding"]
                })
                print(f"🧠 Embedding generado: {person}/{file}")
            except Exception as e:
                print(f"⚠️ Error en {file}: {e}")

    with open(EMBEDDING_PATH, "w") as f:
        json.dump(embeddings, f)
    print(f"📦 Embeddings guardados en {EMBEDDING_PATH}")

def entrenar():
    recortar_y_guardar()
    generar_embeddings()

if __name__ == "__main__":
    entrenar()
