import cv2
import os
import numpy as np

# Rutas de configuración del modelo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CFG = os.path.join(BASE_DIR, "yoloface/cfg/yolov3-face.cfg")
WEIGHTS = os.path.join(BASE_DIR, "yoloface/model-weights/yolov3-wider_16000.weights")

# Inicializar el modelo una sola vez
net = cv2.dnn.readNetFromDarknet(CFG, WEIGHTS)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)  # Si usás CUDA

CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.3

def detect_faces(frame):
    """Detecta rostros en una imagen (frame). Devuelve una lista de cajas [x, y, w, h]."""
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    layer_names = net.getLayerNames()
    output_layer_ids = net.getUnconnectedOutLayers().flatten()
    output_layers = [layer_names[i - 1] for i in output_layer_ids]
    outs = net.forward(output_layers)

    boxes = []
    confidences = []

    for out in outs:
        for detection in out:
            confidence = detection[4]
            if confidence > CONFIDENCE_THRESHOLD:
                center_x, center_y, width, height = (
                    int(detection[0] * w),
                    int(detection[1] * h),
                    int(detection[2] * w),
                    int(detection[3] * h),
                )
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                boxes.append([x, y, width, height])
                confidences.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    final_boxes = []
    if len(indices) > 0:
        for i in indices:
            i = i[0] if isinstance(i, (list, tuple, np.ndarray)) else i
            final_boxes.append(boxes[i])

    return final_boxes
