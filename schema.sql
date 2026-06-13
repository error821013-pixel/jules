-- PostgreSQL Database Schema for Gaming Club Management System

-- 1. Table Creation

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    balance DOUBLE PRECISION DEFAULT 0.0,
    points INTEGER DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE
);

-- PCs Table
CREATE TABLE pcs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL, -- Standard, VIP, Bootcamp
    hourly_rate DOUBLE PRECISION NOT NULL
);

-- Bookings Table
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pc_id INTEGER REFERENCES pcs(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    total_price DOUBLE PRECISION NOT NULL
);

-- Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'deposit', 'booking'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 2. Basic CRUD Operations

-- Register a new user
INSERT INTO users (username, hashed_password, balance, points, is_admin)
VALUES ('johndoe', '$2b$12$hashedpasswordexample...', 0.0, 0, FALSE);

-- Add a PC
INSERT INTO pcs (name, category, hourly_rate)
VALUES ('PC 1 (Standard)', 'Standard', 50.0);

-- Create a booking
-- Step 1: Insert booking record
INSERT INTO bookings (user_id, pc_id, start_time, end_time, total_price)
VALUES (1, 1, '2023-10-27 14:00:00', '2023-10-27 16:00:00', 100.0);

-- Step 2: Deduct balance from user
UPDATE users SET balance = balance - 100.0 WHERE id = 1;

-- Step 3: Add transaction record
INSERT INTO transactions (user_id, amount, type)
VALUES (1, -100.0, 'booking');

-- Deposit funds
UPDATE users SET balance = balance + 500.0 WHERE id = 1;
INSERT INTO transactions (user_id, amount, type)
VALUES (1, 500.0, 'deposit');


-- 3. Analytical Queries for Admin Dashboard

-- Average Check (Average Order Value) for a specific period
SELECT AVG(total_price)
FROM bookings
WHERE start_time >= '2023-10-01' AND start_time < '2023-11-01';

-- Total Revenue for a specific period
SELECT SUM(total_price)
FROM bookings
WHERE start_time >= '2023-10-01' AND start_time < '2023-11-01';

-- List of currently occupied PCs and their session end times
SELECT p.name AS pc_name, u.username, b.end_time
FROM bookings b
JOIN pcs p ON b.pc_id = p.id
JOIN users u ON b.user_id = u.id
WHERE CURRENT_TIMESTAMP BETWEEN b.start_time AND b.end_time;

-- Attendance Analytics: Number of unique visitors per day
SELECT DATE(start_time) AS visit_date, COUNT(DISTINCT user_id) AS unique_visitors
FROM bookings
GROUP BY DATE(start_time)
ORDER BY visit_date DESC;
