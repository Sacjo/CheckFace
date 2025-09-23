-- Set default schema
SET search_path TO public;

-- Table: roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    description VARCHAR(120) NOT NULL
);

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(120) NOT NULL,
    password TEXT NOT NULL,
    role_id INT REFERENCES roles(id) ON DELETE SET NULL
);

-- Table: courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    career VARCHAR(120),
    semester INT
);

-- Table: course schedules
CREATE TABLE IF NOT EXISTS course_schedules (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    day VARCHAR(20) NOT NULL,
    schedule VARCHAR(50) NOT NULL,
    classroom VARCHAR(50)
);

-- Table: participants (relacionado a usuarios)
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    ci INT NOT NULL,
    occupation VARCHAR(50) NOT NULL,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);

-- Relación muchos a muchos: participants ↔ courses
CREATE TABLE IF NOT EXISTS participant_courses (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE
);

-- ✅ Table: attendances con participant_id (no user_id)
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    date TIMESTAMP,
    observations TEXT
);