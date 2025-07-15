# CheckFace

**CheckFace** es un sistema de asistencia basado en reconocimiento facial en tiempo real. Está diseñado para entornos educativos como aulas universitarias, permitiendo registrar la presencia de los estudiantes mediante el uso de una cámara y tecnologías de visión artificial.

---

## 🧠 Tecnologías utilizadas

- **Frontend**: React + Bootstrap (basado en plantilla SB Admin)
- **Backend**: Flask (Python)
- **Base de datos**: PostgreSQL
- **Reconocimiento facial**: DeepFace (modelo ArcFace)
- **Otros**: OpenCV, Axios, Recharts, dotenv

---

## ⚙️ Estructura del proyecto

```
CheckFace/
├── backend/
│   ├── app/
│   │   ├── detection/         # (Opcional - detección facial)
│   │   ├── models/            # Modelos y pesos
│   │   └── routes/            # Rutas Flask (reconocimiento, asistencia)
│   ├── database/              # Conexión y script de base de datos
│   └── run.py                 # Punto de entrada del backend
├── frontend/
│   └── src/                   # Código fuente React
│       ├── components/        # Gráficos, cámara, sidebar
│       └── pages/             # Dashboard y página de reconocimiento
├── .env                       # Variables de entorno (no subir)
├── .gitignore                 # Archivos ignorados por Git
├── train_faces.py            # Script para procesar rostros y generar embeddings
└── requirements.txt          # Dependencias Python
```

---

## 🚀 Funcionalidades actuales

- [x] Reconocimiento facial automático con webcam
- [x] Registro de asistencia a base de datos
- [x] Dashboard con gráfico de asistencias por día
- [x] API REST con endpoints para:
  - `/api/asistencia` (POST)
  - `/api/asistencias` (GET)
  - `/api/asistencias/resumen` (GET)
- [x] Barra lateral con navegación entre Dashboard y Reconocimiento Facial
- [x] Registro mediante Postman verificado

---

## 🔐 Seguridad

- `.env` utilizado para ocultar credenciales de conexión
- Se evita subir imágenes o datos sensibles (`raw_faces/`, `known_faces/`)

---

## 🧪 Scripts útiles

```bash
# Ejecutar backend
python run.py

# Inicializar tablas
python -m database.init_db

# Generar embeddings de rostros
python train_faces.py
```

---

## ✅ Últimos cambios importantes

- Migración de modelo: `Facenet → ArcFace`
- Ajuste de umbral de similitud (`60`)
- Generación de resumen por persona al entrenar
- Rediseño del sidebar basado en plantilla SB Admin

---

## 🗓️ Última actualización

2025-07-15
