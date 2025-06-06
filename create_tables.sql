-- Create database if not exists
CREATE DATABASE IF NOT EXISTS your_database_name;
USE your_database_name;

-- Create secure_users table
CREATE TABLE secure_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- Create secure_password_history table
CREATE TABLE secure_password_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    old_password_hash VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES secure_users(id)
);

-- Sample user (password = Test@123)
INSERT INTO secure_users (username, password_hash) VALUES
('john_doe', '$2b$12$1VQ0wWMea2ADGpkqHqfH5ezGV9eWm3n8PvL7bpCHu38rf0ElJvJLu');
