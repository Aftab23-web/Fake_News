"""
Clean up old sample predictions
"""
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='truthlens_db'
    )
    
    cursor = conn.cursor()
    
    # Delete old sample predictions with IP addresses
    print("Deleting old sample predictions...")
    cursor.execute("DELETE FROM predictions WHERE user_ip = '127.0.0.1'")
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ Deleted {deleted_count} old sample predictions")
    
    # Verify
    cursor.execute("SELECT COUNT(*) as count FROM predictions")
    result = cursor.fetchone()
    print(f"Remaining predictions: {result[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
