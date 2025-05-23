import io, time, threading
from flask import Blueprint, render_template, request, jsonify, send_file
from PIL import Image
import numpy as np
import cv2
from openpyxl import Workbook
from app.detection.yoloface import detect_faces
from app.recognition.face_recognizer import recognize_face_embedding

main = Blueprint('main', __name__, template_folder='templates')

# Para almacenar resultados durante cada sesión de 1 min
attendance = []
unrecognized = set()
_lock = threading.Lock()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/recognize', methods=['POST'])
def api_recognize():
    """
    Recibe un JPEG en el body, devuelve JSON:
      { results: [ {name, time} ], attendance: [], unrecognized: [] }
    """
    data = request.data
    img = Image.open(io.BytesIO(data)).convert('RGB')
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    boxes = detect_faces(frame)
    results = []

    with _lock:
        for (x, y, w, h) in boxes:
            face = frame[y:y+h, x:x+w]
            name, sim = recognize_face_embedding(face)
            now = time.strftime('%H:%M:%S')
            if name == 'Unknown':
                unrecognized.add(f'Anonimo_{x}_{y}')
            else:
                attendance.append((name, now))
            results.append({'name': name, 'time': now})

    return jsonify(results=results,
                   attendance=attendance,
                   unrecognized=list(unrecognized))

@main.route('/api/attendance', methods=['GET'])
def api_attendance():
    """
    Devuelve los registros actuales de asistencia y no reconocidos.
    """
    return jsonify(attendance=attendance,
                   unrecognized=list(unrecognized))

@main.route('/api/reset', methods=['POST'])
def api_reset():
    """Limpia los registros de asistencia y no reconocidos."""
    with _lock:
        attendance.clear()
        unrecognized.clear()
    return jsonify(success=True)

@main.route('/export')
def export_report():
    """Genera un archivo XLSX con los resultados actuales de asistencia."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencia"
    # Cabecera
    ws.append(["Alumno", "Hora", "Estado"])
    # Filas de asistencia
    for name, ts in attendance:
        ws.append([name, ts, "✔️"])
    # Filas de no reconocidos
    for name in unrecognized:
        ws.append([name, "", "Anonimo"])
    # Serializar a bytes
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name="reporte_asistencia.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@main.route('/logout')
def logout():
    # lógica de cerrar sesión o redirección a login
    return ('', 204)
