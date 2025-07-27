// src/components/Sidebar.js
import { NavLink } from 'react-router-dom';
import { useState } from 'react';

export default function Sidebar({ children }) {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  return (
    <div className="d-flex min-vh-100">
      {/* Sidebar */}
      <div
        className={`border-end bg-dark ${collapsed ? 'd-none' : ''}`}
        id="sidebar-wrapper"
        style={{ width: '220px' }}
      >
        <div className="sidebar-heading border-bottom bg-dark text-white px-3 py-4 fw-bold">
          CheckFace
        </div>
        <div className="list-group list-group-flush">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `list-group-item list-group-item-action bg-dark text-white px-4 ${
                isActive ? 'active bg-primary' : ''
              }`
            }
          >
            <i className="fas fa-chart-bar me-2"></i> Dashboard
          </NavLink>
          <NavLink
            to="/reconocimiento"
            className={({ isActive }) =>
              `list-group-item list-group-item-action bg-dark text-white px-4 ${
                isActive ? 'active bg-primary' : ''
              }`
            }
          >
            <i className="fas fa-camera me-2"></i> Reconocimiento Facial
          </NavLink>
          <NavLink
            to="/registrar-estudiante"
            className={({ isActive }) =>
              `list-group-item list-group-item-action bg-dark text-white px-4 ${
                isActive ? 'active bg-primary' : ''
              }`
            }
          >
            <i className="fas fa-user-plus me-2"></i> Registrar Estudiante
          </NavLink>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex-grow-1">
        <nav className="navbar navbar-expand-lg navbar-light bg-light border-bottom px-4">
          <button className="btn btn-outline-primary" onClick={toggleSidebar}>
            <i className="fas fa-bars"></i>
          </button>
        </nav>
        <div className="container-fluid mt-3">{children}</div>
      </div>
    </div>
  );
}
