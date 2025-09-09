-- Reset database
DROP DATABASE IF EXISTS school_portal;
CREATE DATABASE school_portal;
USE school_portal;

-- Users (teachers + headmaster)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Teacher', 'Headmaster') NOT NULL,
    subject VARCHAR(50) DEFAULT NULL
);

-- Students
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL
);

-- Attendance
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

-- Scores
CREATE TABLE scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    is_final BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

-- Score Edit Requests
CREATE TABLE score_edit_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    score_id INT NOT NULL,
    requested_score DECIMAL(5,2) NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (score_id) REFERENCES scores(score_id)
);

-- Insert sample users
INSERT INTO users (username, password_hash, role, subject) VALUES
('headmaster1', 'pass123', 'Headmaster', NULL),
('teacher_john', 'pass123', 'Teacher', 'Math'),
('teacher_mary', 'pass123', 'Teacher', 'English');

-- Insert sample students
INSERT INTO students (full_name, class_name) VALUES
('Alice Brown', 'Grade 6'),
('James Smith', 'Grade 6');
