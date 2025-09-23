import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Select from 'react-select';

export default function AsignarCurso() {
  const [participants, setParticipants] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedParticipant, setSelectedParticipant] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [pRes, cRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/participants'),
          axios.get('http://127.0.0.1:5000/api/courses')
        ]);

        const formattedParticipants = pRes.data.map(p => ({
          value: p.id,
          label: `${p.username} - CI ${p.ci}`
        }));
        setParticipants(formattedParticipants);
        setCourses(cRes.data);
      } catch (err) {
        console.error("❌ Error al cargar participantes o cursos:", err);
      }
    };
    fetchData();
  }, []);

  const onSubmit = async e => {
    e.preventDefault();

    if (!selectedParticipant || !selectedCourse) {
      setStatus({ type: 'danger', msg: 'Seleccioná un participante y un curso.' });
      return;
    }

    try {
      await axios.post(`http://127.0.0.1:5000/api/participants/${selectedParticipant.value}/assign-course`, {
        course_id: selectedCourse
      });

      setStatus({ type: 'success', msg: 'Curso asignado correctamente.' });
      setSelectedParticipant(null);
      setSelectedCourse('');
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al asignar el curso.';
      setStatus({ type: 'danger', msg });
    }
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Asignar Curso a Participante</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Asignar Curso</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-link me-1"></i>
          Asignación de Curso
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label className="form-label">Participante</label>
              <Select
                options={participants}
                value={selectedParticipant}
                onChange={setSelectedParticipant}
                placeholder="Seleccionar participante..."
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Curso</label>
              <select
                className="form-select"
                value={selectedCourse}
                onChange={e => setSelectedCourse(e.target.value)}
              >
                <option value="">-- Seleccionar curso --</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>
                    {course.name} ({course.career} - Semestre {course.semester})
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary">
              Asignar Curso
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}