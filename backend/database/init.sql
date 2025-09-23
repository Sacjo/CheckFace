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

-- Table: courses (without schedule/day/classroom directly)
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    career VARCHAR(120),
    semester INT
);

-- NEW: Table for course schedules (multiple days/times/classrooms per course)
CREATE TABLE IF NOT EXISTS course_schedules (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    day VARCHAR(20) NOT NULL,          -- e.g., "Monday"
    schedule VARCHAR(50) NOT NULL,     -- e.g., "08:00 - 10:00"
    classroom VARCHAR(50)              -- e.g., "Room A1"
);

-- Table: user_courses (relation between users and courses)
CREATE TABLE IF NOT EXISTS user_courses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE
);

-- Table: attendances (with observations)
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    date TIMESTAMP,
    observations TEXT
);

-- NEW: Table for participants (linked to user, stores CI and role type)
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    ci INT NOT NULL,
    occupation VARCHAR(50) NOT NULL,   -- e.g., "student", "teacher"
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);