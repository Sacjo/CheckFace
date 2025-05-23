// ----------------------
// Fecha y hora en la cabecera (misma línea, formato hh:mm dd/MM/yyyy)
// ----------------------
const nowEl = document.getElementById('currentDateTime');
function updateDateTime() {
  const d = new Date();
  const timeStr = d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  const dateStr = d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
  nowEl.textContent = `${timeStr}   ${dateStr}`;
}
updateDateTime();
setInterval(updateDateTime, 1000);

// ----------------------
// Variables del reconocimiento
// ----------------------
const video           = document.getElementById('video');
const snapshot        = document.getElementById('snapshot');
const startBtn        = document.getElementById('startBtn');
const stopBtn         = document.getElementById('stopBtn');
const reportBtn       = document.getElementById('reportBtn');
const timerEl         = document.getElementById('timer');
const attendanceTable = document.getElementById('attendanceTable');
const unrecList       = document.getElementById('unrecognizedList');

let stream, ctx, interval, endTime;
let recognizing = false;

// ----------------------
// Inicializar cámara
// ----------------------
async function initCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    ctx = snapshot.getContext('2d');
    startBtn.disabled = false;
  } catch (err) {
    console.error('No fue posible acceder a la cámara:', err);
    alert('Debes permitir el uso de la cámara para iniciar el reconocimiento');
  }
}

// ----------------------
// Temporizador
// ----------------------
function updateTimer() {
  const remaining = Math.max(0, Math.floor((endTime - Date.now()) / 1000));
  timerEl.textContent = `${remaining}s`;
  if (remaining === 0) stopRecognition();
}

// ----------------------
// Parar reconocimiento
// ----------------------
function stopRecognition() {
  recognizing = false;
  clearInterval(interval);

  // Restablecer botones y temporizador
  startBtn.disabled  = false;
  stopBtn.disabled   = true;
  reportBtn.disabled = false;
  timerEl.textContent = '';
}

// ----------------------
// Enviar frame al servidor
// ----------------------
async function sendFrame() {
  if (!recognizing) return;

  ctx.drawImage(video, 0, 0, snapshot.width, snapshot.height);
  const blob = await new Promise(res => snapshot.toBlob(res, 'image/jpeg'));

  const resp = await fetch('/api/recognize', { method: 'POST', body: blob });
  if (!resp.ok) {
    console.error('Error en /api/recognize', resp.status);
    return;
  }

  const data = await resp.json();
  if (!recognizing) return;

  renderLists(data);
}

// ----------------------
// Renderizar listas
// ----------------------
function renderLists(data) {
  attendanceTable.innerHTML = '';
  data.attendance.forEach(([name, hour]) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${name}</td><td>${hour}</td><td>✔️</td>`;
    attendanceTable.appendChild(tr);
  });

  unrecList.innerHTML = '';
  data.unrecognized.forEach(name => {
    const li = document.createElement('li');
    li.className = 'list-group-item';
    li.textContent = name;
    unrecList.appendChild(li);
  });
}

// ----------------------
// Eventos de usuario
// ----------------------
startBtn.addEventListener('click', async () => {
  // Deshabilitar controles y limpiar datos previos
  startBtn.disabled   = true;
  stopBtn.disabled    = false;
  reportBtn.disabled  = true;
  recognizing          = true;
  endTime              = Date.now() + 60 * 1000;

  // Resetear datos en servidor y UI al iniciar nueva sesión
  try {
    await fetch('/api/reset', { method: 'POST' });
    attendanceTable.innerHTML = '';
    unrecList.innerHTML       = '';
  } catch (e) {
    console.error('Error al resetear datos:', e);
  }

  // Iniciar bucle de captura
  interval = setInterval(async () => {
    if (!recognizing || Date.now() >= endTime) {
      stopRecognition();
      return;
    }
    updateTimer();
    try {
      await sendFrame();
    } catch (e) {
      console.error('sendFrame falló', e);
    }
  }, 500);
});

stopBtn.addEventListener('click', stopRecognition);

// Descargar reporte
reportBtn.addEventListener('click', () => {
  window.location.href = '/export';
});

// ----------------------
// Arranque
// ----------------------
window.addEventListener('DOMContentLoaded', () => {
  startBtn.disabled  = true;
  stopBtn.disabled   = true;
  reportBtn.disabled = true;
  initCamera();
});
