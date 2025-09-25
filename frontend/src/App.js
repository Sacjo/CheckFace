// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom";

// ⚠️ Ajusta la ruta y el nombre del archivo según exista en tu proyecto:
//   - Si el archivo es "components/sidebar.jsx": usa la siguiente línea.
import Sidebar from "./components/sidebar";
//   - Si el archivo es "components/Sidebar.jsx": cambia por:
// import Sidebar from "./components/Sidebar";

// Páginas públicas
import Login from "./pages/Login";
import Register from "./pages/Register";

// Páginas privadas
import Dashboard from "./pages/Dashboard";
import Reconocimiento from "./pages/Reconocimiento";
import RegistrarEstudiante from "./pages/RegistrarEstudiante";
import RegistrarRol from "./pages/RegistrarRol";
import RegistrarCurso from "./pages/RegistrarCurso";
import RegistrarHorarioCurso from "./pages/RegistrarHorarioCurso";
import RegistrarAsistenciaManual from './pages/RegistrarAsistenciaManual';
import AsignarCurso from './pages/AsignarCurso';

// --- Guards ---
const isAuth = () => {
  try {
    const u = JSON.parse(localStorage.getItem("user"));
    return !!u;
  } catch {
    return false;
  }
};

const ProtectedRoute = () => (isAuth() ? <Outlet /> : <Navigate to="/login" replace />);
const PublicOnlyRoute = () => (!isAuth() ? <Outlet /> : <Navigate to="/dashboard" replace />);

// --- Layouts ---
const AppLayout = () => (
  <Sidebar>
    <Outlet />
  </Sidebar>
);

const AuthLayout = () => (
  // Sin sidebar; usa el fondo claro de SB Admin si quieres
  <Outlet />
);


function App() {
  return (
    <Router>
      <Routes>
        {/* Entra por /login; si ya hay sesión, PublicOnlyRoute te manda a /dashboard */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Rutas públicas (sin Sidebar) */}
        <Route element={<PublicOnlyRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>
        </Route>

        {/* Rutas privadas (con Sidebar) */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/reconocimiento" element={<Reconocimiento />} />
            <Route path="/registrar-estudiante" element={<RegistrarEstudiante />} />
            <Route path="/registrar-rol" element={<RegistrarRol />} />
            <Route path="/registrar-curso" element={<RegistrarCurso />} />
            <Route path="/registrar-horario" element={<RegistrarHorarioCurso />} />
            <Route path="/registrar-asistencia" element={<RegistrarAsistenciaManual />} />
            <Route path="/asignar-curso" element={<AsignarCurso />} />
          </Route>
        </Route>

        {/* 404 → login (la guarda redirige a dashboard si estás logueado) */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;