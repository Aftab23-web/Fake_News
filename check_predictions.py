"""
Quick script to check predictions in database
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
    
    # Check all predictions
    print("\n=== All Predictions ===")
    cursor.execute("SELECT id, user_ip, SUBSTRING(input_text, 1, 50) as text, prediction, timestamp FROM predictions ORDER BY timestamp DESC LIMIT 10")
    predictions = cursor.fetchall()
    
    for pred in predictions:
        print(f"ID: {pred['id']}, User: {pred['user_ip']}, Prediction: {pred['prediction']}, Time: {pred['timestamp']}")
        print(f"  Text: {pred['text']}...")
        print()
    
    # Check unique users
    print("\n=== Unique Users in Predictions ===")
    cursor.execute("SELECT DISTINCT user_ip, COUNT(*) as count FROM predictions GROUP BY user_ip")
    users = cursor.fetchall()
    
    for user in users:
        print(f"User: '{user['user_ip']}' - Predictions: {user['count']}")
    
    # Check registered users
    print("\n=== Registered Users ===")
    cursor.execute("SELECT username, email FROM users")
    registered = cursor.fetchall()
    
    for user in registered:
        print(f"Username: '{user['username']}', Email: {user['email']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
