// src/components/CameraCapture.js
import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

export default function CameraCapture() {
  const webcamRef = useRef(null);
  const [deviceId, setDeviceId] = useState(null);
  const [result, setResult] = useState(null);
  const [capturing, setCapturing] = useState(false);
  const [intervalId, setIntervalId] = useState(null);
  const [lastRegistered, setLastRegistered] = useState({});
  const [registroConfirmado, setRegistroConfirmado] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(devices => {
      const videoDevices = devices.filter(d => d.kind === 'videoinput');
      const externalCam = videoDevices.find(
        d => d.label.toLowerCase().includes('droidcam') || d.label.toLowerCase().includes('obs')
      );
      if (externalCam) {
        setDeviceId(externalCam.deviceId);
      } else if (videoDevices.length > 0) {
        setDeviceId(videoDevices[0].deviceId);
      }
    });
  }, []);

  const captureAndSend = async () => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    try {
      const res = await fetch(imageSrc);
      const blob = await res.blob();
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

      const formData = new FormData();
      formData.append('image', file);

      const response = await axios.post('http://127.0.0.1:5000/api/recognize', formData);
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

          // Ocultar alerta luego de 4 segundos
          setTimeout(() => setRegistroConfirmado(false), 4000);
        }
      }
    } catch (error) {
      console.error('Error al reconocer:', error);
      setResult({ error: 'Error en el reconocimiento' });
    }
  };

  const startCapturing = () => {
    setCapturing(true);
    const id = setInterval(captureAndSend, 2000);
    setIntervalId(id);

    setTimeout(() => {
      clearInterval(id);
      setCapturing(false);
    }, 15000);
  };

  useEffect(() => {
    return () => clearInterval(intervalId);
  }, [intervalId]);

  return (
    <div className="container text-center mt-4">
      <h3>Reconocimiento Facial (Automático)</h3>

      {deviceId ? (
        <>
          <Webcam
            audio={false}
            height={480}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            width={640}
            videoConstraints={{ width: 640, height: 480, deviceId }}
            className="rounded border"
          />
          <br />
          <button onClick={startCapturing} className="btn btn-success mt-3" disabled={capturing}>
            {capturing ? 'Reconociendo...' : 'Iniciar Reconocimiento'}
          </button>
        </>
      ) : (
        <p className="text-danger">Cargando cámara...</p>
      )}

      {registroConfirmado && (
        <div className="alert alert-success mt-4" role="alert">
          ✅ Asistencia registrada correctamente
        </div>
      )}

      {result && !result.error && (
        <div className="alert mt-4" role="alert" style={{ background: result.match ? '#d1e7dd' : '#f8d7da' }}>
          <h5>{result.match ? '✅ Coincidencia' : '❌ No reconocido'}</h5>
          <p>Nombre: {result.name}</p>
          <p>Similitud: {result.similarity}%</p>
        </div>
      )}
    </div>
  );
}
