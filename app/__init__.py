"""
Flask Application Factory
Initializes and configures the Flask app
"""

from flask import Flask
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """
    Create and configure the Flask application
    
    Args:
        config_name: Configuration to use (default, development, production)
        
    Returns:
        Configured Flask app
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Create necessary directories
    os.makedirs(os.path.join(app.config['BASE_DIR'], 'models'), exist_ok=True)
    
    # Register blueprints
    from app.routes.main import main_bp, init_routes
    from app.routes.auth import auth_bp, init_auth
    from app.models.database import Database
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    # Initialize routes with dependencies
    with app.app_context():
        try:
            # Initialize database (optional - app works without it)
            database = None
            try:
                database = Database(app.config)
                logger.info("✅ Database connected successfully")
            except Exception as db_error:
                logger.warning(f"⚠️  Database not available: {db_error}")
                logger.warning("⚠️  App will run without database (predictions work, dashboard disabled)")
            
            # Initialize routes
            init_routes(app, database)
            init_auth(database)
            
            logger.info("✅ Application initialized successfully")
            logger.info(f"📊 Using configuration: {config_name}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing application: {e}")
            raise
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    return app
