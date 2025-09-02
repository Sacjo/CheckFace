// src/pages/RegistrarEstudiante.js
import React, { useState } from 'react';
import axios from 'axios';

export default function RegistrarEstudiante() {
  const [name, setName]       = useState('');
  const [files, setFiles]     = useState([]);      // array de imágenes
  const [status, setStatus]   = useState(null);

  const onFileChange = e => {
    // limitar a máximo 10 ficheros
    const selected = Array.from(e.target.files).slice(0, 10);
    setFiles(selected);
  };

  const onSubmit = async e => {
    e.preventDefault();
    // if (!name || files.length >=1) {
    //   setStatus({ 
    //     type: 'danger', 
    //     msg: 'Debe indicar nombre y al menos 5 imágenes (máx 10).' 
    //   });
    //   return;
    // }

    const formData = new FormData();
    formData.append('name', name);
    files.forEach((f, idx) => {
      formData.append('images', f);  // backend recibirá lista en request.files.getlist('images')
    });

    try {
      await axios.post(
        'http://127.0.0.1:5000/api/students',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setStatus({ type: 'success', msg: 'Estudiante registrado correctamente' });
      setName('');
      setFiles([]);
      // limpiar input file
      e.target.reset();
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al registrar estudiante' });
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
              <label htmlFor="name" className="form-label">Nombre completo</label>
              <input
                type="text"
                id="name"
                className="form-control"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="images" className="form-label">
                Fotografías (5 a 10 imágenes)
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
              Registrar
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
