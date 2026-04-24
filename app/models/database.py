"""
Database models and connection handler
Manages MySQL database connections and operations
"""

import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database connection manager with connection pooling"""
    
    def __init__(self, config):
        """Initialize database connection pool"""
        self.config = config
        self.connection_pool = None
        self._create_pool()
    
    def _create_pool(self):
        """Create connection pool"""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="truthlens_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.config.get('MYSQL_HOST', 'localhost'),
                database=self.config.get('MYSQL_DATABASE', 'truthlens_db'),
                user=self.config.get('MYSQL_USER', 'root'),
                password=self.config.get('MYSQL_PASSWORD', ''),
                port=self.config.get('MYSQL_PORT', 3306)
            )
            logger.info("✅ Database connection pool created successfully")
        except Error as e:
            logger.error(f"❌ Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """
        Execute a database query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            fetch: Whether to fetch all results
            fetch_one: Whether to fetch only one result
            
        Returns:
            Query results if fetch=True or fetch_one=True, else affected row count
        """
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                    return result
                elif fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    connection.commit()
                    return cursor.rowcount
            except Error as e:
                logger.error(f"❌ Query execution error: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def insert_prediction(self, input_text, input_url, prediction, confidence, 
                         sentiment, sentiment_score, user_ip, user_agent, processing_time):
        """
        Insert a prediction record into the database
        
        Args:
            input_text: The input news text
            input_url: The input URL (if provided)
            prediction: FAKE or REAL
            confidence: Confidence percentage
            sentiment: Sentiment analysis result
            sentiment_score: Sentiment score
            user_ip: User's IP address
            user_agent: User's browser agent
            processing_time: Time taken to process
            
        Returns:
            Insert ID
        """
        query = """
            INSERT INTO predictions 
            (input_text, input_url, prediction, confidence, sentiment, 
             sentiment_score, user_ip, user_agent, processing_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            input_text[:5000],  # Limit text length
            input_url,
            prediction,
            float(confidence),  # Convert numpy float64 to Python float
            sentiment,
            float(sentiment_score),  # Convert numpy float64 to Python float
            user_ip,
            user_agent[:255] if user_agent else None,
            float(processing_time)  # Convert to Python float
        )
        
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                connection.commit()
                insert_id = cursor.lastrowid
                logger.info(f"✅ Prediction saved with ID: {insert_id}")
                return insert_id
            except Error as e:
                logger.error(f"❌ Error inserting prediction: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def get_statistics(self):
        """
        Get dashboard statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_predictions': 0,
            'fake_count': 0,
            'real_count': 0,
            'avg_confidence': 0,
            'recent_predictions': []
        }
        
        try:
            # Get total counts
            count_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction = 'FAKE' THEN 1 ELSE 0 END) as fake,
                    SUM(CASE WHEN prediction = 'REAL' THEN 1 ELSE 0 END) as real,
                    AVG(confidence) as avg_conf
                FROM predictions
            """
            result = self.execute_query(count_query, fetch=True)
            
            if result and len(result) > 0:
                stats['total_predictions'] = result[0]['total'] or 0
                stats['fake_count'] = result[0]['fake'] or 0
                stats['real_count'] = result[0]['real'] or 0
                stats['avg_confidence'] = float(result[0]['avg_conf'] or 0)
            
            # Get recent predictions
            recent_query = """
                SELECT 
                    id,
                    SUBSTRING(input_text, 1, 100) as text_preview,
                    prediction,
                    confidence,
                    sentiment,
                    timestamp
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT 10
            """
            stats['recent_predictions'] = self.execute_query(recent_query, fetch=True)
            
        except Error as e:
            logger.error(f"❌ Error getting statistics: {e}")
        
        return stats
    
    def verify_user(self, username, password_hash):
        """
        Verify user credentials
        
        Args:
            username: Username
            password_hash: Hashed password
            
        Returns:
            User data if valid, None otherwise
        """
        query = """
            SELECT id, username, email, is_admin
            FROM users
            WHERE username = %s AND password_hash = %s
        """
        
        result = self.execute_query(query, (username, password_hash), fetch=True)
        
        if result and len(result) > 0:
            # Update last login
            update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            self.execute_query(update_query, (result[0]['id'],))
            return result[0]
        
        return None
    
    def get_daily_stats(self, days=7):
        """
        Get daily statistics for the past N days
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily statistics
        """
        query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total,
                SUM(CASE WHEN prediction = 'FAKE' THEN 1 ELSE 0 END) as fake,
                SUM(CASE WHEN prediction = 'REAL' THEN 1 ELSE 0 END) as real_count
            FROM predictions
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """
        
        try:
            result = self.execute_query(query, (days,), fetch=True)
            return result or []
        except Error as e:
            logger.error(f"❌ Error getting daily stats: {e}")
            return []
    
    def get_all_users(self):
        """
        Get all registered users with their activity
        
        Returns:
            List of users with activity count
        """
        query = """
            SELECT 
                u.id,
                u.username,
                u.email,
                u.is_admin,
                u.created_at,
                u.last_login,
                COUNT(p.id) as prediction_count
            FROM users u
            LEFT JOIN predictions p ON u.username = p.user_ip
            GROUP BY u.id, u.username, u.email, u.is_admin, u.created_at, u.last_login
            ORDER BY u.last_login DESC
        """
        
        try:
            result = self.execute_query(query, fetch=True)
            return result or []
        except Error as e:
            logger.error(f"❌ Error getting users: {e}")
            return []
    
    def get_user_search_history(self, username=None):
        """
        Get search history for all users or a specific user
        
        Args:
            username: Optional username to filter by
            
        Returns:
            List of predictions with user information
        """
        if username:
            query = """
                SELECT 
                    p.id,
                    p.user_ip as username,
                    SUBSTRING(p.input_text, 1, 150) as text_preview,
                    p.input_url,
                    p.prediction,
                    p.confidence,
                    p.sentiment,
                    p.timestamp
                FROM predictions p
                WHERE p.user_ip = %s
                ORDER BY p.timestamp DESC
                LIMIT 50
            """
            params = (username,)
        else:
            query = """
                SELECT 
                    p.id,
                    p.user_ip as username,
                    SUBSTRING(p.input_text, 1, 150) as text_preview,
                    p.input_url,
                    p.prediction,
                    p.confidence,
                    p.sentiment,
                    p.timestamp
                FROM predictions p
                ORDER BY p.timestamp DESC
                LIMIT 100
            """
            params = None
        
        try:
            result = self.execute_query(query, params, fetch=True)
            return result or []
        except Error as e:
            logger.error(f"❌ Error getting search history: {e}")
            return []
