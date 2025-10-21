# ============================================================================
# AI TRENDS APPLICATION - Main Flask Application
# ============================================================================
# 
# This is the main entry point for the AI Trends web application.
# It handles routing, authentication, report generation, and API endpoints.
#
# KEY FEATURES:
# - User authentication and session management
# - AI report generation
# - Chatbot interaction
# - LinkedIn post generation
# - YouTube video recommendations
# - AI leaderboard visualization
#
# BEFORE RUNNING:
# 1. Ensure all dependencies are installed (pip install -r requirements.txt)
# 2. Configure your .env file with API keys
# 3. Set up user profiles in data/users/
# 4. Run with: python app.py
# ============================================================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import os
import sys
import logging
from datetime import datetime
import subprocess

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import configuration and modules
from config import Config
from backend.user_manager import UserManager
from backend.ai_agents import AIAgentsPipeline

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize Flask-Session for user session management
Session(app)

# Initialize CSRF Protection for security
csrf = CSRFProtect(app)

# ============================================================================
# LOGGING SETUP
# ============================================================================
# Configure application logging to track errors and user activity

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# INITIALIZE MANAGERS
# ============================================================================

# User manager handles authentication and profile management
user_manager = UserManager()

# AI pipeline handles report generation and chatbot
# Initialize when needed to avoid API key errors on startup
ai_pipeline = None

# ============================================================================
# CREATE NECESSARY DIRECTORIES
# ============================================================================

os.makedirs('logs', exist_ok=True)
os.makedirs('data/reports', exist_ok=True)
os.makedirs('data/scraped', exist_ok=True)
os.makedirs('data/backups', exist_ok=True)

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/')
def index():
    """
    Root route - redirects to dashboard if logged in, otherwise to login
    """
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    """
    Login page and authentication handler
    
    GET: Display login form
    POST: Authenticate user credentials
    """
    if request.method == 'POST':
        try:
            # Get form data
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            logger.info(f"Login attempt for user: {username}")
            
            # Authenticate user
            if user_manager.authenticate(username, password):
                # Set session
                session['username'] = username
                session.permanent = True
                
                logger.info(f"User {username} logged in successfully")
                
                # Return JSON response for AJAX requests
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'redirect': url_for('dashboard')
                    })
                else:
                    return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid username or password'
                    }), 401
                else:
                    return render_template('login.html', error='Invalid username or password')
                    
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'An error occurred during login'
                }), 500
            else:
                return render_template('login.html', error='An error occurred. Please try again.')
    
    # GET request - show login page
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logout user and clear session
    """
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User {username} logged out")
    return redirect(url_for('login'))

# ============================================================================
# ROUTES - DASHBOARD & PROFILE
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """
    Main dashboard page - displays user stats and recent reports
    """
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    try:
        # Get user profile
        profile = user_manager.get_user_profile(username)
        
        # Get user statistics
        stats = user_manager.get_user_statistics(username)
        
        # Get recent reports
        recent_reports = user_manager.get_user_reports(username, limit=5)
        
        return render_template(
            'dashboard.html',
            username=username,
            profile=profile,
            stats=stats,
            recent_reports=recent_reports
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard for {username}: {str(e)}")
        return render_template('dashboard.html', username=username, error=str(e))


@app.route('/profile')
def profile():
    """
    User profile page - displays user information and statistics
    """
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    try:
        profile = user_manager.get_user_profile(username)
        stats = user_manager.get_user_statistics(username)
        
        return render_template(
            'profile.html',
            username=username,
            profile=profile,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error loading profile for {username}: {str(e)}")
        return redirect(url_for('dashboard'))

# ============================================================================
# ROUTES - AI FEATURES
# ============================================================================

@app.route('/generate-report', methods=['POST'])
@csrf.exempt
def generate_report():
    """
    Generate personalized AI trends report based on user profile
    
    Returns: JSON with generated report markdown
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        logger.info(f"Generating report for user: {username}")
        
        # Initialize AI pipeline if not already done
        global ai_pipeline
        if ai_pipeline is None:
            ai_pipeline = AIAgentsPipeline()
        
        # Get user profile
        profile = user_manager.get_user_profile(username)
        
        # Generate report
        report_markdown = ai_pipeline.generate_full_report(profile)
        
        # Save report
        report_data = {
            'username': username,
            'profile': profile,
            'report': report_markdown,
            'generated_at': datetime.now().isoformat()
        }
        
        report_filename = user_manager.save_user_report(username, report_data)
        
        logger.info(f"Report generated successfully for {username}: {report_filename}")
        
        return jsonify({
            'success': True,
            'report': report_markdown,
            'filename': report_filename
        })
        
    except Exception as e:
        logger.error(f"Error generating report for {username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/chat', methods=['POST'])
@csrf.exempt
def chat():
    """
    Handle chatbot messages - AI assistant for answering questions
    
    Expects JSON: { "message": "user question", "history": [...] }
    Returns: JSON with AI response
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        logger.info(f"Chat message from {username}: {user_message[:50]}...")
        
        # Initialize AI pipeline if not already done
        global ai_pipeline
        if ai_pipeline is None:
            ai_pipeline = AIAgentsPipeline()
        
        # Get user profile for personalization
        profile = user_manager.get_user_profile(username)
        
        # Generate chatbot response
        response_text = ai_pipeline.chat_with_user(
            user_message=user_message,
            user_profile=profile,
            conversation_history=conversation_history
        )
        
        logger.info(f"Chat response generated for {username}")
        
        return jsonify({
            'success': True,
            'message': response_text
        })
        
    except Exception as e:
        logger.error(f"Error in chat for {username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate response. Please try again.'
        }), 500


@app.route('/generate-linkedin-post', methods=['POST'])
@csrf.exempt
def generate_linkedin_post():
    """
    Generate LinkedIn post from report or custom topic
    
    Expects JSON: { "option": "from_report"|"custom_topic", "topic": "..." }
    Returns: JSON with generated LinkedIn post
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        data = request.get_json()
        option = data.get('option')  # 'from_report' or 'custom_topic'
        topic = data.get('topic', '')  # For custom topic option
        
        logger.info(f"Generating LinkedIn post for {username}, option: {option}")
        
        # Initialize AI pipeline if not already done
        global ai_pipeline
        if ai_pipeline is None:
            ai_pipeline = AIAgentsPipeline()
        
        # Get user profile
        profile = user_manager.get_user_profile(username)
        
        if option == 'from_report':
            # Get the latest report
            recent_reports = user_manager.get_user_reports(username, limit=1)
            
            if not recent_reports:
                return jsonify({
                    'success': False,
                    'error': 'No reports found. Please generate a report first.'
                }), 400
            
            report_content = recent_reports[0]['data'].get('report', '')
            
            if not report_content:
                return jsonify({
                    'success': False,
                    'error': 'Report content not found.'
                }), 400
            
            # Generate LinkedIn post from report
            linkedin_post = ai_pipeline.generate_linkedin_post_from_report(
                report_content=report_content,
                user_profile=profile
            )
            
        elif option == 'custom_topic':
            if not topic or not topic.strip():
                return jsonify({
                    'success': False,
                    'error': 'Please provide a topic.'
                }), 400
            
            # Generate LinkedIn post from custom topic
            linkedin_post = ai_pipeline.generate_linkedin_post_from_topic(
                topic=topic.strip(),
                user_profile=profile
            )
            
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid option. Choose "from_report" or "custom_topic".'
            }), 400
        
        logger.info(f"LinkedIn post generated successfully for {username}")
        
        return jsonify({
            'success': True,
            'post': linkedin_post
        })
        
    except Exception as e:
        logger.error(f"Error generating LinkedIn post for {username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get-youtube-videos', methods=['POST'])
@csrf.exempt
def get_youtube_videos():
    """
    Get personalized YouTube video recommendations based on user profile
    
    Returns: JSON with video list and search keywords
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        logger.info(f"Fetching YouTube videos for {username}")
        
        # Initialize AI pipeline if not already done
        global ai_pipeline
        if ai_pipeline is None:
            ai_pipeline = AIAgentsPipeline()
        
        # Get user profile
        profile = user_manager.get_user_profile(username)
        
        # Get YouTube video recommendations
        result = ai_pipeline.get_personalized_youtube_videos(
            user_profile=profile,
            max_results=8
        )
        
        if result['success']:
            logger.info(f"Successfully fetched {len(result['videos'])} videos for {username}")
            return jsonify({
                'success': True,
                'videos': result['videos'],
                'keywords': result['keywords']
            })
        else:
            logger.error(f"Failed to fetch videos: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch videos')
            }), 500
        
    except Exception as e:
        logger.error(f"Error fetching YouTube videos for {username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ROUTES - LEADERBOARD
# ============================================================================

@app.route('/generate-leaderboard', methods=['POST'])
@csrf.exempt
def generate_leaderboard():
    """
    Generate AI Leaderboard visualization - runs in background
    
    This runs the llm_leaderboard.py script to scrape and visualize
    AI model performance data
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        logger.info(f"Starting leaderboard generation for user: {username}")
        
        # Path to leaderboard script
        leaderboard_script = os.path.join(os.path.dirname(__file__), 'scrapers', 'llm_leaderboard.py')
        
        # Run the leaderboard script in background (non-blocking)
        import threading
        
        def run_leaderboard_script():
            try:
                subprocess.run(
                    [sys.executable, leaderboard_script],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=os.path.dirname(__file__),
                    encoding='utf-8',
                    errors='replace',
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
                )
                logger.info("Leaderboard generation completed")
            except Exception as e:
                logger.error(f"Background leaderboard generation failed: {str(e)}")
        
        # Start background thread
        thread = threading.Thread(target=run_leaderboard_script, daemon=True)
        thread.start()
        
        # Find the most recent existing HTML file (if any)
        import glob
        html_files = glob.glob(os.path.join(os.path.dirname(__file__), 'livebench_leaderboard_*.html'))
        
        if html_files:
            # Get the most recent file
            latest_file = max(html_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            logger.info(f"Using existing leaderboard file: {filename}")
        else:
            # No existing file, user will need to wait for generation
            filename = None
            logger.info("No existing leaderboard file, generating new one")
        
        return jsonify({
            'success': True,
            'message': 'Leaderboard generation started',
            'filename': filename,
            'generating': filename is None
        })
        
    except Exception as e:
        logger.error(f"Error starting leaderboard generation for {username}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@app.route('/leaderboard/<filename>')
def serve_leaderboard(filename):
    """
    Serve the leaderboard HTML file
    
    Security: Only allows files matching the expected pattern
    """
    try:
        # Security: only allow livebench_leaderboard files
        if not filename.startswith('livebench_leaderboard_') or not filename.endswith('.html'):
            return "Invalid file", 403
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not os.path.exists(filepath):
            return "Leaderboard file not found. Please try generating again.", 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return html_content
        
    except Exception as e:
        logger.error(f"Error serving leaderboard: {str(e)}")
        return f"Error loading leaderboard: {str(e)}", 500

# ============================================================================
# ROUTES - REPORTS & DATA
# ============================================================================

@app.route('/get-report/<filename>')
def get_report(filename):
    """
    Get a specific report by filename
    
    Security: Only allows users to access their own reports
    """
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        # Validate filename belongs to user
        if not filename.startswith(f"{username}_report_"):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Load report
        report_path = os.path.join('data/reports', filename)
        
        if not os.path.exists(report_path):
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        import json
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        return jsonify({
            'success': True,
            'report': report_data
        })
        
    except Exception as e:
        logger.error(f"Error loading report {filename}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ROUTES - UTILITY & HEALTH
# ============================================================================

@app.route('/api/check-session')
def check_session():
    """
    Check if user session is valid
    
    Returns: JSON with authentication status
    """
    if 'username' in session:
        return jsonify({
            'authenticated': True,
            'username': session['username']
        })
    else:
        return jsonify({
            'authenticated': False
        })


@app.route('/health')
def health():
    """
    Health check endpoint for monitoring
    
    Returns: JSON with application status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - Page not found"""
    if request.is_json:
        return jsonify({'error': 'Not found'}), 404
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors - Internal server error"""
    logger.error(f"Internal server error: {str(error)}")
    if request.is_json:
        return jsonify({'error': 'Internal server error'}), 500
    return "Internal server error", 500

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Validate configuration before starting
    config_errors = Config.validate_config()
    if config_errors:
        logger.warning("Configuration warnings:")
        for error in config_errors:
            logger.warning(f"  - {error}")
    
    # Start the application
    logger.info("Starting AI Trends Dashboard...")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG'],
        use_reloader=False
    )