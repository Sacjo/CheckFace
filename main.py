from app.detection.yoloface import detect_faces
from app.recognition.face_recognizer import recognize_face_embedding
import cv2

print("🚀 Iniciando CheckFace: detección + reconocimiento en tiempo real...")

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ No se pudo abrir la cámara.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Error al capturar frame.")
        break

    boxes = detect_faces(frame)

    for (x, y, w, h) in boxes:
        # Recortar el rostro detectado por YOLO
        face_crop = frame[y:y+h, x:x+w]

        # Reconocer quién es
        name, similarity = recognize_face_embedding(face_crop)

        label = f"{name} ({similarity:.1f}%)"


        # Dibujar el resultado
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("CheckFace - Reconocimiento en tiempo real", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("👋 Cerrando CheckFace...")
        break

cap.release()
cv2.destroyAllWindows()
