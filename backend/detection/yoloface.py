from ultralytics import YOLO

# Cargar modelo una sola vez
<<<<<<<< HEAD:backend/app/detection/yoloface.py
model = YOLO("backend/app/detection/model-weights/yolov8n-face.pt")
========
model = YOLO("backend/detection/model-weights/yolov8n-face.pt")
>>>>>>>> 726bc54c60275af276d98210caf47b613686a914:backend/detection/yoloface.py

def detect_faces(frame):
    results = model.predict(source=frame, conf=0.5, verbose=False)[0]
    boxes = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w = x2 - x1
        h = y2 - y1
        boxes.append((x1, y1, w, h))

    return boxes
