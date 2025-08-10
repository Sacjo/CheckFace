// src/components/EditStudentModal.js
import React, { useState } from 'react';
import axios from 'axios';

export default function EditStudentModal({ student, onClose, onSaved }) {
  const [name, setName] = useState(student?.name || '');
  const [files, setFiles] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const fd = new FormData();
      if (name && name !== student.name) fd.append('name', name);
      Array.from(files).forEach(f => fd.append('images', f));
      await axios.put(`http://127.0.0.1:5000/api/students/${student.id}`, fd);
      onSaved();   // refrescar tabla
      onClose();   // cerrar modal
    } catch (err) {
      console.error('Update error:', err);
      alert(err.response?.data?.error || 'No se pudo actualizar');
    }
  };

  if (!student) return null;

  return (
    <div className="modal fade show" style={{ display: 'block', background: 'rgba(0,0,0,.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Editar Estudiante #{student.id}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="mb-3">
                <label className="form-label">Nombre</label>
                <input
                  className="form-control"
                  value={name}
                  onChange={e => setName(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Agregar fotos (opcional)</label>
                <input
                  type="file"
                  className="form-control"
                  multiple
                  accept="image/*"
                  onChange={e => setFiles(e.target.files)}
                />
                <small className="text-muted">Se reentrenará al guardar si subes nuevas fotos.</small>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" type="button" onClick={onClose}>Cancelar</button>
              <button className="btn btn-primary" type="submit">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
