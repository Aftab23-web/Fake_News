"""
Check for recent predictions by Sonu
"""
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='truthlens_db'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Check when Sonu was created
    cursor.execute("SELECT username, created_at FROM users WHERE username = 'Sonu'")
    sonu = cursor.fetchone()
    if sonu:
        print(f"\nSonu registered at: {sonu['created_at']}")
    
    # Check all predictions after Sonu's registration
    print("\n=== All Predictions (most recent first) ===")
    cursor.execute("SELECT id, user_ip, prediction, timestamp FROM predictions ORDER BY timestamp DESC LIMIT 20")
    predictions = cursor.fetchall()
    
    for pred in predictions:
        print(f"ID: {pred['id']}, User: '{pred['user_ip']}', Prediction: {pred['prediction']}, Time: {pred['timestamp']}")
    
    # Count predictions by each "user"
    print("\n=== Predictions Count ===")
    cursor.execute("SELECT user_ip, COUNT(*) as count FROM predictions GROUP BY user_ip")
    users = cursor.fetchall()
    
    for user in users:
        print(f"User: '{user['user_ip']}' - Count: {user['count']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
