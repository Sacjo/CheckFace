import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function RegistrarEstudiante() {
  const [form, setForm] = useState({
    name: '',
    ci: '',
    email: '',
    password: '',
    role_id: '',
    course_id: '',
  });
  const [files, setFiles] = useState([]);
  const [roles, setRoles] = useState([]);
  const [courses, setCourses] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    // Cargar roles y cursos al montar
    const fetchData = async () => {
      try {
        const [rolesRes, coursesRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/roles'),
          axios.get('http://127.0.0.1:5000/api/courses'),
        ]);
        setRoles(rolesRes.data);
        setCourses(coursesRes.data);
      } catch (err) {
        console.error("Error al cargar roles o cursos:", err);
      }
    };
    fetchData();
  }, []);

  const onFileChange = e => {
    const selected = Array.from(e.target.files).slice(0, 10);
    setFiles(selected);
  };

  const onChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const onSubmit = async e => {
    e.preventDefault();

    if (
      !form.name || !form.ci || !form.email || !form.password ||
      !form.role_id || !form.course_id || files.length < 3
    ) {
      setStatus({
        type: 'danger',
        msg: 'Todos los campos son obligatorios y se requieren al menos 3 imágenes.',
      });
      return;
    }

    const formData = new FormData();
    Object.entries(form).forEach(([key, val]) => formData.append(key, val));
    files.forEach(file => formData.append('images', file));

    try {
      await axios.post(
        'http://127.0.0.1:5000/api/users',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setStatus({ type: 'success', msg: 'Estudiante registrado correctamente' });
      setForm({ name: '', ci: '', email: '', password: '', role_id: '', course_id: '' });
      setFiles([]);
      e.target.reset(); // limpiar input file
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al registrar estudiante';
      setStatus({ type: 'danger', msg });
    }
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Nuevo Estudiante</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Estudiante</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-user-plus me-1"></i>
          Datos del Estudiante
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label className="form-label">Nombre completo</label>
              <input
                type="text"
                name="name"
                className="form-control"
                value={form.name}
                onChange={onChange}
              />
            </div>
            <div className="mb-3">
              <label className="form-label">CI</label>
              <input
                type="text"
                name="ci"
                className="form-control"
                value={form.ci}
                onChange={onChange}
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="email"
                name="email"
                className="form-control"
                value={form.email}
                onChange={onChange}
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Contraseña</label>
              <input
                type="password"
                name="password"
                className="form-control"
                value={form.password}
                onChange={onChange}
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Rol</label>
              <select
                name="role_id"
                className="form-select"
                value={form.role_id}
                onChange={onChange}
              >
                <option value="">Seleccionar rol</option>
                {roles.map(role => (
                  <option key={role.id} value={role.id}>{role.description}</option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <label className="form-label">Curso</label>
              <select
                name="course_id"
                className="form-select"
                value={form.course_id}
                onChange={onChange}
              >
                <option value="">Seleccionar curso</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>
                    {course.name} ({course.career} - Semestre {course.semester})
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <label htmlFor="images" className="form-label">
                Fotografías (mínimo 3 - máximo 10)
              </label>
              <input
                type="file"
                id="images"
                accept="image/*"
                multiple
                className="form-control"
                onChange={onFileChange}
              />
              <small className="text-muted">
                Has seleccionado {files.length} archivo(s).
              </small>
            </div>
            <button type="submit" className="btn btn-primary">
              Registrar Estudiante
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}