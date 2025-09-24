// src/components/CameraCapture.js

// mejorar el reconocmiento, cuando inice el reconomiento, limpiar los nombres pendientes
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
  const [conteoNombres, setConteoNombres] = useState({});
  const today = new Date().toISOString().split("T")[0];
  const [cursoSeleccionado, setCursoSeleccionado] = useState("");
  const conteoRef = useRef({});


  useEffect(() => {
    conteoRef.current = conteoNombres;
  }, [conteoNombres]);

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
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
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

      const reconocidos = (Array.isArray(response.data) ? response.data : [])
        .filter(m => m.match && m.name && !isNaN(Number(m.name)))
        .map(m => Number(m.name));

      console.log("✅ IDs reconocidos válidos (CI):", reconocidos);

      if (reconocidos.length > 0) {
        setConteoNombres((prevConteo) => {
          const nuevoConteo = { ...prevConteo };
          reconocidos.forEach((id) => {
            nuevoConteo[id] = (nuevoConteo[id] || 0) + 1;
            console.log(`📊 CI ${id} → ${nuevoConteo[id]} capturas`);
          });
          return nuevoConteo;
        });
      }
      console.log("📷 Respuesta reconocimiento:", response.data);
    } catch (error) {
      console.error('Error en reconocimiento:', error);
      setResult({ error: 'Error en el reconocimiento' });
    }

  };

  // 3. Inicia la captura periódica
  // Reemplazar al iniciar el reconocimiento
  const startCapturing = async () => {
    yaEnviado = false;
    if (intervalId) clearInterval(intervalId);
    setNombresPendientes([]);
    setConteoNombres({});
    setRegistroConfirmado(false);
    setResult(null);

    try {
      const res = await axios.get("http://127.0.0.1:5000/api/current_course");
      const cursoActivo = res.data;

      if (!cursoActivo || !cursoActivo.course_id) {
        setCursoSeleccionado("");
        setRegistroConfirmado(false);
        setNombresPendientes([]);
        setResult(null);
        alert("⚠️ No hay curso activo para esta hora y fecha.");
        return;
      }

      setCursoSeleccionado(cursoActivo);

      setCapturing(true);
      const id = setInterval(captureAndSend, 2000);
      setIntervalId(id);

      setTimeout(async () => {
        clearInterval(id);

        console.log("conteoNombres (ref):", conteoRef.current);

        const idsFiltrados = Object.entries(conteoRef.current)
          .filter(([ci, count]) => Number.isFinite(Number(ci)) && count >= 3)
          .map(([ci]) => String(ci));

        console.log("📸 IDs reconocidos por >=3 capturas:", idsFiltrados);

        if (!yaEnviado && idsFiltrados.length > 0) {
          yaEnviado = true;

          try {
            const registradosRes = await axios.get(
              "http://127.0.0.1:5000/api/asistencia/registrados",
              {
                params: {
                  course_id: cursoActivo.course_id,
                  date: today,
                },
              }
            );

            const yaRegistrados = registradosRes.data.registrados || [];
            console.log("🗂 Lista ya en DB:", yaRegistrados);

            yaRegistrados.forEach(r => {
              console.log("👉 DB CI:", r.ci, " | typeof:", typeof r.ci);
            });
            idsFiltrados.forEach(ci => {
              console.log("👉 Reconocido CI:", ci, " | typeof:", typeof ci);
            });

            console.log("🔎 Comparando:", idsFiltrados, yaRegistrados.map(r => r.ci));
            const nuevosIds = idsFiltrados.filter(
              ci => !yaRegistrados.some(r => String(r.ci) === String(ci))
            );
            console.log("🆕 CIs realmente nuevos:", nuevosIds);


            const nuevosDetalles = nuevosIds.map(ci => {
              const match = result.find(r => r.name === ci); // r.name es el CI reconocido
              return match
                ? { ci, full_name: match.full_name || "Desconocido" }
                : { ci, full_name: "Desconocido" };
            });

            if (nuevosDetalles.length === 0) {
              console.log("⚠️ Todos ya estaban registrados. No se envía nada.");
              setRegistroConfirmado(false);
              setNombresPendientes([]);
              setCapturing(false);
              return;
            }

            const postRes = await axios.post(
              "http://127.0.0.1:5000/api/asistencia",
              {
                cis: nuevosIds,
                course_id: cursoActivo.course_id,
                date: today,
              }
            );

            console.log("✅ Asistencia enviada:", postRes.data);


            const { fuera_curso } = postRes.data;

            const detallesFinales = nuevosDetalles.filter(
              p => !fuera_curso.includes(p.ci)
            );

            if (detallesFinales.length > 0) {
              setRegistroConfirmado(true);
              setNombresPendientes(detallesFinales);
            } else {
              setRegistroConfirmado(false);
              setNombresPendientes([]);
            }


          } catch (err) {
            console.error("❌ Error al verificar/enviar asistencia:", err);
          }
        }

        setCapturing(false);
      }, 15000);
    } catch (error) {
      console.error("Error al obtener curso activo:", error);
      alert("Error al verificar el curso activo.");
    }
  };

  // Limpieza de intervalos
  useEffect(() => () => clearInterval(intervalId), [intervalId]);

  return (
    <div className="container text-center mt-4">
      <h3>Reconocimiento Facial (Automático)</h3>

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

      {cursoSeleccionado && (
        <div className="alert alert-info mt-3">
          📘 Curso activo: {cursoSeleccionado.name} - {cursoSeleccionado.career} ({cursoSeleccionado.semester}° semestre)
        </div>
      )}

      {registroConfirmado && nombresPendientes.length > 0 ? (
        <>
          <div className="alert alert-success mt-4">
            ✅ Asistencia registrada correctamente
          </div>

          <div className="mt-4">
            <h5>🟢 Estudiantes registrados:</h5>
            <ul className="list-group">
              {nombresPendientes.map((p, idx) => (
                <li key={idx} className="list-group-item">
                  {p.ci}
                </li>
              ))}
            </ul>
          </div>
        </>
      ) : (
        <div className="alert alert-info mt-4">
          📌 Todos los estudiantes ya estaban registrados.
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
