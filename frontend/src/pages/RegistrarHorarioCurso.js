import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

export default function RegistrarHorarioCurso() {
  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({
    course_id: '',
    day: '',
    start_time: null,
    end_time: null,
    classroom: '',
  });

  const [status, setStatus] = useState(null);

  useEffect(() => {
    axios
      .get('http://127.0.0.1:5000/api/courses')
      .then((res) => setCourses(res.data))
      .catch((err) => {
        console.error(err);
        setStatus({ type: 'danger', msg: 'Error al cargar cursos.' });
      });
  }, []);

  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  };

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
        {
          course_id,
          day,
          schedule,
          classroom,
        },
        { headers: { 'Content-Type': 'application/json' } }
      );

      setStatus({ type: 'success', msg: 'Horario registrado correctamente.' });
      setFormData({
        course_id: '',
        day: '',
        start_time: null,
        end_time: null,
        classroom: '',
      });
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar el horario.' });
    }
  };

  // Rango mínimo y máximo para las horas
  const today = new Date();
  const minTime = new Date(today.setHours(6, 0, 0));
  const maxTime = new Date(today.setHours(22, 0, 0));

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Horario para un Curso</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Horario</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-calendar-plus me-1"></i>
          Datos del Horario
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}

          <form onSubmit={onSubmit}>
            {/* Curso */}
            <div className="mb-3">
              <label htmlFor="course_id" className="form-label">Curso</label>
              <select
                id="course_id"
                name="course_id"
                className="form-select"
                value={formData.course_id}
                onChange={onChange}
              >
                <option value="">-- Seleccionar curso --</option>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>

            {/* Día */}
            <div className="mb-3">
              <label htmlFor="day" className="form-label">Día</label>
              <select
                id="day"
                name="day"
                className="form-select"
                value={formData.day}
                onChange={onChange}
              >
                <option value="">-- Seleccionar día --</option>
                {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((day) => (
                  <option key={day} value={day}>{day}</option>
                ))}
              </select>
            </div>

            {/* Horario */}
            <div className="mb-3 row">
              <div className="col">
                <label htmlFor="start_time" className="form-label">Hora de Inicio</label>
                <DatePicker
                  selected={formData.start_time}
                  onChange={(date) => setFormData({ ...formData, start_time: date })}
                  showTimeSelect
                  showTimeSelectOnly
                  timeIntervals={30}
                  timeCaption="Inicio"
                  dateFormat="HH:mm"
                  minTime={minTime}
                  maxTime={maxTime}
                  className="form-control"
                  placeholderText="Seleccionar hora"
                />
              </div>

              <div className="col">
                <label htmlFor="end_time" className="form-label">Hora de Fin</label>
                <DatePicker
                  selected={formData.end_time}
                  onChange={(date) => setFormData({ ...formData, end_time: date })}
                  showTimeSelect
                  showTimeSelectOnly
                  timeIntervals={30}
                  timeCaption="Fin"
                  dateFormat="HH:mm"
                  minTime={minTime}
                  maxTime={maxTime}
                  className="form-control"
                  placeholderText="Seleccionar hora"
                />
              </div>
            </div>

            {/* Aula */}
            <div className="mb-3">
              <label htmlFor="classroom" className="form-label">Aula</label>
              <select
                id="classroom"
                name="classroom"
                className="form-select"
                value={formData.classroom}
                onChange={onChange}
              >
                <option value="">-- Seleccionar aula --</option>
                {[...Array(20)].map((_, i) => (
                  <option key={i + 1} value={`Aula ${i + 1}`}>{`Aula ${i + 1}`}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary">
              Registrar Horario
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}