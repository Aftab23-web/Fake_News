"""
Application entry point
Run this file to start the Flask server
"""

from app import create_app
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Get environment
env = os.environ.get('FLASK_ENV', 'development')

# Create app
app = create_app(env)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting TruthLens AI - Fake News Detector")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print("\n📍 Server will be available at: http://localhost:5000")
    print("📍 Dashboard: http://localhost:5000/dashboard")
    print("📍 Login: http://localhost:5000/login")
    print("\n🔐 Default Admin Credentials:")
    print(f"   Username: {app.config['ADMIN_USERNAME']}")
    print(f"   Password: {app.config['ADMIN_PASSWORD']}")
    print("\n⚠️  Please change default credentials in production!")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
