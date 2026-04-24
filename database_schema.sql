-- ============================================
-- TruthLens AI Database Schema
-- Database for storing fake news predictions
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS truthlens_db;
USE truthlens_db;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS users;

-- ============================================
-- Users table for admin authentication
-- ============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Predictions table for storing detection results
-- ============================================
CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_text TEXT NOT NULL,
    input_url VARCHAR(500),
    prediction VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    sentiment VARCHAR(20),
    sentiment_score DECIMAL(5,2),
    user_ip VARCHAR(45),
    user_agent VARCHAR(255),
    processing_time DECIMAL(6,3),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prediction (prediction),
    INDEX idx_timestamp (timestamp),
    INDEX idx_confidence (confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Statistics view for dashboard
-- ============================================
CREATE OR REPLACE VIEW prediction_stats AS
SELECT 
    COUNT(*) as total_predictions,
    SUM(CASE WHEN prediction = 'FAKE' THEN 1 ELSE 0 END) as fake_count,
    SUM(CASE WHEN prediction = 'REAL' THEN 1 ELSE 0 END) as real_count,
    AVG(confidence) as avg_confidence,
    DATE(timestamp) as prediction_date
FROM predictions
GROUP BY DATE(timestamp)
ORDER BY prediction_date DESC;

-- ============================================
-- Insert default admin user
-- Password: admin123 (Change this in production!)
-- ============================================
INSERT INTO users (username, password_hash, email, is_admin)
VALUES ('admin', 'scrypt:32768:8:1$cJlM8B9KMZ1qGq9g$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6', 'admin@truthlens.ai', TRUE);

-- ============================================
-- Sample data for testing (optional)
-- ============================================
INSERT INTO predictions (input_text, prediction, confidence, sentiment, sentiment_score, user_ip)
VALUES 
    ('Breaking: Scientists discover new evidence of climate change impact on oceans.', 'REAL', 87.50, 'Neutral', 0.05, '127.0.0.1'),
    ('SHOCKING: Aliens found in government facility, officials refuse to comment!', 'FAKE', 94.20, 'Negative', -0.35, '127.0.0.1'),
    ('Local community comes together to support flood victims with donations.', 'REAL', 82.15, 'Positive', 0.68, '127.0.0.1');

-- ============================================
-- Show created tables
-- ============================================
SHOW TABLES;

SELECT 'Database schema created successfully!' as Status;
