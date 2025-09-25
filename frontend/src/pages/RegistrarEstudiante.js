// src/pages/RegistrarEstudiante.js
import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Select from 'react-select';

export default function RegistrarEstudiante() {
  const [form, setForm] = useState({
    user_id: '',
    course_id: '',
    full_name: '',
    ci: '',
    occupation: ''
  });
  const [files, setFiles] = useState([]);
  const [users, setUsers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [status, setStatus] = useState(null);

  // ---------- carga combos ----------
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersRes, coursesRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/users/available'),
          axios.get('http://127.0.0.1:5000/api/courses'),
        ]);
        const userOptions = usersRes.data.map(u => ({
          value: u.id,
          label: `${u.username} (ID ${u.id})`
        }));
        setUsers(userOptions);
        setCourses(coursesRes.data);
      } catch (err) {
        console.error("Error al cargar usuarios o cursos:", err);
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

  const onUserSelect = selected => {
    setForm({ ...form, user_id: selected?.value || '' });
  };

  const onSubmit = async e => {
    e.preventDefault();

    if (!form.user_id || !form.course_id || !form.full_name || !form.ci || files.length < 3) {
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
        'http://127.0.0.1:5000/api/participants',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setStatus({ type: 'success', msg: 'Participante registrado correctamente' });
      setForm({ user_id: '', course_id: '', full_name: '', ci: '', occupation: '' });
      setFiles([]);
      e.target.reset();

      // refrescar listado
      await loadParticipantsUnique();
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al registrar participante';
      setStatus({ type: 'danger', msg });
    }
  };

  // =====================================================
  //  NUEVO: listado "1 fila por alumno" (participants-unique)
  // =====================================================
  const [participants, setParticipants] = useState([]);
  const [loadingList, setLoadingList] = useState(false);

  // Filtros (sin ocupación)
  const [q, setQ] = useState('');
  const [fCourseId, setFCourseId] = useState(''); // '' = todos

  const loadParticipantsUnique = async () => {
    try {
      setLoadingList(true);
      const params = {};
      if (q) params.q = q;
      if (fCourseId) params.course_id = fCourseId;

      const { data } = await axios.get(
        'http://127.0.0.1:5000/api/participants-unique',
        { params }
      );
      setParticipants(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setParticipants([]);
      setStatus({ type: 'danger', msg: 'Error al listar participantes.' });
    } finally {
      setLoadingList(false);
    }
  };

  // cargar al entrar y cada vez que cambian filtros
  useEffect(() => {
    loadParticipantsUnique();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, fCourseId]);

  // (opcional) filtro adicional en cliente si quieres refinar por texto
  const filteredParticipants = useMemo(() => {
    return participants; // ya viene filtrado desde el backend
  }, [participants]);

  const clearFilters = () => {
    setQ('');
    setFCourseId('');
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Participante</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Participante</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-user-plus me-1"></i>
          Datos del Participante
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label className="form-label">Seleccionar Usuario</label>
              <Select
                options={users}
                onChange={onUserSelect}
                placeholder="Buscar usuario por nombre o ID..."
                isClearable
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Nombre completo</label>
              <input
                type="text"
                name="full_name"
                className="form-control"
                value={form.full_name}
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

            {/* Si ya no quieres "ocupación" en el alta, elimina este bloque.
                Lo dejo porque lo usabas al registrar. */}
            <div className="mb-3">
              <label className="form-label">Ocupación</label>
              <select
                name="occupation"
                className="form-select"
                value={form.occupation}
                onChange={onChange}
              >
                <option value="">Seleccionar ocupación</option>
                <option value="student">Estudiante</option>
                <option value="teacher">Docente</option>
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
              Registrar Participante
            </button>
          </form>
        </div>
      </div>

      {/* =======================
          LISTA 1 fila por alumno
          ======================= */}
      <div className="card">
        <div className="card-header">
          <i className="fas fa-list me-1"></i> Participantes registrados
        </div>
        <div className="card-body">

          {/* Filtros (sin ocupación) */}
          <div className="row g-3 mb-3">
            <div className="col-md-6 col-lg-5">
              <label className="form-label">Buscar (Nombre o CI)</label>
              <input
                type="text"
                className="form-control"
                placeholder="Ej: Oscar o 123456…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </div>
            <div className="col-md-5 col-lg-4">
              <label className="form-label">Curso</label>
              <select
                className="form-select"
                value={fCourseId}
                onChange={(e) => setFCourseId(e.target.value)}
              >
                <option value="">Todos</option>
                {courses.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.career} - Sem {c.semester})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-1 d-flex align-items-end">
              <button className="btn btn-outline-secondary w-100" onClick={clearFilters}>
                Limpiar
              </button>
            </div>
          </div>

          {/* Tabla */}
          {loadingList ? (
            <p className="mb-0">Cargando…</p>
          ) : filteredParticipants.length === 0 ? (
            <p className="text-muted mb-0">No hay participantes que coincidan con los filtros.</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped table-bordered align-middle">
                <thead>
                  <tr>
                    <th style={{width: 80}}>ID</th>
                    <th>Nombre</th>
                    <th>CI</th>
                    <th>Curso(s)</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredParticipants.map(p => (
                    <tr key={p.id}>
                      <td>{p.id}</td>
                      <td>{p.full_name}</td>
                      <td>{p.ci}</td>
                      <td>{p.course_names || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
