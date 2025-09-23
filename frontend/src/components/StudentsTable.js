// src/components/StudentsTable.js
import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import 'datatables.net-dt';
import EditStudentModal from './EditStudentModal';
import $ from 'jquery';

export default function StudentsTable() {
  const [data, setData] = useState([]);
  const [editTarget, setEditTarget] = useState(null);
  const tableRef = useRef(null);

  const fetchData = () =>
    axios.get('http://127.0.0.1:5000/api/students/summary')
      .then(res => setData(res.data))
      .catch(err => console.error('Error fetching students:', err));

  useEffect(() => { fetchData(); }, []);

  useEffect(() => {
    if (!tableRef.current) return;

    // destruir instancia previa si existe
    if ($.fn.DataTable.isDataTable(tableRef.current)) {
      $(tableRef.current).DataTable().clear().destroy();
    }
    if (!data.length) return;

    const dt = $(tableRef.current).DataTable({
      data,
      columns: [
        { title: 'ID', data: 'id' },
        { title: 'Nombre', data: 'name' },
        {
          title: 'Última asistencia',
          data: 'last_attendance',
          render: (d) => d ? new Date(d).toLocaleString() : '-'
        },
        { title: '# Fotos', data: 'photo_count' },
        {
          title: 'Acciones',
          data: null,
          orderable: false,
          searchable: false,
          render: (row) => `
            <button class="btn btn-sm btn-outline-primary btn-edit" data-id="${row.id}">
              <i class="fas fa-pen"></i> Editar
            </button>
            <button class="btn btn-sm btn-outline-danger btn-delete ms-2" data-id="${row.id}">
              <i class="fas fa-trash"></i> Eliminar
            </button>
          `
        }
      ],
      pageLength: 10,
      lengthMenu: [5, 10, 15, 20],
      dom: 'Bfrtip',
      buttons: [
        { extend: 'copy',  text: 'Copiar' },
        { extend: 'csv',   text: 'CSV' },
        { extend: 'excel', text: 'Excel' },
        { extend: 'pdf',   text: 'PDF' },
        { extend: 'print', text: 'Imprimir' }
      ],
    });

    // eventos de acciones
    $(tableRef.current).on('click', '.btn-edit', function () {
      const id = $(this).data('id');
      const target = data.find(s => s.id === id);
      if (target) setEditTarget(target);
    });

    $(tableRef.current).on('click', '.btn-delete', async function () {
      const id = $(this).data('id');
      if (!window.confirm(`¿Eliminar estudiante #${id}?`)) return;
      try {
        await axios.delete(`http://127.0.0.1:5000/api/students/${id}`);
        fetchData();
      } catch (err) {
        console.error('Error eliminando:', err);
        alert('No se pudo eliminar');
      }
    });

    return () => {
      if ($.fn.DataTable.isDataTable(tableRef.current)) {
        $(tableRef.current).DataTable().off('click', '.btn-edit');
        $(tableRef.current).DataTable().off('click', '.btn-delete');
        $(tableRef.current).DataTable().clear().destroy();
      }
    };
  }, [data]);

  return (
    <div className="card mb-4">
      <div className="card-header">
        <i className="fas fa-table me-1"></i>
        Lista de Estudiantes
      </div>
      <div className="card-body">
        <table ref={tableRef} className="display" style={{ width: '100%' }} />
      </div>

      {editTarget && (
        <EditStudentModal
          student={editTarget}
          onClose={() => setEditTarget(null)}
          onSaved={fetchData}
        />
      )}
    </div>
  );
}
