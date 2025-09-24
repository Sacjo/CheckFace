// src/pages/RegistrarRol.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";
const API_ROLES = `${API_BASE}/api/roles`;

export default function RegistrarRol() {
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState(null);   // { type: "success"|"danger", msg: string }
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);

  // estado del modal de edición
  const [editing, setEditing] = useState(null); // { id, description } | null
  const [editDesc, setEditDesc] = useState("");

  const loadRoles = async () => {
    try {
      setLoading(true);
      const { data } = await axios.get(API_ROLES);
      setRoles(Array.isArray(data) ? data : []);
    } catch {
      setStatus({ type: "danger", msg: "No se pudo cargar la lista de roles." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadRoles(); }, []);

  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);

    if (!description.trim()) {
      setStatus({ type: "danger", msg: "Debe ingresar una descripción de rol." });
      return;
    }

    try {
      await axios.post(
        API_ROLES,
        { description: description.trim() },
        { headers: { "Content-Type": "application/json" } }
      );
      setDescription("");
      setStatus({ type: "success", msg: "Rol registrado correctamente." });
      loadRoles();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al registrar el rol.";
      setStatus({ type: "danger", msg });
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar este rol?")) return;
    setStatus(null);
    try {
      await axios.delete(`${API_ROLES}/${id}`);
      setStatus({ type: "success", msg: "Rol eliminado correctamente." });
      loadRoles();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al eliminar el rol.";
      setStatus({ type: "danger", msg });
    }
  };

  // ---- edición ----
  const openEdit = (role) => {
    setEditing(role);
    setEditDesc(role.description || "");
    setStatus(null);
  };

  const saveEdit = async () => {
    if (!editing) return;
    const newDesc = editDesc.trim();
    if (!newDesc) {
      setStatus({ type: "danger", msg: "La descripción no puede estar vacía." });
      return;
    }
    if (newDesc === editing.description) {
      setStatus({ type: "info", msg: "No hay cambios para guardar." });
      return;
    }
    try {
      await axios.put(`${API_ROLES}/${editing.id}`, { description: newDesc }, {
        headers: { "Content-Type": "application/json" }
      });
      setStatus({ type: "success", msg: "Rol actualizado correctamente." });
      setEditing(null);
      loadRoles();
    } catch (err) {
      const msg = err?.response?.data?.message || err?.response?.data?.error || "Error al actualizar el rol.";
      setStatus({ type: "danger", msg });
    }
  };

  const closeEdit = () => setEditing(null);

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Nuevo Rol</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
        <li className="breadcrumb-item active">Registrar Rol</li>
      </ol>

      {status && (
        <div className={`alert alert-${status.type}`} role="alert">
          {status.msg}
        </div>
      )}

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-user-shield me-1"></i> Datos del Rol
        </div>
        <div className="card-body">
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label htmlFor="description" className="form-label">Descripción del Rol</label>
              <input
                type="text"
                id="description"
                className="form-control"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                
              />
            </div>
            <button type="submit" className="btn btn-primary">Registrar Rol</button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <i className="fas fa-list me-1"></i> Roles registrados
        </div>
        <div className="card-body">
          {loading ? (
            <p>Cargando…</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped table-bordered align-middle">
                <thead>
                  <tr>
                    <th style={{ width: 80 }}>ID</th>
                    <th>Descripción</th>
                    <th style={{ width: 200 }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {roles.map((r) => (
                    <tr key={r.id}>
                      <td>{r.id}</td>
                      <td>{r.description}</td>
                      <td className="d-flex gap-2">
                        <button className="btn btn-sm btn-outline-secondary" onClick={() => openEdit(r)}>
                          Editar
                        </button>
                        <button className="btn btn-sm btn-outline-danger" onClick={() => onDelete(r.id)}>
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                  {roles.length === 0 && (
                    <tr><td colSpan={3} className="text-center text-muted">Sin roles aún</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de edición (simple, sin libs) */}
      {editing && (
        <>
          <div className="modal show d-block" tabIndex="-1" role="dialog">
            <div className="modal-dialog" role="document">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Editar rol #{editing.id}</h5>
                  <button type="button" className="btn-close" onClick={closeEdit}></button>
                </div>
                <div className="modal-body">
                  <label className="form-label">Descripción</label>
                  <input
                    className="form-control"
                    value={editDesc}
                    onChange={(e) => setEditDesc(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeEdit}>Cancelar</button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={saveEdit}
                    disabled={!editDesc.trim()}
                  >
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
