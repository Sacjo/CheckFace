from detection.yoloface import detect_faces
from recognition.face_recognizer import load_centroids, recognize_face
import cv2

# Cargar centroides
centroids = load_centroids()

print("🚀 Iniciando CheckFace: detección + reconocimiento en tiempo real...")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("⚠️ Cámara externa no disponible. Probando con cámara integrada...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ No se pudo abrir ninguna cámara.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Error al capturar frame.")
        break

    boxes = detect_faces(frame)

    for (x, y, w, h) in boxes:
        # Recortar rostro detectado
        face_crop = frame[y:y+h, x:x+w]
        face_crop = cv2.resize(face_crop, (160, 160))

        # Reconocer
        identity, min_dist, similarity = recognize_face(face_crop, centroids)

        label = f"{identity} ({similarity:.1f}%)"
        print(f"🔎 Detectado: {label}")

        # Dibujar en pantalla
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("CheckFace - Reconocimiento en tiempo real", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("👋 Cerrando CheckFace...")
        break

cap.release()
cv2.destroyAllWindows()