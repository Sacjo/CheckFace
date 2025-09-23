import React, { useState } from 'react';
import axios from 'axios';

export default function RegistrarCurso() {
  const [formData, setFormData] = useState({
    name: '',
    career: '',
    semester: '',
  });

  const [status, setStatus] = useState(null);

  const onChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const onSubmit = async e => {
    e.preventDefault();

    const { name, career, semester } = formData;

    if (!name.trim() || !career.trim() || !semester.trim()) {
      setStatus({ type: 'danger', msg: 'Todos los campos son obligatorios.' });
      return;
    }

    try {
      await axios.post(
        'http://127.0.0.1:5000/api/courses',
        {
          name,
          career,
          semester: parseInt(semester),
        },
        { headers: { 'Content-Type': 'application/json' } }
      );

      setStatus({ type: 'success', msg: 'Curso registrado correctamente.' });
      setFormData({ name: '', career: '', semester: '' });
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar el curso.' });
    }
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Nuevo Curso</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Curso</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-book me-1"></i>
          Datos del Curso
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label htmlFor="name" className="form-label">Nombre del Curso</label>
              <input
                type="text"
                id="name"
                name="name"
                className="form-control"
                value={formData.name}
                onChange={onChange}
              />
            </div>

            <div className="mb-3">
              <label htmlFor="career" className="form-label">Carrera</label>
              <select
                id="career"
                name="career"
                className="form-select"
                value={formData.career}
                onChange={onChange}
              >
                <option value="">-- Seleccionar carrera --</option>
                <option value="Análisis de Sistemas">Análisis de Sistemas</option>
                <option value="Turismo">Turismo</option>
                <option value="Ingeniería Eléctrica">Ingeniería Eléctrica</option>
                <option value="Ingeniería en Sistemas">Ingeniería en Sistemas</option>
              </select>
            </div>

            <div className="mb-3">
              <label htmlFor="semester" className="form-label">Semestre</label>
              <select
                id="semester"
                name="semester"
                className="form-select"
                value={formData.semester}
                onChange={onChange}
              >
                <option value="">-- Seleccionar semestre --</option>
                {[...Array(10)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{i + 1}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary">
              Registrar Curso
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}