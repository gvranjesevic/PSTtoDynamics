"""
Configuration Settings Template for PST to Dynamics 365 Import System
====================================================================

SECURITY NOTICE: This file previously contained sensitive credentials.
All sensitive data has been removed for security reasons.

For configuration, please use environment variables or the secure
configuration system in config.py instead.

This file is kept for historical reference only.
"""

import os

# === SECURITY NOTICE ===
# This configuration file has been sanitized to remove all sensitive information.
# 
# To configure the application:
# 1. Copy environment_template.txt to .env
# 2. Fill in your actual values in the .env file
# 3. Use the secure configuration system in config.py
#
# NEVER commit actual credentials to version control!

# === DYNAMICS 365 AUTHENTICATION ===
# Use environment variables instead:
# DYNAMICS_USERNAME=your.email@company.com
# DYNAMICS_PASSWORD=your_secure_password
# DYNAMICS_TENANT_DOMAIN=company.com
# DYNAMICS_CLIENT_ID=your-client-id
USERNAME = os.getenv("DYNAMICS_USERNAME", "CONFIGURE_IN_ENV_FILE")
PASSWORD = None  # Use environment variable DYNAMICS_PASSWORD or keyring
TENANT_DOMAIN = os.getenv("DYNAMICS_TENANT_DOMAIN", "CONFIGURE_IN_ENV_FILE")
CLIENT_ID = os.getenv("DYNAMICS_CLIENT_ID", "CONFIGURE_IN_ENV_FILE")
CRM_BASE_URL = os.getenv("DYNAMICS_CRM_URL", "https://yourorg.crm.dynamics.com/api/data/v9.2")

# === PST FILE CONFIGURATION ===
# Use environment variables for file paths:
# DEFAULT_PST_PATH=C:\path\to\your\default.pst
# CURRENT_PST_PATH=C:\path\to\your\current.pst
DEFAULT_PST_PATH = os.getenv("DEFAULT_PST_PATH", r"CONFIGURE_IN_ENV_FILE")
CURRENT_PST_PATH = os.getenv("CURRENT_PST_PATH", r"PST\configure_in_env.pst")

# === SYSTEM CONFIGURATION ===
# Use environment variable: SYSTEM_USER_ID=your-system-user-id
SYSTEM_USER_ID = os.getenv("SYSTEM_USER_ID", "CONFIGURE_IN_ENV_FILE")

# === IMPORT BEHAVIOR SETTINGS ===
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))  # Number of emails to process in each batch
MAX_RETRIES = 3  # Maximum retries for failed operations
RETRY_DELAY = 2  # Seconds to wait between retries

# === SAFETY SETTINGS ===
REQUIRE_USER_CONFIRMATION = True  # Require confirmation for major operations
BACKUP_BEFORE_IMPORT = True  # Create backup before importing
TEST_MODE_DEFAULT = True  # Start in test mode by default

# === FILTERING SETTINGS ===
EXCLUDE_TEAMS_MESSAGES = True  # Skip Microsoft Teams messages
EXCLUDE_AUTOMATED_EMAILS = True  # Skip automated system emails
MIN_EMAIL_LENGTH = 10  # Minimum email body length to import

# === DUPLICATE DETECTION ===
DUPLICATE_THRESHOLD_HOURS = 1  # Hours within which emails are considered duplicates
CHECK_SUBJECT_SIMILARITY = True  # Compare subject lines for duplicates
CHECK_BODY_SIMILARITY = False  # Compare email bodies (slower)

# === LOGGING CONFIGURATION ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE_PATH = "import_logs"
MAX_LOG_FILE_SIZE_MB = 100

# === CONTACT CREATION SETTINGS ===
AUTO_CREATE_CONTACTS = False  # Automatically create missing contacts
REQUIRE_CONTACT_CONFIRMATION = True  # Ask before creating new contacts

# === EMAIL STATUS SETTINGS ===
DEFAULT_EMAIL_STATUS = "Closed"  # Default status for imported emails
PRESERVE_ORIGINAL_DATES = True  # Use original email dates, not import date

# === ATTACHMENT HANDLING ===
IMPORT_ATTACHMENTS = False  # Include attachments in import (Phase 3 feature)
MAX_ATTACHMENT_SIZE_MB = 25  # Maximum attachment size to import

# === UI CONFIGURATION ===
SHOW_PROGRESS_BARS = True
DETAILED_PROGRESS = True
QUIET_MODE = False

# === VALIDATION ===
def validate_config():
    """Validate configuration settings."""
    errors = []
    
    if USERNAME == "CONFIGURE_IN_ENV_FILE":
        errors.append("USERNAME must be configured via environment variable DYNAMICS_USERNAME")
    
    if not PASSWORD:
        errors.append("PASSWORD must be configured via environment variable DYNAMICS_PASSWORD or keyring")
    
    if TENANT_DOMAIN == "CONFIGURE_IN_ENV_FILE":
        errors.append("TENANT_DOMAIN must be configured via environment variable DYNAMICS_TENANT_DOMAIN")
    
    if CLIENT_ID == "CONFIGURE_IN_ENV_FILE":
        errors.append("CLIENT_ID must be configured via environment variable DYNAMICS_CLIENT_ID")
    
    if CURRENT_PST_PATH != "PST\\configure_in_env.pst" and not os.path.exists(CURRENT_PST_PATH):
        errors.append(f"PST file not found: {CURRENT_PST_PATH}")
    
    if BATCH_SIZE < 1 or BATCH_SIZE > 1000:
        errors.append("BATCH_SIZE must be between 1 and 1000")
    
    return errors

# === PHASE 2 CONTACT CREATION SETTINGS ===
CONTACT_CREATION = {
    'AUTO_CREATE_MISSING': True,        # Automatically create missing contacts
    'EXTRACT_FROM_DISPLAY_NAME': True,  # Use sender display names when available
    'EXTRACT_COMPANY_FROM_DOMAIN': True, # Extract company from email domain
    'VALIDATE_EMAIL_FORMAT': True,      # Validate email addresses before creation
    'SKIP_SERVICE_EMAILS': False,       # Skip obvious service/automated emails
    'MAX_CONTACTS_PER_BATCH': 25,       # Maximum contacts to create in one batch
    'REQUIRE_CONFIRMATION': True,       # Ask before creating contacts
    'DEFAULT_CONTACT_SOURCE': 'PST Import' # Default source for created contacts
}

# === PHASE 2 ADVANCED COMPARISON SETTINGS ===
ADVANCED_COMPARISON = {
    'USE_MESSAGE_ID': True,             # Use Message-ID header for matching
    'USE_CONTENT_HASH': True,           # Use content hash for duplicate detection
    'FUZZY_TIMESTAMP_MINUTES': 5,       # Minutes tolerance for timestamp matching
    'SUBJECT_SIMILARITY_THRESHOLD': 0.8, # Threshold for subject similarity (0-1)
    'SENDER_RECIPIENT_MATCHING': True,   # Match by sender+recipient combination
    'CONTENT_SIMILARITY_THRESHOLD': 0.9 # Threshold for content similarity (0-1)
}

# === PHASE 2 BULK PROCESSING SETTINGS ===
BULK_PROCESSING = {
    'ENABLE_BULK_MODE': False,          # Enable processing beyond test limits
    'MAX_EMAILS_PER_SESSION': int(os.getenv("MAX_EMAILS_PER_SESSION", "5000")),
    'BATCH_SIZE_BULK': 100,             # Batch size for bulk operations
    'PARALLEL_PROCESSING': False,       # Enable parallel processing (experimental)
    'MEMORY_OPTIMIZATION': True,        # Use memory-efficient processing
    'CHECKPOINT_INTERVAL': 500,         # Save progress every N emails
    'AUTO_RESUME': True                 # Automatically resume interrupted imports
}

# === PHASE 2 ANALYTICS SETTINGS ===
IMPORT_ANALYTICS = {
    'ENABLE_ANALYTICS': True,           # Enable detailed analytics tracking
    'TRACK_SENDER_STATISTICS': True,    # Track statistics by sender
    'TRACK_TIMELINE_COMPLETENESS': True, # Analyze timeline completeness
    'EXPORT_REPORTS': True,             # Enable report export functionality
    'REPORT_FORMATS': ['json', 'csv'],  # Available report formats
    'ANALYTICS_RETENTION_DAYS': 90      # Days to retain analytics data
}

# === FEATURE FLAGS (for phased implementation) ===
class FeatureFlags:
    # Phase 1 Features (COMPLETE)
    TIMELINE_CLEANUP = True
    PST_READING = True
    BASIC_IMPORT = True
    
    # Phase 2 Features (COMPLETE)
    CONTACT_CREATION = True
    ADVANCED_COMPARISON = True
    BULK_PROCESSING = True
    IMPORT_ANALYTICS = True
    
    # Phase 3 Features (PLANNED)
    ATTACHMENT_HANDLING = False
    BATCH_OPTIMIZATION = False
    
    # Phase 4 Features (PLANNED)
    ENTERPRISE_UI = False
    ADVANCED_REPORTING = False 