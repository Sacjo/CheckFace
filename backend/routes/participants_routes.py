# backend/routes/participans_routes.py
from flask import Blueprint, request, jsonify
from database.db import get_connection
import os
from werkzeug.utils import secure_filename
from train_faces import entrenar
from datetime import datetime, timedelta


participants_routes = Blueprint("participants_routes", __name__)

# Directorios base
RAW_DIR   = os.path.join(os.getcwd(), 'backend', 'recognition', 'raw_faces')
KNOWN_DIR = os.path.join(os.getcwd(), 'backend', 'recognition', 'known_faces')
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(KNOWN_DIR, exist_ok=True)


# POST: Crear nuevo participante
@participants_routes.route("/api/participants", methods=["POST"])
def create_participant():
    data = request.form
    full_name  = data.get("full_name")
    ci         = data.get("ci")
    occupation = data.get("occupation")
    user_id    = data.get("user_id")
    course_id  = data.get("course_id")
    images     = request.files.getlist("images")

    if not all([full_name, ci, occupation, user_id, course_id]) or not images:
        return jsonify({"error": "Todos los campos y al menos una imagen son requeridos"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si CI ya existe en participants
        cur.execute("SELECT id FROM participants WHERE ci = %s", (ci,))
        if cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "CI ya registrado"}), 409

        # Verificar existencia de usuario y curso
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404

        cur.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
        if not cur.fetchone():
            return jsonify({"error": "Curso no encontrado"}), 404

        # Insertar participante
        cur.execute("""
            INSERT INTO participants (full_name, ci, occupation, user_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (full_name, ci, occupation, user_id))
        participant_id = cur.fetchone()[0]

        # Asignar curso
        cur.execute("""
            INSERT INTO participant_courses (participant_id, course_id)
            VALUES (%s, %s)
        """, (participant_id, course_id))

        conn.commit()
        cur.close(); conn.close()

        # Guardar imágenes
        ci_safe = secure_filename(ci)
        ci_path = os.path.join(RAW_DIR, ci_safe)
        os.makedirs(ci_path, exist_ok=True)

        start_idx = len(os.listdir(ci_path)) + 1
        for i, img in enumerate(images, start=start_idx):
            filename = f"{i}_{secure_filename(img.filename)}"
            img.save(os.path.join(ci_path, filename))

        # Ejecutar entrenamiento
        import subprocess
        subprocess.run(["python", "backend/train_faces.py", ci])

        return jsonify({
            "success": True,
            "participant_id": participant_id,
            "ci": ci,
            "message": "Participante creado, curso asignado y modelo entrenado"
        }), 201

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500
    

@participants_routes.route("/api/participants", methods=["GET"])
def get_all_participants():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, u.username, p.ci
            FROM participants p
            JOIN users u ON p.user_id = u.id
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        participants = []
        for row in rows:
            participants.append({
                "id": row[0],
                "username": row[1],
                "ci": row[2]
            })

        return jsonify(participants), 200
    except Exception as e:
        print("❌ Error al obtener participantes:", e)
        return jsonify({"error": str(e)}), 500
    

# POST: Asignar un curso a un participante ya existente
@participants_routes.route("/api/participants/<int:participant_id>/assign-course", methods=["POST"])
def assign_course(participant_id):
    data = request.json
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"error": "Se requiere course_id"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si ya tiene asignado ese curso
        cursor.execute("""
            SELECT 1 FROM participant_courses 
            WHERE participant_id = %s AND course_id = %s
        """, (participant_id, course_id))
        if cursor.fetchone():
            return jsonify({"error": "El curso ya está asignado"}), 409

        # Asignar curso
        cursor.execute("""
            INSERT INTO participant_courses (participant_id, course_id)
            VALUES (%s, %s)
        """, (participant_id, course_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Curso asignado correctamente"}), 200

    except Exception as e:
        print("❌ Error al asignar curso:", e)
        return jsonify({"error": str(e)}), 500
    
    
    
    


#  --- reemplaza los decoradores actuales por estos dos ---
@participants_routes.route("/api/participants-table", methods=["GET"])
@participants_routes.route("/api/participants-tabla", methods=["GET"])  # alias en español
def participants_table():
    """
    Registros de ASISTENCIAS con filtros opcionales:
      - q:        busca en nombre completo o CI (ILIKE)
      - course_id: id del curso (opcional)
      - from, to:  fechas YYYY-MM-DD (opcional; por defecto últimos 7 días)

    Respuesta: lista de items con:
      attendance_id, full_name, ci, course_id, course_name, date (ISO), observations
    """
    try:
        # --------- filtros ----------
        q         = (request.args.get("q") or "").strip()
        course_id = (request.args.get("course_id") or "").strip()

        # Aceptamos 'from'/'to' o 'date_from'/'date_to'
        qs_from = (request.args.get("from") or request.args.get("date_from") or "").strip()
        qs_to   = (request.args.get("to")   or request.args.get("date_to")   or "").strip()

        # Curso (opcional)
        course_val = int(course_id) if course_id.isdigit() else None

        # Fechas por defecto: últimos 7 días (incluye hoy)
        today = datetime.today().date()
        default_from = today - timedelta(days=6)
        default_to   = today

        def parse_ymd(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        date_from = parse_ymd(qs_from) or default_from
        date_to   = parse_ymd(qs_to)   or default_to

        conn = get_connection()
        cur = conn.cursor()

        # --------- consulta ----------
        # Tomamos asistencias y unimos a participantes y cursos
        sql = """
            SELECT
                a.id            AS attendance_id,
                p.full_name     AS full_name,
                p.ci            AS ci,
                c.id            AS course_id,
                c.name          AS course_name,
                a.date          AS date,
                a.observations  AS observations
            FROM attendances a
            JOIN participants p ON p.id = a.participant_id
            LEFT JOIN courses c ON c.id = a.course_id
            WHERE
                (DATE(a.date) BETWEEN %s AND %s)
                AND (%s = '' OR p.full_name ILIKE %s OR CAST(p.ci AS TEXT) ILIKE %s)
                AND (%s IS NULL OR c.id = %s)
            ORDER BY a.date DESC, p.full_name ASC
        """

        like = f"%{q}%"
        params = [date_from, date_to, q, like, like, course_val, course_val]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        # --------- salida ----------
        out = []
        for r in rows:
            out.append({
                "attendance_id": r[0],
                "full_name":     r[1],
                "ci":            r[2],
                "course_id":     r[3],
                "course_name":   r[4],
                "date":          r[5].isoformat() if r[5] else None,
                "observations":  r[6] if r[6] is not None else "",
            })

        return jsonify(out), 200

    except Exception as e:
        print("❌ Error en /api/participants-table:", e)
        return jsonify({"error": str(e)}), 500



# ========= NUEVO: resumen % asistencia por alumno-curso =========
@participants_routes.route("/api/participants-attendance-summary", methods=["GET"])
def participants_attendance_summary():
    """
    Devuelve filas agregadas por participante+curso dentro de un rango de fechas:
      - total_scheduled: clases programadas (según course_schedules y los días de la semana)
      - total_attended: asistencias registradas en attendances (fechas únicas)
      - pct: porcentaje de asistencia (total_attended / total_scheduled * 100)
    Filtros:
      q: busca en full_name o CI (opcional)
      course_id: id del curso (opcional)
      from: YYYY-MM-DD (opcional, default = hoy-6)
      to:   YYYY-MM-DD (opcional, default = hoy)
      min_pct: filtra por porcentaje mínimo (0-100), opcional
    """
    try:
        from datetime import datetime, timedelta, date

        q         = (request.args.get("q") or "").strip()
        course_id = (request.args.get("course_id") or "").strip()
        min_pct   = (request.args.get("min_pct") or "").strip()
        s_from    = (request.args.get("from") or "").strip()
        s_to      = (request.args.get("to") or "").strip()

        # Rango por defecto: últimos 7 días (incluye hoy)
        today = date.today()
        default_from = today - timedelta(days=6)
        default_to   = today

        def parse_ymd(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        date_from = parse_ymd(s_from) or default_from
        date_to   = parse_ymd(s_to)   or default_to

        course_val = int(course_id) if course_id.isdigit() else None
        min_pct_val = float(min_pct) if min_pct.replace(".", "", 1).isdigit() else None

        conn = get_connection()
        cur = conn.cursor()

        # Postgres: EXTRACT(DOW) -> 0=Dom .. 6=Sáb
        sql = """
        WITH date_range AS (
          SELECT generate_series(%s::date, %s::date, interval '1 day')::date AS d
        ),
        sched AS (
          SELECT
            cs.course_id,
            CASE
              WHEN LOWER(cs.day) = 'sunday'    THEN 0
              WHEN LOWER(cs.day) = 'monday'    THEN 1
              WHEN LOWER(cs.day) = 'tuesday'   THEN 2
              WHEN LOWER(cs.day) = 'wednesday' THEN 3
              WHEN LOWER(cs.day) = 'thursday'  THEN 4
              WHEN LOWER(cs.day) = 'friday'    THEN 5
              WHEN LOWER(cs.day) = 'saturday'  THEN 6
              ELSE NULL
            END AS dow
          FROM course_schedules cs
        ),
        sessions AS (  -- todas las clases programadas por curso en el rango
          SELECT dr.d, s.course_id
          FROM date_range dr
          JOIN sched s ON EXTRACT(DOW FROM dr.d) = s.dow
        ),
        scheduled_counts AS (
          SELECT course_id, COUNT(*)::int AS total_scheduled
          FROM sessions
          GROUP BY course_id
        ),
        attended_counts AS (
          SELECT a.participant_id, a.course_id,
                 COUNT(DISTINCT DATE(a.date))::int AS total_attended
          FROM attendances a
          WHERE DATE(a.date) BETWEEN %s AND %s
          GROUP BY a.participant_id, a.course_id
        )
        SELECT
          p.id          AS participant_id,
          p.full_name   AS full_name,
          p.ci          AS ci,
          c.id          AS course_id,
          c.name        AS course_name,
          COALESCE(sc.total_scheduled, 0) AS total_scheduled,
          COALESCE(ac.total_attended, 0)   AS total_attended,
          CASE
            WHEN COALESCE(sc.total_scheduled, 0) > 0
              THEN ROUND(100.0 * COALESCE(ac.total_attended, 0) / sc.total_scheduled, 2)
            ELSE 0
          END::float AS pct
        FROM participant_courses pc
        JOIN participants p ON p.id = pc.participant_id
        JOIN courses c      ON c.id = pc.course_id
        LEFT JOIN scheduled_counts sc ON sc.course_id = pc.course_id
        LEFT JOIN attended_counts  ac ON ac.participant_id = pc.participant_id
                                     AND ac.course_id      = pc.course_id
        WHERE
          (%s = '' OR p.full_name ILIKE %s OR CAST(p.ci AS TEXT) ILIKE %s)
          AND (%s IS NULL OR c.id = %s)
        ORDER BY p.full_name ASC, c.name ASC
        """

        like = f"%{q}%"
        params = [date_from, date_to, date_from, date_to, q, like, like, course_val, course_val]
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        out = []
        for r in rows:
            item = {
                "participant_id": r[0],
                "full_name": r[1],
                "ci": r[2],
                "course_id": r[3],
                "course_name": r[4],
                "total_scheduled": int(r[5]),
                "total_attended": int(r[6]),
                "pct": float(r[7]),
            }
            if min_pct_val is not None and item["pct"] < min_pct_val:
                continue
            out.append(item)

        return jsonify(out), 200

    except Exception as e:
        print("❌ Error en /api/participants-attendance-summary:", e)
        return jsonify({"error": str(e)}), 500




@participants_routes.route("/api/participants-unique", methods=["GET"])
def participants_unique_list():
    """
    Devuelve una fila por participante:
      id, full_name, ci, course_ids (array), course_names (string).
    Filtros opcionales:
      - q: busca por nombre o CI (ILIKE)
      - course_id: si se especifica, solo alumnos que pertenezcan a ese curso
    """
    try:
        q = (request.args.get("q") or "").strip()
        course_id = (request.args.get("course_id") or "").strip()
        course_val = int(course_id) if course_id.isdigit() else None

        conn = get_connection()
        cur = conn.cursor()

        # Nota: LEFT JOIN para no perder participantes sin cursos.
        #   Agrupamos por participante y agregamos cursos (id + nombre).
        #   Si llega course_id, filtramos por pertenencia a ese curso.
        sql = """
        SELECT
          p.id,
          p.full_name,
          p.ci,
          COALESCE(ARRAY_AGG(DISTINCT c.id) FILTER (WHERE c.id IS NOT NULL), '{}') AS course_ids,
          COALESCE(STRING_AGG(DISTINCT c.name, ', ' ORDER BY c.name), '')          AS course_names
        FROM participants p
        LEFT JOIN participant_courses pc ON pc.participant_id = p.id
        LEFT JOIN courses c             ON c.id = pc.course_id
        WHERE
          (%s = '' OR p.full_name ILIKE %s OR CAST(p.ci AS TEXT) ILIKE %s)
          AND (%s IS NULL OR c.id = %s)
        GROUP BY p.id, p.full_name, p.ci
        ORDER BY p.id DESC;
        """

        like = f"%{q}%"
        params = [q, like, like, course_val, course_val]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        out = [{
            "id": r[0],
            "full_name": r[1],
            "ci": r[2],
            "course_ids": list(r[3]) if r[3] is not None else [],
            "course_names": r[4] or ""
        } for r in rows]

        return jsonify(out), 200

    except Exception as e:
        print("❌ Error en /api/participants-unique:", e)
        return jsonify({"error": str(e)}), 500
