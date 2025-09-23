// src/pages/Dashboard.js
import React from 'react';
import ResumenAsistencias from '../components/ResumenAsistencias';
import StudentsTable from '../components/StudentsTable';

export default function Dashboard() {
  return (
    <div className="container-fluid px-4">
      <h1 className="mt-4">Asistencias por Día</h1>

      {/* Card con el gráfico */}
      <div className="card mb-4">
        <div className="card-header">
          <i className="fas fa-chart-bar me-1"></i>
          Asistencias por Día
        </div>
        <div className="card-body">
          <ResumenAsistencias />
        </div>
      </div>

      {/* Tabla de estudiantes debajo del gráfico */}
      <StudentsTable />
    </div>
  );
}
