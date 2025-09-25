// src/components/StudentsTable.js
import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

export default function StudentsTable() {
  // filtros
  const [q, setQ] = useState("");
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState("");
  const [from, setFrom] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 6);
    return d;
  });
  const [to, setTo] = useState(() => new Date());
  const [minPct, setMinPct] = useState("");

  // datos
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  // cursos para select
  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/api/courses")
      .then((res) => setCourses(res.data || []))
      .catch(() => setCourses([]));
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setStatus(null);

      const params = {
        q: q || "",
        course_id: courseId || "",
        from: from ? from.toISOString().slice(0, 10) : "",
        to: to ? to.toISOString().slice(0, 10) : "",
      };
      if (minPct !== "") params.min_pct = minPct;

      const { data } = await axios.get(
        "http://127.0.0.1:5000/api/participants-attendance-summary",
        { params }
      );
      setRows(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setRows([]);
      setStatus({ type: "danger", msg: "Error al listar participantes." });
    } finally {
      setLoading(false);
    }
  };

  // carga inicial
  useEffect(() => {
    fetchSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const clearFilters = () => {
    setQ("");
    setCourseId("");
    const d1 = new Date();
    d1.setDate(d1.getDate() - 6);
    setFrom(d1);
    setTo(new Date());
    setMinPct("");
    fetchSummary();
  };

  const filtered = useMemo(() => rows, [rows]);

  // ============== Exportaciones ==============
  const exportCSV = () => {
    const headers = [
      "Nombre",
      "CI",
      "Curso",
      "Asistencias",
      "Programadas",
      "% Asistencia",
    ];

    const csvRows = [
      headers.join(","),
      ...filtered.map((r) =>
        [
          `"${r.full_name.replace(/"/g, '""')}"`,
          `"${r.ci}"`,
          `"${r.course_name.replace(/"/g, '""')}"`,
          r.total_attended,
          r.total_scheduled,
          r.pct,
        ].join(",")
      ),
    ];
    const blob = new Blob([csvRows.join("\n")], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "asistencias_resumen.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportXLSX = () => {
    const wsData = filtered.map((r) => ({
      Nombre: r.full_name,
      CI: r.ci,
      Curso: r.course_name,
      Asistencias: r.total_attended,
      Programadas: r.total_scheduled,
      "% Asistencia": r.pct,
    }));
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(wsData);
    XLSX.utils.book_append_sheet(wb, ws, "Resumen");
    XLSX.writeFile(wb, "asistencias_resumen.xlsx");
  };

  const exportPDF = () => {
    const doc = new jsPDF({ orientation: "landscape" });
    doc.setFontSize(14);
    doc.text("Resumen de Asistencias", 14, 14);

    const head = [
      ["Nombre", "CI", "Curso", "Asistencias", "Programadas", "% Asistencia"],
    ];
    const body = filtered.map((r) => [
      r.full_name,
      r.ci,
      r.course_name,
      r.total_attended,
      r.total_scheduled,
      r.pct,
    ]);

    doc.autoTable({
      head,
      body,
      startY: 20,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [41, 128, 185] },
    });

    doc.save("asistencias_resumen.pdf");
  };

  return (
    <div className="card">
      <div className="card-header">
        <i className="fas fa-list me-1" /> Lista de Estudiantes
      </div>

      <div className="card-body">
        {/* Filtros */}
        <div className="row g-3 align-items-end">
          <div className="col-md-4">
            <label className="form-label">Nombre o CI</label>
            <input
              className="form-control"
              placeholder="Buscar..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchSummary()}
            />
          </div>

          <div className="col-md-3">
            <label className="form-label">Curso</label>
            <select
              className="form-select"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
            >
              <option value="">Todos</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.career} - Sem {c.semester})
                </option>
              ))}
            </select>
          </div>

          <div className="col-md-2">
            <label className="form-label">Desde</label>
            <DatePicker
              selected={from}
              onChange={setFrom}
              className="form-control"
              dateFormat="MM/dd/yyyy"
            />
          </div>
          <div className="col-md-2">
            <label className="form-label">Hasta</label>
            <DatePicker
              selected={to}
              onChange={setTo}
              className="form-control"
              dateFormat="MM/dd/yyyy"
            />
          </div>

          <div className="col-md-1 d-grid">
            <button className="btn btn-primary" onClick={fetchSummary}>
              Aplicar
            </button>
          </div>
        </div>

        <div className="row g-3 align-items-end mt-1">
          <div className="col-md-2">
            <label className="form-label">% mínimo</label>
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              className="form-control"
              value={minPct}
              onChange={(e) => setMinPct(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchSummary()}
              placeholder="p.ej. 75"
            />
          </div>
          <div className="col-md-2 d-grid">
            <button className="btn btn-outline-secondary" onClick={clearFilters}>
              Limpiar
            </button>
          </div>

          {/* Exportaciones */}
          <div className="col-md-8 d-flex justify-content-end gap-2">
            <button className="btn btn-outline-primary" onClick={exportCSV}>
              <i className="fas fa-file-csv me-1" />
              CSV
            </button>
            <button className="btn btn-outline-success" onClick={exportXLSX}>
              <i className="fas fa-file-excel me-1" />
              XLSX
            </button>
            <button className="btn btn-outline-danger" onClick={exportPDF}>
              <i className="fas fa-file-pdf me-1" />
              PDF
            </button>
          </div>
        </div>

        {/* Estado */}
        {status && (
          <div className={`alert alert-${status.type} mt-3`} role="alert">
            {status.msg}
          </div>
        )}

        {/* Tabla */}
        <div className="table-responsive mt-3">
          {loading ? (
            <p className="mb-0">Cargando…</p>
          ) : filtered.length === 0 ? (
            <p className="text-muted mb-0">No hay registros que coincidan con los filtros.</p>
          ) : (
            <table className="table table-striped table-bordered align-middle">
              <thead className="table-light" style={{ position: "sticky", top: 0, zIndex: 1 }}>
                <tr>
                  <th>Nombre</th>
                  <th>CI</th>
                  <th>Curso</th>
                  <th>Asistencias</th>
                  <th>Programadas</th>
                  <th>% Asistencia</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r, idx) => (
                  <tr key={`${r.participant_id}-${r.course_id}-${idx}`}>
                    <td>{r.full_name}</td>
                    <td>{r.ci}</td>
                    <td>{r.course_name}</td>
                    <td>{r.total_attended}</td>
                    <td>{r.total_scheduled}</td>
                    <td>{r.pct}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
