import React from 'react';
import ResumenAsistencias from '../components/ResumenAsistencias';

export default function Dashboard() {
  return (
    <div className="ml-64 p-6">
      <h2 className="text-2xl font-semibold mb-4">📈 Asistencias por Día</h2>
      <ResumenAsistencias />
    </div>
  );
}
