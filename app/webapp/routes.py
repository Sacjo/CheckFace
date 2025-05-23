import io
import time
import threading
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, session, flash, jsonify, send_file
)
from . import db
from .models import User
from PIL import Image
import numpy as np
import cv2
from openpyxl import Workbook
from app.detection.yoloface import detect_faces
from app.recognition.face_recognizer import recognize_face_embedding

main = Blueprint('main', __name__, template_folder='templates')

# Memoria de la sesión actual
attendance   = []
unrecognized = set()
_lock        = threading.Lock()

# — Autenticación —
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user'] = username
            return redirect(url_for('main.index'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# — Página principal protegida —
@main.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    return render_template('index.html')

# — API de reconocimiento protegida —
@main.route('/api/recognize', methods=['POST'])
def api_recognize():
    if 'user' not in session:
        return jsonify(error='No autenticado'), 401
    try:
        data = request.data
        img = Image.open(io.BytesIO(data)).convert('RGB')
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        boxes = detect_faces(frame)
        results = []

        with _lock:
            for x, y, w, h in boxes:
                face = frame[y:y+h, x:x+w]
                name, sim = recognize_face_embedding(face)
                now = time.strftime('%H:%M:%S')
                if name == 'Unknown':
                    unrecognized.add(f'Anonimo_{x}_{y}')
                else:
                    attendance.append((name, now))
                results.append({'name': name, 'time': now})

        return jsonify(
            results=results,
            attendance=attendance,
            unrecognized=list(unrecognized)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(error=str(e)), 500

# — API para resetear datos —
@main.route('/api/reset', methods=['POST'])
def api_reset():
    if 'user' not in session:
        return jsonify(error='No autenticado'), 401
    with _lock:
        attendance.clear()
        unrecognized.clear()
    return jsonify(success=True)

# — API para obtener datos de asistencia —
@main.route('/api/attendance', methods=['GET'])
def api_attendance():
    if 'user' not in session:
        return jsonify(error='No autenticado'), 401
    return jsonify(
        attendance=attendance,
        unrecognized=list(unrecognized)
    )

# — Exportar reporte a XLSX —
@main.route('/export')
def export_report():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencia"
    ws.append(["Alumno", "Hora", "Estado"])
    for name, ts in attendance:
        ws.append([name, ts, "✔️"])
    for name in unrecognized:
        ws.append([name, "", "Anonimo"])
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name="reporte_asistencia.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
