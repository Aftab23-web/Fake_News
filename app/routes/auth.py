"""
Authentication routes for admin login
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Database instance (initialized in __init__.py)
database = None

# In-memory user store (when database is not available)
in_memory_users = {}


def init_auth(db):
    """Initialize database for auth routes"""
    global database
    database = db


@auth_bp.route('/login')
def login_page():
    """Render login page"""
    # If already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')


@auth_bp.route('/register')
def register_page():
    """Render registration page"""
    # If already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html')


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """
    API endpoint for user registration
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        # Validate username length
        if len(username) < 3:
            return jsonify({
                'success': False,
                'error': 'Username must be at least 3 characters'
            }), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400
        
        # Validate email format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Check if database is available
        if database is None:
            # Allow registration without database for demo
            logger.warning("⚠️ Database not available, using in-memory storage")
            
            # Check if username or email already exists in memory
            for stored_user in in_memory_users.values():
                if stored_user['username'] == username or stored_user['email'] == email:
                    return jsonify({
                        'success': False,
                        'error': 'Username or email already exists'
                    }), 409
            
            # Store user in memory with hashed password
            password_hash = generate_password_hash(password)
            in_memory_users[username] = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'is_admin': False
            }
            
            # Set session (temporary solution without database)
            session['logged_in'] = True
            session['username'] = username
            session['email'] = email
            session['is_admin'] = False
            
            logger.info(f"✅ User registered (in-memory): {username}")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful (in-memory mode)',
                'username': username,
                'is_admin': False
            }), 200
        
        # Check if username already exists
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        existing_user = database.execute_query(check_query, (username, email), fetch_one=True)
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 409
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        insert_query = """
            INSERT INTO users (username, email, password_hash, is_admin, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        database.execute_query(insert_query, (username, email, password_hash, False))
        
        # Set session
        session['logged_in'] = True
        session['username'] = username
        session['email'] = email
        session['is_admin'] = False
        
        logger.info(f"✅ User registered: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'username': username,
            'is_admin': False
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    API endpoint for user login (supports both admin and regular users)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        # Check admin credentials first (for backward compatibility)
        from config import Config
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            # Set session for admin
            session['logged_in'] = True
            session['username'] = username
            session['is_admin'] = True
            
            logger.info(f"✅ Admin logged in: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'username': username,
                'is_admin': True
            }), 200
        
        # Check database for registered users
        if database is not None:
            try:
                query = "SELECT id, username, email, password_hash, is_admin FROM users WHERE username = %s"
                user = database.execute_query(query, (username,), fetch_one=True)
                
                if user and check_password_hash(user['password_hash'], password):
                    # Set session
                    session['logged_in'] = True
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['is_admin'] = bool(user['is_admin'])
                    
                    logger.info(f"✅ User logged in: {user['username']}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'username': user['username'],
                        'is_admin': bool(user['is_admin'])
                    }), 200
            except Exception as db_error:
                logger.warning(f"⚠️ Database error during login: {db_error}")
        else:
            # Check in-memory users when database is not available
            if username in in_memory_users:
                user = in_memory_users[username]
                if check_password_hash(user['password_hash'], password):
                    # Set session
                    session['logged_in'] = True
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['is_admin'] = user['is_admin']
                    
                    logger.info(f"✅ User logged in (in-memory): {user['username']}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'username': user['username'],
                        'is_admin': user['is_admin']
                    }), 200
        
        # If we get here, login failed
        logger.warning(f"❌ Failed login attempt for username: {username}")
        return jsonify({
            'success': False,
            'error': 'Invalid username or password'
        }), 401
            
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """
    API endpoint for logout
    """
    try:
        username = session.get('username', 'Unknown')
        
        # Clear session
        session.clear()
        
        logger.info(f"✅ User logged out: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/api/check-auth', methods=['GET'])
def check_auth():
    """
    Check if user is authenticated
    """
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True,
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False)
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200
