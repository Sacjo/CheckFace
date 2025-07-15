import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

const ResumenAsistencias = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/asistencias/resumen')
      .then(response => setData(response.data))
      .catch(error => console.error('Error al cargar resumen:', error));
  }, []);

  return (
    <div className="container mt-5">
      <h4>📊 Asistencias por Día</h4>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="fecha" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="cantidad" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ResumenAsistencias;
