from app.detection.yoloface import detect_faces
import cv2

print("🚀 Iniciando CheckFace (detección en tiempo real)...")

cap = cv2.VideoCapture(0)

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
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("CheckFace - Detección", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print("👋 Cerrando CheckFace...")
        break

cap.release()
cv2.destroyAllWindows()
