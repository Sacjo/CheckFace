# backend/routes/attendance_routes.py
from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime, timedelta

attendance_routes = Blueprint("attendance_routes", __name__)

@attendance_routes.route("/api/asistencia", methods=["POST"])
def registrar_asistencia():
    data = request.get_json()
    cis = data.get("cis", [])
    course_id = data.get("course_id")
    fecha = data.get("date")
    observations = data.get("observations", None)

    if not cis or not course_id or not fecha:
        return jsonify({"success": False, "message": "Nombres, course_id y date requeridos"}), 400

    registrados, no_encontrados, fuera_curso = [], [], []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for ci in cis:
            cursor.execute("SELECT id FROM participants WHERE ci = %s", (ci,))
            user = cursor.fetchone()
            if not user:
                no_encontrados.append(ci)
                continue

            user_id = user[0]

            cursor.execute(
                "SELECT 1 FROM participant_courses WHERE participant_id = %s AND course_id = %s",
                (user_id, course_id)
            )
            if not cursor.fetchone():
                fuera_curso.append(ci)
                continue

            cursor.execute(
                """
                INSERT INTO attendances (participant_id, course_id, date, observations)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT unique_attendance_per_day
                DO UPDATE
                SET observations = EXCLUDED.observations
                """,
                (user_id, course_id, fecha, observations)
            )
            registrados.append(ci)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "registrados": registrados,
            "no_encontrados": no_encontrados,
            "fuera_curso": fuera_curso
        }), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_routes.route("/api/asistencia-manual", methods=["POST"])
def registrar_asistencia_manual():
    try:
        data = request.get_json()
        print("📥 Recibido en backend:", data)

        participant_id = data.get("user_id")   # ID del participante
        course_id      = data.get("course_id")
        date           = data.get("date")
        observations   = data.get("observations", None)

        if not participant_id or not course_id or not date:
            return jsonify({"success": False, "message": "Campos requeridos: user_id, course_id y date"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Verificar participante
        cursor.execute("SELECT id FROM participants WHERE id = %s", (participant_id,))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"success": False, "message": "Participante no encontrado"}), 404

        # Verificar pertenencia al curso
        cursor.execute("""
            SELECT 1 FROM participant_courses
            WHERE participant_id = %s AND course_id = %s
        """, (participant_id, course_id))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"success": False, "message": "El participante no está asignado al curso"}), 400

        # Registrar asistencia con fecha específica
        cursor.execute("""
            INSERT INTO attendances (participant_id, course_id, date, observations)
            VALUES (%s, %s, %s, %s)
        """, (participant_id, course_id, date, observations))

        conn.commit()
        cursor.close(); conn.close()

        return jsonify({"success": True, "message": "Asistencia manual registrada"}), 201

    except Exception as e:
        print("❌ Error en asistencia manual:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ======= LISTADO SIMPLE (corregido a 'attendances' + 'participants') =======
@attendance_routes.route("/api/asistencias", methods=["GET"])
def obtener_asistencias():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.full_name, a.date
            FROM attendances a
            JOIN participants p ON p.id = a.participant_id
            ORDER BY a.date DESC
            LIMIT 200
        """)
        rows = cursor.fetchall()

        asistencias = [{"name": row[0], "date": row[1].isoformat()} for row in rows]

        cursor.close(); conn.close()
        return jsonify(asistencias), 200

    except Exception as e:
        print("❌ Error al obtener asistencias:", e)
        return jsonify({"error": str(e)}), 500


# ======= RESUMEN CON FILTROS (para el gráfico) =======
@attendance_routes.route("/api/asistencias/resumen", methods=["GET"])
def resumen_asistencias():
    try:
        # Query params
        qs_from = request.args.get("from")
        qs_to = request.args.get("to")
        qs_course_id = request.args.get("course_id")
        qs_occ = request.args.get("occupation")

        # Rango por defecto: últimos 7 días (incluye hoy)
        today = datetime.today().date()
        default_from = today - timedelta(days=6)
        default_to = today

        # Parseo de fechas
        def parse_ymd(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        date_from = parse_ymd(qs_from) or default_from
        date_to = parse_ymd(qs_to) or default_to

        # Normalizar filtros opcionales
        course_id = int(qs_course_id) if (qs_course_id and qs_course_id.strip().isdigit()) else None
        occupation = qs_occ if qs_occ in ("student", "teacher") else None

        conn = get_connection()
        cur = conn.cursor()

        # Generamos serie de días y LEFT JOIN para conservar días sin registros
        sql = """
        WITH dates AS (
          SELECT generate_series(%s::date, %s::date, interval '1 day')::date AS day
        )
        SELECT d.day,
               COALESCE(COUNT(a.id), 0) AS cnt
        FROM dates d
        LEFT JOIN attendances a
               ON date(a.date) = d.day
              AND (%s IS NULL OR a.course_id = %s)
        LEFT JOIN participants p
               ON p.id = a.participant_id
              AND (%s IS NULL OR p.occupation = %s)
        GROUP BY d.day
        ORDER BY d.day ASC
        """
        params = [date_from, date_to, course_id, course_id, occupation, occupation]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        out = [{"date": r[0].isoformat(), "count": int(r[1])} for r in rows]
        return jsonify(out), 200

    except Exception as e:
        print("Error en resumen_asistencias:", e)
        return jsonify({"error": str(e)}), 500


@attendance_routes.route("/api/participants/<int:participant_id>/courses", methods=["GET"])
def obtener_cursos_de_participante(participant_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.name, c.semester, c.career
            FROM courses c
            JOIN participant_courses pc ON pc.course_id = c.id
            WHERE pc.participant_id = %s
        """, (participant_id,))

        cursos = cursor.fetchall()
        cursor.close(); conn.close()

        result = []
        for c in cursos:
            result.append({
                "id": c[0],
                "name": c[1],
                "semester": c[2],
                "career": c[3]
            })

        return jsonify(result), 200

    except Exception as e:
        print("❌ Error al obtener cursos del participante:", e)
        return jsonify({"error": str(e)}), 500
    

@attendance_routes.route("/api/asistencia/registrados", methods=["GET"])
def get_asistencias_registradas():
    course_id = request.args.get("course_id")
    fecha = request.args.get("date")

    if not course_id or not fecha:
        return jsonify({"success": False, "message": "course_id y date requeridos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.ci, p.full_name
            FROM attendances a
            JOIN participants p ON a.participant_id = p.id
            WHERE a.course_id = %s AND a.date::date = %s::date
        """, (course_id, fecha))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        registrados = [
            {"id": row[0], "ci": row[1], "full_name": row[2]} for row in rows
        ]

        return jsonify({"success": True, "registrados": registrados}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
    


# ======= PORCENTAJES DE ASISTENCIA POR ALUMNO Y CURSO =======
@attendance_routes.route("/api/asistencias/porcentajes", methods=["GET"])
def porcentajes_asistencia():
    """
    Devuelve filas por (participante, curso) con:
      attended   = asistencias registradas en el rango
      scheduled  = clases programadas en el rango (según course_schedules)
      pct        = round(attended / scheduled * 100)

    Query params:
      from       YYYY-MM-DD (default: hoy-6)
      to         YYYY-MM-DD (default: hoy)
      course_id  (opcional) filtra por curso específico
      q          (opcional) busca por nombre o CI (ILIKE)
      min_pct    (opcional) entero 0..100, filtra por porcentaje mínimo
    """
    try:
        # ---- leer params y defaults ----
        qs_from    = request.args.get("from")
        qs_to      = request.args.get("to")
        qs_course  = request.args.get("course_id")
        qs_q       = request.args.get("q", "").strip()
        qs_min_pct = request.args.get("min_pct")

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

        course_id = int(qs_course) if (qs_course and qs_course.isdigit()) else None
        min_pct   = int(qs_min_pct) if (qs_min_pct and qs_min_pct.isdigit()) else None

        # patrón búsqueda (nombre/CI)
        q_pattern = f"%{qs_q.lower()}%" if qs_q else None

        conn = get_connection()
        cur  = conn.cursor()

        # CTE:
        # - dates: días del rango
        # - course_dow: (course_id, dow) del horario (Monday..Sunday -> 1..7)
        # - scheduled_by_course: cuántas clases hay por curso en el rango
        # - attendance_by_pc: cuántas asistencias por (participante, curso) en el rango
        sql = """
        WITH dates AS (
          SELECT generate_series(%s::date, %s::date, interval '1 day')::date AS day
        ),
        course_dow AS (
          SELECT
            cs.course_id,
            CASE lower(cs.day)
              WHEN 'monday'    THEN 1
              WHEN 'tuesday'   THEN 2
              WHEN 'wednesday' THEN 3
              WHEN 'thursday'  THEN 4
              WHEN 'friday'    THEN 5
              WHEN 'saturday'  THEN 6
              WHEN 'sunday'    THEN 7
              ELSE NULL
            END AS dow
          FROM course_schedules cs
        ),
        scheduled_by_course AS (
          SELECT cd.course_id, COUNT(*)::int AS scheduled
          FROM dates d
          JOIN course_dow cd
            ON EXTRACT(ISODOW FROM d.day)::int = cd.dow
          GROUP BY cd.course_id
        ),
        attendance_by_pc AS (
          SELECT a.participant_id, a.course_id, COUNT(*)::int AS attended
          FROM attendances a
          WHERE DATE(a.date) BETWEEN %s AND %s
          GROUP BY a.participant_id, a.course_id
        )
        SELECT
          p.id        AS participant_id,
          p.full_name,
          p.ci,
          c.id        AS course_id,
          c.name      AS course_name,
          COALESCE(apc.attended, 0) AS attended,
          COALESCE(sbc.scheduled, 0) AS scheduled,
          CASE
            WHEN COALESCE(sbc.scheduled, 0) = 0 THEN 0
            ELSE ROUND((COALESCE(apc.attended,0)::numeric * 100.0) / sbc.scheduled)::int
          END AS pct
        FROM participant_courses pc
        JOIN participants p ON p.id = pc.participant_id
        JOIN courses     c   ON c.id = pc.course_id
        LEFT JOIN attendance_by_pc   apc ON apc.participant_id = pc.participant_id
                                        AND apc.course_id      = pc.course_id
        LEFT JOIN scheduled_by_course sbc ON sbc.course_id     = pc.course_id
        WHERE (%s IS NULL OR pc.course_id = %s)
          AND (%s IS NULL OR lower(p.full_name) LIKE %s OR p.ci ILIKE %s)
          -- si no hubo clases programadas en el rango, no tiene sentido calcular %
          AND COALESCE(sbc.scheduled, 0) > 0
        ORDER BY p.full_name ASC, c.name ASC
        """
        params = [
            date_from, date_to,            # dates
            date_from, date_to,            # attendance_by_pc
            course_id, course_id,          # filtro curso
            q_pattern, q_pattern, q_pattern  # filtro q (nombre / CI)
        ]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        result = []
        for r in rows:
            row = {
                "participant_id": r[0],
                "full_name":      r[1],
                "ci":             r[2],
                "course_id":      r[3],
                "course_name":    r[4],
                "attended":       int(r[5]),
                "scheduled":      int(r[6]),
                "pct":            int(r[7]),
            }
            result.append(row)

        # filtro por porcentaje mínimo (si viene)
        if min_pct is not None:
            result = [x for x in result if x["pct"] >= min_pct]

        return jsonify(result), 200

    except Exception as e:
        print("❌ Error en porcentajes_asistencia:", e)
        return jsonify({"error": str(e)}), 500


# ======= PORCENTAJES POR PARTICIPANTE Y CURSO (para la tabla) =======
@attendance_routes.route("/api/asistencias/porcentajes", methods=["GET"])
def asistencias_porcentajes():
    """
    Devuelve filas: un registro por (participante, curso) con:
      attended (asistencias), scheduled (clases programadas) y pct (porcentaje),
    filtrado por rango de fechas, curso, búsqueda por nombre/CI y % mínimo.
    Query string:
      from=YYYY-MM-DD, to=YYYY-MM-DD, course_id=<id>, q=<texto>, min_pct=<0..100>
    """
    try:
        from datetime import datetime, timedelta
        conn = get_connection()
        cur = conn.cursor()

        # --- Parámetros ---
        qs_from      = request.args.get("from")
        qs_to        = request.args.get("to")
        qs_course_id = request.args.get("course_id")
        qs_q         = request.args.get("q", "").strip()
        qs_min_pct   = request.args.get("min_pct")

        today = datetime.today().date()
        date_from = datetime.strptime(qs_from, "%Y-%m-%d").date() if qs_from else (today - timedelta(days=6))
        date_to   = datetime.strptime(qs_to, "%Y-%m-%d").date()   if qs_to   else today

        course_id = int(qs_course_id) if (qs_course_id and qs_course_id.isdigit()) else None
        q_like    = f"%{qs_q}%" if qs_q else ""
        min_pct   = int(qs_min_pct) if (qs_min_pct and qs_min_pct.isdigit()) else None

        # --- SQL ---
        sql = """
        WITH dates AS (
          SELECT generate_series(%s::date, %s::date, interval '1 day')::date AS d
        ),
        -- Conteo de clases programadas en el rango, por participante y curso
        scheduled AS (
          SELECT pc.participant_id,
                 cs.course_id,
                 COUNT(*) AS scheduled
          FROM participant_courses pc
          JOIN course_schedules cs ON cs.course_id = pc.course_id
          JOIN dates dt
            ON EXTRACT(ISODOW FROM dt.d)::int = array_position(
                 ARRAY['monday','tuesday','wednesday','thursday','friday','saturday','sunday'],
                 lower(cs.day)
               )
          GROUP BY pc.participant_id, cs.course_id
        ),
        -- Conteo de asistencias reales registradas en el rango
        attended AS (
          SELECT a.participant_id,
                 a.course_id,
                 COUNT(*) AS attended
          FROM attendances a
          WHERE date(a.date) BETWEEN %s AND %s
          GROUP BY a.participant_id, a.course_id
        )
        SELECT
          p.id  AS participant_id,
          p.full_name,
          p.ci,
          c.id  AS course_id,
          c.name AS course_name,
          COALESCE(att.attended, 0)  AS attended,
          COALESCE(sch.scheduled, 0) AS scheduled,
          CASE
            WHEN COALESCE(sch.scheduled, 0) = 0 THEN 0
            ELSE ROUND(100.0 * COALESCE(att.attended,0) / sch.scheduled)::int
          END AS pct
        FROM participant_courses pc
        JOIN participants p ON p.id = pc.participant_id
        JOIN courses     c ON c.id = pc.course_id
        LEFT JOIN attended att
               ON att.participant_id = pc.participant_id AND att.course_id = pc.course_id
        LEFT JOIN scheduled sch
               ON sch.participant_id = pc.participant_id AND sch.course_id = pc.course_id
        WHERE (%s IS NULL OR c.id = %s)
          AND (%s = '' OR p.full_name ILIKE %s OR p.ci ILIKE %s)
          AND (%s IS NULL OR
               (CASE
                  WHEN COALESCE(sch.scheduled, 0) = 0 THEN 0
                  ELSE ROUND(100.0 * COALESCE(att.attended,0) / sch.scheduled)::int
                END) >= %s)
        ORDER BY p.full_name, c.name;
        """

        params = [
            date_from, date_to,             # dates CTE
            date_from, date_to,             # attended CTE
            course_id, course_id,           # filtro curso
            q_like, q_like, q_like,         # filtro nombre/CI
            min_pct, min_pct                # filtro % mínimo
        ]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        data = [{
            "participant_id": r[0],
            "full_name":      r[1],
            "ci":             r[2],
            "course_id":      r[3],
            "course_name":    r[4],
            "attended":       int(r[5]),
            "scheduled":      int(r[6]),
            "pct":            int(r[7]),
        } for r in rows]

        return jsonify(data), 200

    except Exception as e:
        print("❌ Error en /api/asistencias/porcentajes:", e)
        return jsonify({"error": str(e)}), 500
