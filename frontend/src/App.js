// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/sidebar';
import Dashboard from './pages/Dashboard';
import Reconocimiento from './pages/Reconocimiento';
import RegistrarEstudiante from './pages/RegistrarEstudiante';
import RegistrarRol from './pages/RegistrarRol';

function App() {
  return (
    <Router>
      <Sidebar>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/reconocimiento" element={<Reconocimiento />} />
          <Route path="/registrar-estudiante" element={<RegistrarEstudiante />} />
          <Route path="/registrar-rol" element={<RegistrarRol />} />
        </Routes>
      </Sidebar>
    </Router>
  );
}

export default App;