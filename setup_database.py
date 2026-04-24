"""
Setup script to create database and tables
Run this script to setup the MySQL database
"""
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

def setup_database():
    """Create database and tables"""
    try:
        # Connect to MySQL server (without database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            print("Creating database...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS truthlens_db")
            print("✅ Database 'truthlens_db' created successfully")
            
            # Select database
            cursor.execute("USE truthlens_db")
            
            # Drop existing tables
            print("Dropping existing tables...")
            cursor.execute("DROP TABLE IF EXISTS predictions")
            cursor.execute("DROP TABLE IF EXISTS users")
            
            # Create users table
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Users table created")
            
            # Create predictions table
            print("Creating predictions table...")
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Predictions table created")
            
            # Insert default admin user
            print("Creating admin user...")
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (%s, %s, %s, %s)
            """, ('admin', admin_password_hash, 'admin@truthlens.ai', True))
            print("✅ Admin user created (username: admin, password: admin123)")
            
            # Insert sample predictions
            print("Adding sample data...")
            cursor.executemany("""
                INSERT INTO predictions (input_text, prediction, confidence, sentiment, sentiment_score, user_ip)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                ('Breaking: Scientists discover new evidence of climate change impact on oceans.', 'REAL', 87.50, 'Neutral', 0.05, '127.0.0.1'),
                ('SHOCKING: Aliens found in government facility, officials refuse to comment!', 'FAKE', 94.20, 'Negative', -0.35, '127.0.0.1'),
                ('Local community comes together to support flood victims with donations.', 'REAL', 82.15, 'Positive', 0.68, '127.0.0.1')
            ])
            print("✅ Sample data added")
            
            # Commit changes
            connection.commit()
            
            print("\n" + "="*60)
            print("✅ Database setup completed successfully!")
            print("="*60)
            print("\nDatabase: truthlens_db")
            print("Admin Username: admin")
            print("Admin Password: admin123")
            print("\nYou can now run the application with: python run.py")
            
    except Error as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed")
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("TruthLens AI - Database Setup Script")
    print("="*60)
    setup_database()
