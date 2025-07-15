// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/sidebar';
import Dashboard from './pages/Dashboard';
import Reconocimiento from './pages/Reconocimiento';

function App() {
  return (
    <Router>
      <Sidebar>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/reconocimiento" element={<Reconocimiento />} />
        </Routes>
      </Sidebar>
    </Router>
  );
}

export default App;
