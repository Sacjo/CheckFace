-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    ci INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Tabla de materias
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    career VARCHAR(120),
    semester INT
);

-- Tabla intermedia: usuarios ↔ materias
CREATE TABLE IF NOT EXISTS user_courses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE
);

-- Tabla de asistencias
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    date TIMESTAMP
);

-- Tabla de imágenes faciales
CREATE TABLE IF NOT EXISTS face_images (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    embedding TEXT
);