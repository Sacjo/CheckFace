// src/components/CameraCapture.js
import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';

export default function CameraCapture() {
  const videoRef = useRef(null);
  const [streamStarted, setStreamStarted] = useState(false);
  const [result, setResult] = useState(null);
  const [capturing, setCapturing] = useState(false);
  const [intervalId, setIntervalId] = useState(null);
  const [lastRegistered, setLastRegistered] = useState({});
  const [registroConfirmado, setRegistroConfirmado] = useState(false);

  // 1. Arranca la cámara al montar
  useEffect(() => {
    async function startCamera() {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        const externalCam = videoDevices.find(d =>
          d.label.toLowerCase().includes('droidcam') ||
          d.label.toLowerCase().includes('obs')
        );
        const deviceId = externalCam
          ? externalCam.deviceId
          : (videoDevices[0]?.deviceId || null);

        if (!deviceId) {
          console.error('No se encontró ninguna cámara');
          return;
        }

        const stream = await navigator.mediaDevices.getUserMedia({
          video: { deviceId: { exact: deviceId }, width: 640, height: 480 },
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
      setResult(response.data);

      if (response.data.match) {
        const now = Date.now();
        const name = response.data.name;
        if (!lastRegistered[name] || now - lastRegistered[name] > 60000) {
          await axios.post(
            'http://127.0.0.1:5000/api/asistencia',
            { name },
            { headers: { 'Content-Type': 'application/json' } }
          );
          setLastRegistered(prev => ({ ...prev, [name]: now }));
          setRegistroConfirmado(true);
          setTimeout(() => setRegistroConfirmado(false), 4000);
        }
      }
    } catch (error) {
      console.error('Error en reconocimiento:', error);
      setResult({ error: 'Error en el reconocimiento' });
    }
  };

  // 3. Inicia la captura periódica
  const startCapturing = () => {
    if (!streamStarted) return;
    setCapturing(true);
    const id = setInterval(captureAndSend, 2000);
    setIntervalId(id);
    setTimeout(() => {
      clearInterval(id);
      setCapturing(false);
    }, 15000);
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

      {registroConfirmado && (
        <div className="alert alert-success mt-4">
          ✅ Asistencia registrada correctamente
        </div>
      )}

      {result && !result.error && (
        <div
          className="alert mt-4"
          style={{ background: result.match ? '#d1e7dd' : '#f8d7da' }}
        >
          <h5>
            {result.match ? '✅ Coincidencia' : '❌ No reconocido'}
          </h5>
          <p>Nombre: {result.name}</p>
          <p>Similitud: {result.similarity}%</p>
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
