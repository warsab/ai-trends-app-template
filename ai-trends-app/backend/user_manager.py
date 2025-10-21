# ============================================================================
# USER MANAGER
# ============================================================================
# 
# This module handles all user-related operations:
# - User authentication with bcrypt password hashing
# - User profile management (loading from YAML files)
# - Report storage and retrieval
# - User statistics and data export
#
# USER PROFILES:
# - Stored as YAML files in data/users/ directory
# - Each user has a profile file (e.g., demo.yaml)
# - Profiles contain: name, email, job_title, interests, tags
#
# AUTHENTICATION:
# - Uses bcrypt for secure password hashing
# - Passwords are stored as hashed strings in config.py
# - Never store plain text passwords!
#
# ============================================================================

import os
import yaml
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserManager:
    """
    Handles user authentication and profile management.
    
    This class is responsible for:
    - Authenticating users with bcrypt password hashing
    - Loading and saving user profiles from YAML files
    - Managing generated reports
    - Tracking user statistics
    """
    
    def __init__(self, users_config=None, users_dir=None, reports_dir=None):
        """
        Initialize the UserManager.
        
        Args:
            users_config (dict): User configuration (default: from Config.USERS)
            users_dir (str): Directory for user profile YAML files
            reports_dir (str): Directory for storing generated reports
        """
        # Import here to avoid circular imports
        from config import Config
        
        self.users = users_config or Config.USERS
        self.users_dir = users_dir or Config.USERS_DIR
        self.reports_dir = reports_dir or Config.REPORTS_DIR
        
        # Create directories if they don't exist
        os.makedirs(self.users_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Create sample user profile if it doesn't exist
        self._create_sample_profile()
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def authenticate(self, username, password):
        """
        Authenticate user credentials with bcrypt password hashing.
        
        Args:
            username (str): Username to authenticate
            password (str): Plain text password to verify
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if username in self.users:
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            stored_hash = self.users[username]['password']
        
            # Check if password matches the hash
            return bcrypt.check_password_hash(stored_hash, password)
        return False
    
    # ========================================================================
    # PROFILE MANAGEMENT
    # ========================================================================
    
    def get_user_profile(self, username):
        """
        Load user profile from YAML file.
        
        Each user has a YAML file in data/users/ containing their profile data.
        If the file doesn't exist, returns a default profile.
        
        Args:
            username (str): Username to load profile for
            
        Returns:
            dict: User profile with keys: name, email, job_title, interests, tags
            
        Raises:
            ValueError: If user doesn't exist in configuration
        """
        if username not in self.users:
            raise ValueError(f"User {username} not found")
        
        profile_file = self.users[username]['profile']
        profile_path = os.path.join(self.users_dir, profile_file)
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = yaml.safe_load(f)
            
            logger.info(f"Loaded profile for user {username}")
            return profile
            
        except FileNotFoundError:
            logger.error(f"Profile file not found for user {username}: {profile_path}")
            # Return default profile
            return self._get_default_profile(username)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML profile for {username}: {str(e)}")
            return self._get_default_profile(username)
    
    def update_user_profile(self, username, profile_data):
        """
        Update user profile YAML file.
        
        Args:
            username (str): Username to update profile for
            profile_data (dict): New profile data
            
        Returns:
            bool: True if update successful
            
        Raises:
            ValueError: If user doesn't exist
        """
        if username not in self.users:
            raise ValueError(f"User {username} not found")
        
        profile_file = self.users[username]['profile']
        profile_path = os.path.join(self.users_dir, profile_file)
        
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                yaml.dump(profile_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Updated profile for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating profile for {username}: {str(e)}")
            raise
    
    def _get_default_profile(self, username):
        """
        Return default profile if user profile file doesn't exist.
        
        This is a fallback to ensure the app doesn't crash if a profile file
        is missing or corrupted.
        
        Args:
            username (str): Username to create default profile for
            
        Returns:
            dict: Default user profile
        """
        return {
            'name': username.replace('_', ' ').title(),
            'email': f"{username}@example.com",
            'job_title': 'AI Enthusiast',
            'interests': 'General interest in artificial intelligence and technology trends.',
            'tags': ['artificial_intelligence', 'technology', 'innovation']
        }
    
    def _create_sample_profile(self):
        """
        Create a sample demo user profile if it doesn't exist.
        
        This creates the demo.yaml profile file that matches the demo user
        in config.py. This is useful for first-time setup and testing.
        
        CUSTOMIZATION:
        - Modify this to create your own default user profiles
        - Or remove this method entirely if you don't want auto-created profiles
        """
        demo_profile = {
            'name': 'Demo User',
            'email': 'demo@example.com',
            'job_title': 'AI Enthusiast',
            'interests': """I'm interested in staying up-to-date with the latest developments in artificial intelligence, 
machine learning, and emerging technologies. I want to understand how AI is transforming various industries 
and learn about practical applications, best practices, and future trends. I'm particularly focused on 
understanding AI tools, automation, and innovation in my field.""",
            'tags': ['artificial_intelligence', 'machine_learning', 'ai_trends', 'technology', 'innovation', 'automation']
        }
        
        profile_path = os.path.join(self.users_dir, 'demo.yaml')
        
        if not os.path.exists(profile_path):
            try:
                with open(profile_path, 'w', encoding='utf-8') as f:
                    yaml.dump(demo_profile, f, default_flow_style=False, allow_unicode=True)
                
                logger.info("Created demo user profile: demo.yaml")
                
            except Exception as e:
                logger.error(f"Error creating demo profile: {str(e)}")
        else:
            logger.info("Demo profile already exists: demo.yaml")
    
    # ========================================================================
    # REPORT MANAGEMENT
    # ========================================================================
    
    def save_user_report(self, username, report_data):
        """
        Save generated report for user.
        
        Reports are saved as JSON files with timestamps in the filename.
        Format: {username}_report_{timestamp}.json
        
        Args:
            username (str): Username to save report for
            report_data (dict): Report data to save
            
        Returns:
            str: Filename of saved report
            
        Raises:
            Exception: If file write fails
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{username}_report_{timestamp}.json"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report saved for user {username}: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error saving report for {username}: {str(e)}")
            raise
    
    def get_user_reports(self, username, limit=10):
        """
        Get recent reports for user.
        
        Returns the most recent reports, sorted by timestamp (newest first).
        
        Args:
            username (str): Username to get reports for
            limit (int): Maximum number of reports to return (default: 10)
            
        Returns:
            list: List of report dictionaries with 'filename' and 'data' keys
        """
        try:
            report_files = [
                f for f in os.listdir(self.reports_dir) 
                if f.startswith(f"{username}_report_") and f.endswith('.json')
            ]
            
            # Sort by timestamp (newest first)
            report_files.sort(reverse=True)
            
            reports = []
            for report_file in report_files[:limit]:
                report_path = os.path.join(self.reports_dir, report_file)
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    reports.append({
                        'filename': report_file,
                        'data': report_data
                    })
            
            return reports
            
        except Exception as e:
            logger.error(f"Error loading reports for {username}: {str(e)}")
            return []
    
    def delete_user_report(self, username, report_filename):
        """
        Delete a specific report for a user.
        
        Security: Validates that the report belongs to the user before deletion.
        
        Args:
            username (str): Username who owns the report
            report_filename (str): Filename of report to delete
            
        Returns:
            bool: True if deletion successful, False if file not found
            
        Raises:
            ValueError: If report doesn't belong to user
        """
        try:
            # Validate that the report belongs to the user
            if not report_filename.startswith(f"{username}_report_"):
                raise ValueError("Report does not belong to this user")
            
            report_path = os.path.join(self.reports_dir, report_filename)
            
            if os.path.exists(report_path):
                os.remove(report_path)
                logger.info(f"Deleted report {report_filename} for user {username}")
                return True
            else:
                logger.warning(f"Report file not found: {report_filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting report for {username}: {str(e)}")
            raise
    
    # ========================================================================
    # USER STATISTICS & DATA
    # ========================================================================
    
    def get_user_statistics(self, username):
        """
        Get statistics for a user.
        
        Calculates useful metrics like total reports generated,
        last report date, and total sources analyzed.
        
        Args:
            username (str): Username to get statistics for
            
        Returns:
            dict: Statistics with keys:
                - total_reports (int)
                - last_report_date (str or None)
                - total_sources_analyzed (int)
        """
        try:
            reports = self.get_user_reports(username, limit=100)
            
            total_reports = len(reports)
            
            if total_reports == 0:
                return {
                    'total_reports': 0,
                    'last_report_date': None,
                    'total_sources_analyzed': 0
                }
            
            # Get last report date
            last_report = reports[0] if reports else None
            last_report_date = None
            if last_report and 'data' in last_report:
                last_report_date = last_report['data'].get('generated_at')
            
            # Count total sources analyzed across all reports
            total_sources = sum(
                len(report['data'].get('references', [])) 
                for report in reports 
                if 'data' in report
            )
            
            return {
                'total_reports': total_reports,
                'last_report_date': last_report_date,
                'total_sources_analyzed': total_sources
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics for {username}: {str(e)}")
            return {
                'total_reports': 0,
                'last_report_date': None,
                'total_sources_analyzed': 0
            }
    
    def export_user_data(self, username):
        """
        Export all user data including profile and reports.
        
        Useful for data portability, backups, or GDPR compliance.
        
        Args:
            username (str): Username to export data for
            
        Returns:
            dict: Complete user data export
            
        Raises:
            ValueError: If user doesn't exist
        """
        try:
            if username not in self.users:
                raise ValueError(f"User {username} not found")
            
            # Get profile
            profile = self.get_user_profile(username)
            
            # Get all reports
            reports = self.get_user_reports(username, limit=None)
            
            # Get statistics
            stats = self.get_user_statistics(username)
            
            export_data = {
                'username': username,
                'profile': profile,
                'statistics': stats,
                'reports': reports,
                'export_date': datetime.now().isoformat()
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting data for {username}: {str(e)}")
            raise
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def user_exists(self, username):
        """
        Check if a user exists in the system.
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return username in self.users
    
    def get_all_users(self):
        """
        Get list of all registered users.
        
        Returns:
            list: List of usernames
        """
        return list(self.users.keys())