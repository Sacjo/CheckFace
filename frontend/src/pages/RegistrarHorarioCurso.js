// src/pages/RegistrarHorarioCurso.js
import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const CLASSROOMS = Array.from({ length: 20 }, (_, i) => `Aula ${i + 1}`);

export default function RegistrarHorarioCurso() {
  // Cursos para selects
  const [courses, setCourses] = useState([]);

  // Formulario de creación (independiente del listado)
  const [formData, setFormData] = useState({
    course_id: '',
    day: '',
    start_time: null,
    end_time: null,
    classroom: '',
  });

  const [status, setStatus] = useState(null);

  // Listado y filtros (INDEPENDIENTES del form de arriba)
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);
  const [fCourseId, setFCourseId] = useState('');  // ← curso del LISTADO ('' = todos)
  const [fDay, setFDay] = useState('');
  const [fStart, setFStart] = useState(null);
  const [fEnd,   setFEnd] = useState(null);
  const [fClassroom, setFClassroom] = useState('');

  // Modal de edición
  const [editing, setEditing] = useState(null);
  const [eDay, setEDay] = useState('');
  const [eStart, setEStart] = useState(null);
  const [eEnd, setEEnd] = useState(null);
  const [eClassroom, setEClassroom] = useState('');

  // Cargar cursos
  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/courses')
      .then((res) => setCourses(res.data))
      .catch(() => setStatus({ type: 'danger', msg: 'Error al cargar cursos.' }));
  }, []);

  // Cargar LISTADO según fCourseId ('' = todos)
  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        setLoadingSchedules(true);
        const params = fCourseId ? { course_id: fCourseId } : {};
        const { data } = await axios.get('http://127.0.0.1:5000/api/course-schedules', { params });
        setSchedules(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
        setSchedules([]);
        setStatus({ type: 'danger', msg: 'Error al listar horarios.' });
      } finally {
        setLoadingSchedules(false);
      }
    };
    fetchSchedules();
  }, [fCourseId]);

  // Helpers
  const onChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
  const formatTime = (date) => date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

  const parseTimeToMinutes = (hhmm) => {
    const [h, m] = hhmm.split(':').map(Number);
    return h * 60 + m;
  };
  const scheduleToMinutes = (scheduleStr) => {
    const [a, b] = scheduleStr.split('-').map((s) => s.trim());
    return [parseTimeToMinutes(a), parseTimeToMinutes(b)];
  };
  const dateToMinutes = (date) => (date ? date.getHours() * 60 + date.getMinutes() : null);

  // Crear horario (no toca los filtros/listado)
  const onSubmit = async (e) => {
    e.preventDefault();
    const { course_id, day, start_time, end_time, classroom } = formData;

    if (!course_id || !day || !start_time || !end_time || !classroom) {
      setStatus({ type: 'danger', msg: 'Todos los campos son obligatorios.' });
      return;
    }
    if (start_time >= end_time) {
      setStatus({ type: 'danger', msg: 'La hora de inicio debe ser menor que la de fin.' });
      return;
    }

    const schedule = `${formatTime(start_time)} - ${formatTime(end_time)}`;

    try {
      await axios.post(
        'http://127.0.0.1:5000/api/course-schedules',
        { course_id, day, schedule, classroom },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setStatus({ type: 'success', msg: 'Horario registrado correctamente.' });

      // Limpiar form, PERO NO tocamos los filtros/listado
      setFormData({ course_id, day: '', start_time: null, end_time: null, classroom: '' });

      // Refrescar listado usando fCourseId
      const params = fCourseId ? { course_id: fCourseId } : {};
      const { data } = await axios.get('http://127.0.0.1:5000/api/course-schedules', { params });
      setSchedules(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar el horario.' });
    }
  };

  // Rango de horas para pickers
  const minTime = (() => { const d = new Date(); d.setHours(6, 0, 0, 0); return d; })();
  const maxTime = (() => { const d = new Date(); d.setHours(22, 0, 0, 0); return d; })();

  // Filtrado en cliente (por día/aula/solapamiento de horas)
  const filteredSchedules = useMemo(() => {
    return schedules.filter((s) => {
      if (fDay && s.day !== fDay) return false;
      if (fClassroom && s.classroom !== fClassroom) return false;

      const fs = dateToMinutes(fStart);
      const fe = dateToMinutes(fEnd);
      if (fs != null && fe != null) {
        const [ss, se] = scheduleToMinutes(s.schedule);
        // Mostrar los que se SOLAPAN con [fs, fe]
        const overlap = !(se <= fs || ss >= fe);
        return overlap;
      }
      return true;
    });
  }, [schedules, fDay, fClassroom, fStart, fEnd]);

  // Editar
  const openEdit = (row) => {
    setEditing(row);
    setEDay(row.day || '');
    setEClassroom(row.classroom || '');
    const [a, b] = row.schedule.split('-').map((s) => s.trim());
    const [ah, am] = a.split(':').map(Number);
    const [bh, bm] = b.split(':').map(Number);
    const d1 = new Date(); d1.setHours(ah, am, 0, 0);
    const d2 = new Date(); d2.setHours(bh, bm, 0, 0);
    setEStart(d1); setEEnd(d2);
  };

  const saveEdit = async () => {
    if (!editing || !eDay || !eStart || !eEnd || !eClassroom) {
      setStatus({ type: 'danger', msg: 'Completa todos los campos del editor.' });
      return;
    }
    if (eStart >= eEnd) {
      setStatus({ type: 'danger', msg: 'La hora de inicio debe ser menor que la de fin.' });
      return;
    }
    const payload = {
      course_id: editing.course_id,
      day: eDay,
      schedule: `${formatTime(eStart)} - ${formatTime(eEnd)}`,
      classroom: eClassroom,
    };
    try {
      await axios.put(`http://127.0.0.1:5000/api/course-schedules/${editing.id}`, payload, {
        headers: { 'Content-Type': 'application/json' },
      });
      // Refrescar listado según filtros
      const params = fCourseId ? { course_id: fCourseId } : {};
      const { data } = await axios.get('http://127.0.0.1:5000/api/course-schedules', { params });
      setSchedules(Array.isArray(data) ? data : []);
      setEditing(null);
      setStatus({ type: 'success', msg: 'Horario actualizado correctamente.' });
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al actualizar el horario.' });
    }
  };

  const deleteSchedule = async (id) => {
    if (!window.confirm('¿Eliminar este horario?')) return;
    try {
      await axios.delete(`http://127.0.0.1:5000/api/course-schedules/${id}`);
      const params = fCourseId ? { course_id: fCourseId } : {};
      const { data } = await axios.get('http://127.0.0.1:5000/api/course-schedules', { params });
      setSchedules(Array.isArray(data) ? data : []);
      setStatus({ type: 'success', msg: 'Horario eliminado correctamente.' });
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al eliminar el horario.' });
    }
  };

  const clearFilters = () => {
    setFCourseId('');
    setFDay('');
    setFStart(null);
    setFEnd(null);
    setFClassroom('');
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Horario para un Curso</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Horario</li>
      </ol>

      {/* ---------- Formulario de creación (no afecta listados) ---------- */}
      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-calendar-plus me-1"></i>
          Datos del Horario
        </div>
        <div className="card-body">
          {status && <div className={`alert alert-${status.type}`} role="alert">{status.msg}</div>}

          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label htmlFor="course_id" className="form-label">Curso</label>
              <select id="course_id" name="course_id" className="form-select"
                      value={formData.course_id} onChange={onChange}>
                <option value="">-- Seleccionar curso --</option>
                {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>

            <div className="mb-3">
              <label htmlFor="day" className="form-label">Día</label>
              <select id="day" name="day" className="form-select"
                      value={formData.day} onChange={onChange}>
                <option value="">-- Seleccionar día --</option>
                {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>

            <div className="mb-3 row">
              <div className="col">
                <label className="form-label">Hora de Inicio</label>
                <DatePicker
                  selected={formData.start_time}
                  onChange={(date) => setFormData({ ...formData, start_time: date })}
                  showTimeSelect showTimeSelectOnly timeIntervals={30}
                  timeCaption="Inicio" dateFormat="HH:mm"
                  minTime={minTime} maxTime={maxTime}
                  className="form-control" placeholderText="Seleccionar hora"
                />
              </div>
              <div className="col">
                <label className="form-label">Hora de Fin</label>
                <DatePicker
                  selected={formData.end_time}
                  onChange={(date) => setFormData({ ...formData, end_time: date })}
                  showTimeSelect showTimeSelectOnly timeIntervals={30}
                  timeCaption="Fin" dateFormat="HH:mm"
                  minTime={minTime} maxTime={maxTime}
                  className="form-control" placeholderText="Seleccionar hora"
                />
              </div>
            </div>

            <div className="mb-3">
              <label htmlFor="classroom" className="form-label">Aula</label>
              <select id="classroom" name="classroom" className="form-select"
                      value={formData.classroom} onChange={onChange}>
                <option value="">-- Seleccionar aula --</option>
                {CLASSROOMS.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>

            <button type="submit" className="btn btn-primary">Registrar Horario</button>
          </form>
        </div>
      </div>

      {/* ---------- Listado y filtros (independientes) ---------- */}
      <div className="card">
        <div className="card-header">
          <i className="fas fa-list me-1"></i>
          Horarios
        </div>
        <div className="card-body">
          {/* Filtros del listado */}
          <div className="row g-3 mb-3">
            <div className="col-md-3">
              <label className="form-label">Curso</label>
              <select className="form-select" value={fCourseId} onChange={(e) => setFCourseId(e.target.value)}>
                <option value="">Todos</option>
                {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Día</label>
              <select className="form-select" value={fDay} onChange={(e) => setFDay(e.target.value)}>
                <option value="">Todos</option>
                {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Aula</label>
              <select className="form-select" value={fClassroom} onChange={(e) => setFClassroom(e.target.value)}>
                <option value="">Todas</option>
                {CLASSROOMS.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
            <div className="col-md-1">
              <label className="form-label">Desde</label>
              <DatePicker selected={fStart} onChange={setFStart}
                showTimeSelect showTimeSelectOnly timeIntervals={30}
                dateFormat="HH:mm" className="form-control"
                placeholderText="HH:mm" minTime={minTime} maxTime={maxTime}/>
            </div>
            <div className="col-md-1">
              <label className="form-label">Hasta</label>
              <DatePicker selected={fEnd} onChange={setFEnd}
                showTimeSelect showTimeSelectOnly timeIntervals={30}
                dateFormat="HH:mm" className="form-control"
                placeholderText="HH:mm" minTime={minTime} maxTime={maxTime}/>
            </div>
            <div className="col-md-1 d-flex align-items-end">
              <button type="button" className="btn btn-outline-secondary btn-sm w-100" onClick={clearFilters}>
                Limpiar
              </button>
            </div>
          </div>

          {/* Tabla */}
          {loadingSchedules ? (
            <p className="mb-0">Cargando horarios…</p>
          ) : filteredSchedules.length === 0 ? (
            <p className="text-muted mb-0">No hay horarios que coincidan con los filtros.</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped table-bordered align-middle">
                <thead>
                  <tr>
                    <th>Curso</th>
                    <th style={{ width: 120 }}>Día</th>
                    <th style={{ width: 160 }}>Horario</th>
                    <th style={{ width: 140 }}>Aula</th>
                    <th style={{ width: 180 }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSchedules.map((s) => (
                    <tr key={s.id}>
                      <td>
                        {courses.find(c => c.id === s.course_id)?.name || s.course_id}
                      </td>
                      <td>{s.day}</td>
                      <td>{s.schedule}</td>
                      <td>{s.classroom}</td>
                      <td className="d-flex gap-2">
                        <button className="btn btn-sm btn-outline-secondary" onClick={() => openEdit(s)}>
                          Editar
                        </button>
                        <button className="btn btn-sm btn-outline-danger" onClick={() => deleteSchedule(s.id)}>
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de edición */}
      {editing && (
        <>
          <div className="modal show d-block" tabIndex="-1" role="dialog" aria-modal="true">
            <div className="modal-dialog" role="document">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Editar horario #{editing.id}</h5>
                  <button type="button" className="btn-close" onClick={() => setEditing(null)}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Día</label>
                    <select className="form-select" value={eDay} onChange={(e) => setEDay(e.target.value)}>
                      <option value="">-- Seleccionar día --</option>
                      {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
                    </select>
                  </div>
                  <div className="mb-3 row">
                    <div className="col">
                      <label className="form-label">Hora de inicio</label>
                      <DatePicker selected={eStart} onChange={setEStart}
                        showTimeSelect showTimeSelectOnly timeIntervals={30}
                        dateFormat="HH:mm" className="form-control"
                        minTime={minTime} maxTime={maxTime}/>
                    </div>
                    <div className="col">
                      <label className="form-label">Hora de fin</label>
                      <DatePicker selected={eEnd} onChange={setEEnd}
                        showTimeSelect showTimeSelectOnly timeIntervals={30}
                        dateFormat="HH:mm" className="form-control"
                        minTime={minTime} maxTime={maxTime}/>
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Aula</label>
                    <select className="form-select" value={eClassroom} onChange={(e) => setEClassroom(e.target.value)}>
                      <option value="">-- Seleccionar aula --</option>
                      {CLASSROOMS.map((a) => <option key={a} value={a}>{a}</option>)}
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button className="btn btn-secondary" onClick={() => setEditing(null)}>Cancelar</button>
                  <button className="btn btn-primary" onClick={saveEdit}
                          disabled={!eDay || !eStart || !eEnd || !eClassroom}>
                    Guardar cambios
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </>
      )}
    </div>
  );
}
