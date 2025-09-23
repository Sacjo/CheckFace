// src/pages/RegistrarRol.js
import React, { useState } from 'react';
import axios from 'axios';

export default function RegistrarRol() {
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState(null);

  const onSubmit = async e => {
    e.preventDefault();

    if (!description.trim()) {
      setStatus({ type: 'danger', msg: 'Debe ingresar una descripción de rol.' });
      return;
    }

    try {
      await axios.post(
        'http://127.0.0.1:5000/api/roles',
        { description }, // Enviamos JSON simple
        { headers: { 'Content-Type': 'application/json' } }
      );

      setStatus({ type: 'success', msg: 'Rol registrado correctamente.' });
      setDescription('');
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar el rol.' });
    }
  };

  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Registrar Nuevo Rol</h1>
      <ol className="breadcrumb mb-4">
        <li className="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li className="breadcrumb-item active">Registrar Rol</li>
      </ol>

      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-user-shield me-1"></i>
          Datos del Rol
        </div>
        <div className="card-body">
          {status && (
            <div className={`alert alert-${status.type}`} role="alert">
              {status.msg}
            </div>
          )}
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label htmlFor="description" className="form-label">
                Descripción del Rol
              </label>
              <input
                type="text"
                id="description"
                className="form-control"
                value={description}
                onChange={e => setDescription(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Registrar Rol
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}