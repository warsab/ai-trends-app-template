# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
# 
# This module contains helper functions used throughout the application.
# 
# MAIN CATEGORIES:
# - Directory Management: Create and manage application directories
# - Decorators: Retry logic, performance logging, rate limiting
# - Text Processing: Cleaning, truncating, sanitizing text
# - File Operations: File size calculation, filename sanitization
# - URL Handling: URL validation, domain extraction
# - Logging: Application-wide logging setup
#
# These utilities make the codebase more maintainable and DRY (Don't Repeat Yourself).
# ============================================================================

import os
import logging
import time
import re
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# DIRECTORY MANAGEMENT
# ============================================================================

def setup_directories():
    """
    Create necessary directories if they don't exist.
    
    This function ensures all required directories for the application
    are present. It's called automatically when this module is imported.
    
    Directories created:
    - data/: Main data storage
    - data/users/: User profile YAML files
    - data/reports/: Generated report JSON files
    - logs/: Application log files
    - flask_session/: Flask session data
    """
    directories = [
        'data',
        'data/users',
        'data/reports',
        'logs',
        'flask_session'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")

# ============================================================================
# DECORATORS
# ============================================================================

def retry_on_failure(max_retries=3, delay=1):
    """
    Decorator to retry a function on failure.
    
    Useful for operations that might fail temporarily (e.g., API calls,
    network requests). The function will be retried up to max_retries times
    with a delay between attempts.
    
    Args:
        max_retries (int): Maximum number of retry attempts (default: 3)
        delay (int): Delay between retries in seconds (default: 1)
    
    Usage:
        @retry_on_failure(max_retries=3, delay=2)
        def unstable_function():
            # Function that might fail
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def log_performance(func):
    """
    Decorator to log function execution time.
    
    Automatically logs when a function starts, completes, and how long it took.
    Useful for identifying performance bottlenecks.
    
    Usage:
        @log_performance
        def slow_function():
            # Function code
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {elapsed_time:.2f} seconds")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {elapsed_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper


def rate_limit(calls_per_minute=10):
    """
    Decorator to rate limit function calls.
    
    Ensures a function isn't called more than a specified number of times
    per minute. Useful for API calls with rate limits.
    
    Args:
        calls_per_minute (int): Maximum calls per minute (default: 10)
    
    Usage:
        @rate_limit(calls_per_minute=30)
        def api_call():
            # API request code
            pass
    """
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# ============================================================================
# TEXT PROCESSING
# ============================================================================

def clean_text(text):
    """
    Clean and normalize text content.
    
    Removes excessive whitespace, special characters, URLs, emails, and emojis.
    Useful for preparing scraped content for AI processing.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    
    Example:
        >>> clean_text("Hello!!!   World  http://example.com")
        "Hello! World"
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    
    # Remove emojis and special unicode characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text.strip()


def truncate_text(text, max_length=500):
    """
    Truncate text to a maximum length, ending at a sentence boundary.
    
    Tries to truncate at the last sentence (., ?, !) to avoid cutting
    mid-sentence. If no sentence boundary exists in the last 30% of text,
    truncates at max_length with "..." appended.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length in characters (default: 500)
        
    Returns:
        str: Truncated text
    
    Example:
        >>> truncate_text("First sentence. Second sentence.", max_length=20)
        "First sentence."
    """
    if len(text) <= max_length:
        return text
    
    # Try to truncate at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_question = truncated.rfind('?')
    last_exclamation = truncated.rfind('!')
    
    # Find the last sentence ending
    last_sentence_end = max(last_period, last_question, last_exclamation)
    
    if last_sentence_end > max_length * 0.7:  # Only truncate at sentence if we keep at least 70%
        return truncated[:last_sentence_end + 1]
    else:
        return truncated + '...'

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def sanitize_filename(filename):
    """
    Sanitize a filename to remove invalid characters.
    
    Removes characters that are invalid in file paths on most operating
    systems and replaces spaces with underscores.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename safe for use on any OS
    
    Example:
        >>> sanitize_filename("My File: Version 2.0")
        "My_File_Version_2.0"
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length to 200 characters
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def get_file_size(filepath):
    """
    Get file size in human-readable format.
    
    Converts bytes to KB, MB, GB, or TB as appropriate.
    
    Args:
        filepath (str): Path to file
        
    Returns:
        str: File size (e.g., "1.5 MB", "234 KB")
    
    Example:
        >>> get_file_size("data/report.json")
        "45.3 KB"
    """
    if not os.path.exists(filepath):
        return "0 B"
    
    size = os.path.getsize(filepath)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} TB"

# ============================================================================
# URL HANDLING
# ============================================================================

def validate_url(url):
    """
    Validate if a string is a valid URL.
    
    Checks if URL has both scheme (http/https) and network location (domain).
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not a url")
        False
    """
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_domain(url):
    """
    Extract domain name from URL.
    
    Removes scheme, path, and "www." prefix to get just the domain.
    
    Args:
        url (str): Full URL
        
    Returns:
        str: Domain name (e.g., "example.com")
    
    Example:
        >>> extract_domain("https://www.example.com/path/to/page")
        "example.com"
    """
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except:
        return url

# ============================================================================
# DATA STRUCTURES
# ============================================================================

def chunk_list(lst, chunk_size):
    """
    Split a list into chunks of specified size.
    
    Useful for batch processing or paginating large lists.
    
    Args:
        lst (list): List to chunk
        chunk_size (int): Size of each chunk
        
    Returns:
        list: List of chunks (each chunk is a list)
    
    Example:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts):
    """
    Merge multiple dictionaries.
    
    Later dictionaries override earlier ones for duplicate keys.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        dict: Merged dictionary
    
    Example:
        >>> merge_dicts({'a': 1}, {'b': 2}, {'a': 3})
        {'a': 3, 'b': 2}
    """
    result = {}
    for dictionary in dicts:
        result.update(dictionary)
    return result

# ============================================================================
# DATETIME UTILITIES
# ============================================================================

def format_timestamp(dt=None):
    """
    Format a datetime object as a readable string.
    
    Args:
        dt (datetime): Datetime object (defaults to current time if None)
        
    Returns:
        str: Formatted timestamp (YYYY-MM-DD HH:MM:SS)
    
    Example:
        >>> format_timestamp()
        "2025-10-21 14:30:45"
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_level='INFO'):
    """
    Setup logging configuration for the application.
    
    Creates a logs directory and configures logging to write to both
    a daily log file and the console.
    
    Args:
        log_level (str): Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL
                        (default: 'INFO')
    
    Log files are named: app_YYYYMMDD.log
    """
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_file = os.path.join('logs', f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Logging setup complete. Log file: {log_file}")

# ============================================================================
# AUTOMATIC INITIALIZATION
# ============================================================================

# Initialize directories on module import
# This ensures all necessary directories exist when the app starts
try:
    setup_directories()
except Exception as e:
    logger.warning(f"Could not setup directories: {e}")