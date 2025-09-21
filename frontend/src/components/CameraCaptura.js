// src/components/CameraCapture.js
import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';

let yaEnviado = false; // ⬅️ Se define una sola vez

export default function CameraCapture() {
  const videoRef = useRef(null);
  const [streamStarted, setStreamStarted] = useState(false);
  const [result, setResult] = useState(null);
  const [capturing, setCapturing] = useState(false);
  const [intervalId, setIntervalId] = useState(null);
  const [registroConfirmado, setRegistroConfirmado] = useState(false);
  const [nombresPendientes, setNombresPendientes] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [cursoSeleccionado, setCursoSeleccionado] = useState("");

  // 1. Arranca la cámara al montar
  useEffect(() => {
    async function startCamera() {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');

        if (videoDevices.length === 0) {
          console.error('No hay cámaras disponibles');
          alert('No se encontró ninguna cámara en este dispositivo.');
          return;
        }

        const deviceId = videoDevices[0].deviceId;

        const stream = await navigator.mediaDevices.getUserMedia({
          video: deviceId ? { deviceId: { exact: deviceId }, width: 640, height: 480 } : true,
          audio: false
        });
        videoRef.current.srcObject = stream;
        setStreamStarted(true);
      } catch (err) {
        console.error('Error al acceder a la cámara:', err);
      }
    }

    startCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  // 2. Captura un frame y envía al backend
  const captureAndSend = async () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg'));
    const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/recognize',
        formData
      );
      setResult(Array.isArray(response.data) ? response.data : []);

      // Extraer nombres únicos reconocidos correctamente
      const nombresReconocidos = response.data
        .filter((match) => match.match)
        .map((match) => match.name);

      // Guardar los reconocidos en una variable de estado global
      if (nombresReconocidos.length > 0) {
        setNombresPendientes((prev) => {
          const nuevos = nombresReconocidos.filter((n) => !prev.includes(n));
          return [...prev, ...nuevos];
        });
      }
    } catch (error) {
      console.error('Error en reconocimiento:', error);
      setResult({ error: 'Error en el reconocimiento' });
    }
  };

  // 3. Inicia la captura periódica
  const startCapturing = () => {
    yaEnviado = false;
    if (!streamStarted || !cursoSeleccionado) {
      alert("Por favor, seleccioná un curso antes de iniciar.");
      return;
    }

    setCapturing(true);
    const id = setInterval(captureAndSend, 2000);
    setIntervalId(id); // guardamos el ID para limpiarlo después

    // Detener luego de 15 segundos
    setTimeout(() => {
      clearInterval(id); // detenemos la captura

      // ⚠️ Muy importante: usamos el último valor de `nombresPendientes`
      setNombresPendientes((currentNombres) => {
        if (!yaEnviado && currentNombres.length > 0 && cursoSeleccionado) {
          yaEnviado = true;
          axios.post("http://127.0.0.1:5000/api/asistencia", {
            names: currentNombres,
            course_id: cursoSeleccionado,
          }, {
            headers: {
              "Content-Type": "application/json"
            }
          })
            .then((res) => {
              console.log("✅ Asistencia enviada:", res.data);
              setRegistroConfirmado(true);
            })
            .catch((err) => {
              console.error("❌ Error al enviar asistencia:", err);
            });
        } else {
          console.warn("⚠️ Ya se envió o no hay nombres válidos.");
        }

        return currentNombres;
      });

      setCapturing(false);
    }, 15000);
  };

  // Limpieza de intervalos
  useEffect(() => () => clearInterval(intervalId), [intervalId]);

  // Cargar cursos desde el backend al montar
  useEffect(() => {
    const fetchCursos = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/courses");
        setCursos(res.data);
      } catch (error) {
        console.error("Error al obtener cursos:", error);
      }
    };

    fetchCursos();
  }, []);

  return (
    <div className="container text-center mt-4">
      <h3>Reconocimiento Facial (Automático)</h3>
      <div className="mt-3">
        <label htmlFor="curso" className="form-label">Seleccionar Curso</label>
        <select
          id="curso"
          className="form-select"
          value={cursoSeleccionado}
          onChange={(e) => setCursoSeleccionado(e.target.value)}
        >
          <option value="">-- Selecciona un curso --</option>
          {cursos.map(c => (
            <option key={c.id} value={c.id}>
              {c.name} - {c.career} ({c.semester}° semestre)
            </option>
          ))}
        </select>
      </div>

      {!streamStarted && (
        <p className="text-danger">Cargando cámara...</p>
      )}

      <div
        style={{
          position: 'relative',
          width: '640px',
          height: '480px',
          margin: '0 auto',
          backgroundColor: '#000'
        }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
        />
      </div>

      <button
        onClick={startCapturing}
        className="btn btn-success mt-3"
        disabled={capturing || !streamStarted}
      >
        {capturing ? 'Reconociendo...' : 'Iniciar Reconocimiento'}
      </button>

      {registroConfirmado && (
        <div className="alert alert-success mt-4">
          ✅ Asistencia registrada correctamente
        </div>
      )}

      {Array.isArray(result) && result.length > 0 && (
        <div className="alert mt-4" style={{ background: '#e8f0fe' }}>
          <h5>Resultados de reconocimiento:</h5>
          <ul className="list-group">
            {result.map((r, idx) => (
              <li key={idx} className="list-group-item d-flex justify-content-between align-items-center">
                <span>{r.match ? '✅' : '❌'} Nombre: {r.name}</span>
                <span>Similitud: {r.similarity?.toFixed(2)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {result?.error && (
        <div className="alert alert-danger mt-4">
          {result.error}
        </div>
      )}
    </div>
  );
}
