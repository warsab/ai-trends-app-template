# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
# 
# This file contains all configuration settings for the AI Trends application.
# 
# IMPORTANT - Before using this application:
# 1. Copy .env.example to .env
# 2. Fill in your API keys in the .env file
# 3. Generate a secure SECRET_KEY (see instructions below)
# 4. Add your users in the USERS dictionary (see instructions below)
# 5. Customize DEFAULT_URLS for your content sources
#
# ============================================================================

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # ========================================================================
    # FLASK CONFIGURATION
    # ========================================================================
    # SECRET_KEY is used for session security and CSRF protection
    # CRITICAL: Change this in production! Generate with:
    # python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # ========================================================================
    # SESSION CONFIGURATION
    # ========================================================================
    # Controls how user sessions are stored and managed
    SESSION_TYPE = 'filesystem'  # Store sessions as files
    SESSION_PERMANENT = True  # Sessions persist after browser closes
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # Sessions last 24 hours
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'flask_session')
    SESSION_FILE_THRESHOLD = 100  # Max number of sessions before cleanup
    
    # ========================================================================
    # API KEYS CONFIGURATION
    # ========================================================================
    # All API keys should be set in your .env file, never hardcode them here!
    # See .env.example for the required format
    
    # OpenAI API - Required for AI report generation and chatbot
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # Tavily API - Optional, for enhanced web searching
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

    # YouTube API - Optional, for personalized video recommendations
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    
    # ========================================================================
    # GPT MODEL CONFIGURATION
    # ========================================================================
    # Configure which OpenAI models to use and their parameters
    GPT_MODEL_STANDARD = os.getenv('GPT_MODEL_STANDARD', 'gpt-3.5-turbo')  # Faster, cheaper
    GPT_MODEL_ADVANCED = os.getenv('GPT_MODEL_ADVANCED', 'gpt-4')  # Smarter, more expensive
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))  # 0.0-1.0: Lower = more focused, Higher = more creative
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))  # Maximum length of AI responses
    
    # ========================================================================
    # DIRECTORY CONFIGURATION
    # ========================================================================
    # Define where application data is stored
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    USERS_DIR = os.path.join(BASE_DIR, 'data', 'users')  # User profile YAML files
    REPORTS_DIR = os.path.join(BASE_DIR, 'data', 'reports')  # Generated reports
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')  # Application logs
    
    # ========================================================================
    # USER AUTHENTICATION
    # ========================================================================
    # Define users who can access the application
    # 
    # HOW TO ADD USERS:
    # 1. Generate a password hash using bcrypt:
    #    python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
    # 2. Create a YAML profile file in data/users/ (e.g., username.yaml)
    # 3. Add the user to this dictionary
    #
    # EXAMPLE USER STRUCTURE:
    # 'username': {
    #     'password': '$2b$12$...hashed_password...',
    #     'profile': 'username.yaml'
    # }
    #
    # SECURITY NOTE: These are hashed passwords, not plain text!
    # ========================================================================
    
    USERS = {
        'demo': {
            'password': '$2b$12$FwcV.QNAog0DCq8zOQz6C.IJYxliA/Idj64/9QzBPoTGZ.CMgQUCC',  # Password: demo123 (CHANGE THIS!)
            'profile': 'demo.yaml'
        },
        # Add more users here following the same pattern
        # 'alice': {
        #     'password': '$2b$12$...',
        #     'profile': 'alice.yaml'
        # },
    }
    
    # ========================================================================
    # WEB SCRAPING CONFIGURATION
    # ========================================================================
    # Configure which websites to scrape for AI trends content
    # Customize this list based on your interests and industry
    
    DEFAULT_URLS = [
        'https://www.technologyreview.com/artificial-intelligence/',
        'https://venturebeat.com/category/ai/',
        'https://www.theverge.com/ai-artificial-intelligence',
        'https://techcrunch.com/category/artificial-intelligence/',
        'https://openai.com/blog'
    ]
    
    # Scraping limits and timeouts
    MAX_URLS = 5  # Maximum number of URLs to scrape per request
    SCRAPE_TIMEOUT = 30  # Seconds to wait before timing out
    MAX_CONTENT_LENGTH = 10000  # Maximum characters to extract per URL
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'  # Browser identity for scraping
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    # Prevent abuse by limiting requests
    MAX_REQUESTS_PER_HOUR = 10  # Maximum report generations per user per hour
    
    # ========================================================================
    # CONTENT PROCESSING
    # ========================================================================
    # Configure how content is processed and chunked for AI
    MIN_PARAGRAPH_LENGTH = 50  # Minimum characters for a paragraph to be included
    MAX_CHUNK_SIZE = 4000  # Maximum characters per chunk for AI processing
    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    # Control application logging behavior
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    # General application behavior settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # Enable debug mode (NEVER in production!)
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'  # Enable testing mode
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        pass
    
    @classmethod
    def validate_config(cls):
        """
        Validate critical configuration settings before app starts.
        Returns a list of configuration errors, if any.
        """
        errors = []
        
        # Check for required API keys
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set - AI features will not work!")
        
        # Check for secure secret key in production
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-change-this-in-production':
            errors.append("SECRET_KEY should be changed in production for security!")
        
        # Warn about default demo user
        if 'demo' in cls.USERS:
            errors.append("WARNING: Default 'demo' user is still active. Remove or change password in production!")
        
        return errors


# ============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATIONS
# ============================================================================
# Different settings for development, production, and testing environments

class DevelopmentConfig(Config):
    """Development configuration - Use for local development"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration - Use for deployed application"""
    DEBUG = False
    TESTING = False
    
    # Enhanced security settings for production
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection


class TestingConfig(Config):
    """Testing configuration - Use for automated tests"""
    DEBUG = True
    TESTING = True
    
    # Use faster/cheaper models for testing
    GPT_MODEL_STANDARD = 'gpt-3.5-turbo'
    GPT_MODEL_ADVANCED = 'gpt-3.5-turbo'


# ============================================================================
# CONFIGURATION DICTIONARY
# ============================================================================
# Select configuration based on environment
# Usage: config[os.getenv('FLASK_ENV', 'development')]

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}