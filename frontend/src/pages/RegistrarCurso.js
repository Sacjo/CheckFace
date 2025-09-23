// src/pages/RegistrarCurso.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const API = "http://127.0.0.1:5000/api/courses";

export default function RegistrarCurso() {
  // Form de alta
  const [formData, setFormData] = useState({ name: "", career: "", semester: "" });
  // Listado / estado
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // {type:"success"|"danger"|"info", msg:string}

  // Edición (modal)
  const [editing, setEditing] = useState(null); // {id,name,career,semester} | null
  const [eName, setEName] = useState("");
  const [eCareer, setECareer] = useState("");
  const [eSemester, setESemester] = useState("");

  // ---- helpers ----
  const onChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const loadCourses = async () => {
    try {
      setLoading(true);
      const { data } = await axios.get(API);
      setCourses(Array.isArray(data) ? data : []);
    } catch {
      setStatus({ type: "danger", msg: "No se pudo cargar la lista de cursos." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCourses(); }, []);

  // ---- alta ----
  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);

    const { name, career, semester } = formData;
    if (!name.trim() || !career.trim() || !semester.trim()) {
      setStatus({ type: "danger", msg: "Todos los campos son obligatorios." });
      return;
    }

    try {
      await axios.post(
        API,
        { name: name.trim(), career: career.trim(), semester: parseInt(semester, 10) },
        { headers: { "Content-Type": "application/json" } }
      );
      setStatus({ type: "success", msg: "Curso registrado correctamente." });
      setFormData({ name: "", career: "", semester: "" });
      loadCourses();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al registrar el curso.";
      setStatus({ type: "danger", msg });
    }
  };

  // ---- eliminar ----
  const onDelete = async (id) => {
    if (!window.confirm("¿Eliminar este curso?")) return;
    setStatus(null);
    try {
      await axios.delete(`${API}/${id}`);
      setStatus({ type: "success", msg: "Curso eliminado correctamente." });
      loadCourses();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al eliminar el curso.";
      setStatus({ type: "danger", msg });
    }
  };

  // ---- edición ----
  const openEdit = (c) => {
    setEditing(c);
    setEName(c.name || "");
    setECareer(c.career || "");
    setESemester(String(c.semester ?? ""));
    setStatus(null);
  };

  const saveEdit = async () => {
    if (!editing) return;
    if (!eName.trim() || !eCareer.trim() || !eSemester.trim()) {
      setStatus({ type: "danger", msg: "Todos los campos son obligatorios." });
      return;
    }
    try {
      await axios.put(
        `${API}/${editing.id}`,
        { name: eName.trim(), career: eCareer.trim(), semester: parseInt(eSemester, 10) },
        { headers: { "Content-Type": "application/json" } }
      );
      setStatus({ type: "success", msg: "Curso actualizado correctamente." });
      setEditing(null);
      loadCourses();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al actualizar el curso.";
      setStatus({ type: "danger", msg });
    }
  };

  const closeEdit = () => setEditing(null);

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Nuevo Curso</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
        <li className="breadcrumb-item active">Registrar Curso</li>
      </ol>

      {status && <div className={`alert alert-${status.type}`}>{status.msg}</div>}

      <div className="card mb-4">
        <div className="card-header"><i className="fas fa-book me-1"></i> Datos del Curso</div>
        <div className="card-body">
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label htmlFor="name" className="form-label">Nombre del Curso</label>
              <input id="name" name="name" className="form-control"
                     value={formData.name} onChange={onChange} />
            </div>

            <div className="mb-3">
              <label htmlFor="career" className="form-label">Carrera</label>
              <select id="career" name="career" className="form-select"
                      value={formData.career} onChange={onChange}>
                <option value="">-- Seleccionar carrera --</option>
                <option value="Análisis de Sistemas">Análisis de Sistemas</option>
                <option value="Turismo">Turismo</option>
                <option value="Ingeniería Eléctrica">Ingeniería Eléctrica</option>
                <option value="Ingeniería en Sistemas">Ingeniería en Sistemas</option>
              </select>
            </div>

            <div className="mb-3">
              <label htmlFor="semester" className="form-label">Semestre</label>
              <select id="semester" name="semester" className="form-select"
                      value={formData.semester} onChange={onChange}>
                <option value="">-- Seleccionar semestre --</option>
                {[...Array(10)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{i + 1}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary">Registrar Curso</button>
          </form>
        </div>
      </div>

      {/* Listado */}
      <div className="card">
        <div className="card-header"><i className="fas fa-list me-1"></i> Cursos registrados</div>
        <div className="card-body">
          {loading ? (
            <p>Cargando…</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped table-bordered align-middle">
                <thead>
                  <tr>
                    <th style={{ width: 80 }}>ID</th>
                    <th>Nombre</th>
                    <th>Carrera</th>
                    <th>Semestre</th>
                    <th style={{ width: 200 }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((c) => (
                    <tr key={c.id}>
                      <td>{c.id}</td>
                      <td>{c.name}</td>
                      <td>{c.career}</td>
                      <td>{c.semester}</td>
                      <td className="d-flex gap-2">
                        <button className="btn btn-sm btn-outline-secondary" onClick={() => openEdit(c)}>
                          Editar
                        </button>
                        <button className="btn btn-sm btn-outline-danger" onClick={() => onDelete(c.id)}>
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                  {courses.length === 0 && (
                    <tr><td colSpan={5} className="text-center text-muted">Sin cursos aún</td></tr>
                  )}
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
                  <h5 className="modal-title">Editar curso #{editing.id}</h5>
                  <button type="button" className="btn-close" onClick={closeEdit}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Nombre</label>
                    <input className="form-control" value={eName} onChange={(e) => setEName(e.target.value)} />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Carrera</label>
                    <input className="form-control" value={eCareer} onChange={(e) => setECareer(e.target.value)} />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Semestre</label>
                    <select className="form-select" value={eSemester} onChange={(e) => setESemester(e.target.value)}>
                      <option value="">-- Seleccionar semestre --</option>
                      {[...Array(10)].map((_, i) => (
                        <option key={i + 1} value={i + 1}>{i + 1}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button className="btn btn-secondary" onClick={closeEdit}>Cancelar</button>
                  <button className="btn btn-primary" onClick={saveEdit}
                          disabled={!eName.trim() || !eCareer.trim() || !eSemester.trim()}>
                    Guardar cambios
                  </button>
                </div>
              </div>
            </div>
          </div>
          {/* backdrop */}
          <div className="modal-backdrop fade show"></div>
        </>
      )}
    </div>
  );
}
