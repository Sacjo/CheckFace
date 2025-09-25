// src/components/ResumenAsistencias.jsx
import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';

const API_RESUMEN = 'http://127.0.0.1:5000/api/asistencias/resumen';
const API_COURSES = 'http://127.0.0.1:5000/api/courses';

function fmt(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const da = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${da}`;
}

export default function ResumenAsistencias() {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  // fechas por defecto: últimos 7 días
  const today = new Date();
  const last7 = new Date(today); last7.setDate(today.getDate() - 6);
  const [from, setFrom] = useState(fmt(last7));
  const [to, setTo]   = useState(fmt(today));
  const [courseId, setCourseId] = useState('');

  // cursos para el filtro
  useEffect(() => {
    axios.get(API_COURSES)
      .then(res => setCourses(Array.isArray(res.data) ? res.data : []))
      .catch(() => setCourses([]));
  }, []);

  const fetchResumen = async () => {
    try {
      setLoading(true);
      setStatus(null);

      const params = { from, to };
      if (courseId) params.course_id = courseId;

      const { data } = await axios.get(API_RESUMEN, { params });
      const labels = data.map(d => d.date);
      const values = data.map(d => d.count);

      drawChart(labels, values);
    } catch (err) {
      console.error(err);
      setStatus({ type: 'danger', msg: 'Error al cargar el resumen.' });
      drawChart([], []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumen();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const drawChart = (labels, values) => {
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }

    chartRef.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Asistencias',
          data: values,
          backgroundColor: 'rgba(78, 115, 223, 0.5)',
          borderColor: 'rgba(78, 115, 223, 1)',
          borderWidth: 1,
          hoverBackgroundColor: 'rgba(78, 115, 223, 0.7)',
          hoverBorderColor: 'rgba(78, 115, 223, 1)',
          maxBarThickness: 44,
        }],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: ctx => ` ${ctx.parsed.y} asistencias` }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              callback: (_, idx) => {
                const iso = labels[idx] || '';
                const [Y, M, D] = iso.split('-');
                return `${D}/${M}`;
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(234, 236, 244, 1)' },
            ticks: { precision: 0 }
          }
        }
      },
    });
  };

  const onApply = (e) => {
    e.preventDefault();
    fetchResumen();
  };

  const onClear = () => {
    const t = new Date();
    const f = new Date(t); f.setDate(t.getDate() - 6);
    setFrom(fmt(f));
    setTo(fmt(t));
    setCourseId('');
    setTimeout(fetchResumen, 0);
  };

  return (
    <div>
      {/* Filtros responsivos y compactos */}
      <form className="row g-2 g-md-3 align-items-end mb-3" onSubmit={onApply}>
        <div className="col-6 col-md-3">
          <label className="form-label mb-1">Desde</label>
          <input
            type="date"
            className="form-control form-control-sm"
            value={from}
            onChange={e => setFrom(e.target.value)}
          />
        </div>
        <div className="col-6 col-md-3">
          <label className="form-label mb-1">Hasta</label>
          <input
            type="date"
            className="form-control form-control-sm"
            value={to}
            onChange={e => setTo(e.target.value)}
          />
        </div>
        <div className="col-12 col-md-4">
          <label className="form-label mb-1">Curso</label>
          <select
            className="form-select form-select-sm"
            value={courseId}
            onChange={e => setCourseId(e.target.value)}
          >
            <option value="">Todos</option>
            {courses.map(c => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.career} - Sem {c.semester})
              </option>
            ))}
          </select>
        </div>
        <div className="col-12 col-md-2 d-flex gap-2 justify-content-end justify-content-md-start">
          <button type="submit" className="btn btn-primary btn-sm">{loading ? '...' : 'Aplicar'}</button>
          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={onClear}>Limpiar</button>
        </div>
      </form>

      {status && <div className={`alert alert-${status.type} py-2`}>{status.msg}</div>}

      {/* Contenedor del gráfico (alto fijo razonable y 100% ancho) */}
      <div style={{ width: '100%', height: 300 }}>
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
}
