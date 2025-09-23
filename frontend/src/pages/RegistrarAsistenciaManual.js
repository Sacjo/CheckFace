import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import Select from 'react-select';
import 'react-datepicker/dist/react-datepicker.css';

export default function RegistrarAsistenciaManual() {
  const [users, setUsers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    course_id: '',
    date: new Date(),
    observations: '',
  });
  const [status, setStatus] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/participants')
      .then(res => {
        const options = res.data.map(user => ({
          value: user.id,
          label: `${user.username} - CI ${user.ci}`
        }));
        setUsers(options);
      })
      .catch(err => {
        console.error(err);
        setStatus({ type: 'danger', msg: 'Error al cargar estudiantes.' });
      });
  }, []);

  const handleUserSelect = async (selected) => {
    setSelectedUser(selected);
    setFormData({ ...formData, course_id: '' });

    try {
      const res = await axios.get(`http://127.0.0.1:5000/api/participants/${selected.value}/courses`);
      setCourses(res.data);
    } catch (err) {
      console.error(err);
      setCourses([]);
      setStatus({ type: 'danger', msg: 'Error al cargar cursos del estudiante.' });
    }
  };

  const onSubmit = async e => {
    e.preventDefault();

    if (!selectedUser || !formData.course_id || !formData.date) {
      setStatus({ type: 'danger', msg: 'Todos los campos son obligatorios.' });
      return;
    }

    try {
      await axios.post('http://127.0.0.1:5000/api/asistencia-manual', {
        user_id: selectedUser.value,
        course_id: formData.course_id,
        date: formData.date.toISOString(),
        observations: formData.observations
      });

      setStatus({ type: 'success', msg: 'Asistencia registrada correctamente.' });
      setFormData({ course_id: '', date: new Date(), observations: '' });
      setSelectedUser(null);
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar la asistencia.' });
    }
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Asistencia Manual</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Asistencia Manual</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-user-check me-1"></i>
          Ingreso Manual de Asistencia
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            {/* Estudiante */}
            <div className="mb-3">
              <label className="form-label">Estudiante</label>
              <Select
                options={users}
                value={selectedUser}
                onChange={handleUserSelect}
                placeholder="Buscar por nombre o CI..."
              />
            </div>

            {/* Curso */}
            <div className="mb-3">
              <label htmlFor="course_id" className="form-label">Curso</label>
              <select
                id="course_id"
                name="course_id"
                className="form-select"
                value={formData.course_id}
                onChange={e => setFormData({ ...formData, course_id: e.target.value })}
              >
                <option value="">-- Seleccionar curso --</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>
            </div>

            {/* Fecha */}
            <div className="mb-3">
              <label className="form-label">Fecha</label>
              <DatePicker
                selected={formData.date}
                onChange={(date) => setFormData({ ...formData, date })}
                dateFormat="yyyy-MM-dd HH:mm"
                showTimeSelect
                className="form-control"
              />
            </div>

            {/* Observación */}
            <div className="mb-3">
              <label htmlFor="observations" className="form-label">Observación</label>
              <textarea
                id="observations"
                name="observations"
                className="form-control"
                value={formData.observations}
                onChange={e => setFormData({ ...formData, observations: e.target.value })}
                placeholder="Opcional: Ej. Llegó tarde"
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Registrar Asistencia
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}