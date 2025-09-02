from detection.yoloface import detect_faces
from deepface import DeepFace
import cv2
import os
import numpy as np
import json

RAW_DIR = "backend/recognition/raw_faces"
PROCESSED_DIR = "backend/recognition/known_faces"
EMBEDDINGS_DIR = "backend/recognition/embeddings"  # ← nuevo

def recortar_y_guardar():
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
            if not file.lower().endswith((".jpg", ".png", ".jepg",)):
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
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    resumen_por_persona = {}

    for person in os.listdir(PROCESSED_DIR):
        person_path = os.path.join(PROCESSED_DIR, person)
        if not os.path.isdir(person_path):
            continue

        person_embeddings = []

        for file in os.listdir(person_path):
            if not file.lower().endswith((".jpg", ".png")):
                continue

            try:
                img_path = os.path.join(person_path, file)
                result = DeepFace.represent(img_path=img_path, model_name="ArcFace", enforce_detection=False)[0]
                person_embeddings.append(result["embedding"])
                print(f"🧠 Embedding generado: {person}/{file}")
            except Exception as e:
                print(f"⚠️ Error en {file}: {e}")

        # Guardar los embeddings en archivo por persona
        if person_embeddings:
            with open(os.path.join(EMBEDDINGS_DIR, f"{person}.json"), "w") as f:
                json.dump(person_embeddings, f)

            resumen_por_persona[person] = {
                "count": len(person_embeddings),
                "distance_avg": calcular_distancia_promedio(person_embeddings)
            }

    print("\n📦 Embeddings guardados por persona")
    print("📊 Resumen:")
    for person, data in resumen_por_persona.items():
        print(f"🧍 {person}: {data['count']} embeddings - dist. promedio interna: {data['distance_avg']:.2f}")


def calcular_distancia_promedio(embeddings_list):
    if len(embeddings_list) < 2:
        return 0.0
    distancias = []
    for i in range(len(embeddings_list)):
        for j in range(i + 1, len(embeddings_list)):
            a = np.array(embeddings_list[i])
            b = np.array(embeddings_list[j])
            dist = np.linalg.norm(a - b)
            distancias.append(dist)
    return np.mean(distancias) if distancias else 0.0


def entrenar():
    recortar_y_guardar()
    generar_embeddings()

if __name__ == "__main__":
    entrenar()