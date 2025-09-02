from ultralytics import YOLO

# Cargar modelo una sola vez
model = YOLO("backend/detection/model-weights/yolov8n-face.pt")

def detect_faces(frame):
    results = model.predict(source=frame, conf=0.5, verbose=False)[0]
    boxes = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w = x2 - x1
        h = y2 - y1
        boxes.append((x1, y1, w, h))

    return boxes
