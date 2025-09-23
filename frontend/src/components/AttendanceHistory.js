// src/components/AttendanceHistory.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function AttendanceHistory() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/asistencias');
        setRecords(response.data);
      } catch (error) {
        console.error('Error al obtener asistencias:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAttendance();
  }, []);

  return (
    <div className="container mt-4">
      <h4>📋 Historial de Asistencias</h4>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <table className="table table-striped mt-3">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Fecha</th>
              <th>Hora</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r, i) => {
              const date = new Date(r.timestamp);
              return (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{date.toLocaleDateString()}</td>
                  <td>{date.toLocaleTimeString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
