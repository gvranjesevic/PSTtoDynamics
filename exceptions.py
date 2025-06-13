"""
Custom Exception Classes for PST-to-Dynamics Application
=======================================================

Defines specific exception types for better error handling and debugging.
All exceptions inherit from a base PSTDynamicsException class.
"""

class PSTDynamicsException(Exception):
    """Base exception class for all PST-to-Dynamics related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# === PST File Related Exceptions ===

class PSTException(PSTDynamicsException):
    """Base exception for PST file related errors."""
    pass

class PSTFileNotFoundException(PSTException):
    """Raised when PST file cannot be found."""
    
    def __init__(self, file_path: str):
        super().__init__(f"PST file not found: {file_path}", "PST_FILE_NOT_FOUND", {"file_path": file_path})
        self.file_path = file_path

class PSTFileCorruptedException(PSTException):
    """Raised when PST file is corrupted or unreadable."""
    
    def __init__(self, file_path: str, corruption_details: str = None):
        message = f"PST file is corrupted: {file_path}"
        if corruption_details:
            message += f" - {corruption_details}"
        super().__init__(message, "PST_FILE_CORRUPTED", {
            "file_path": file_path,
            "corruption_details": corruption_details
        })
        self.file_path = file_path

class PSTAccessDeniedException(PSTException):
    """Raised when access to PST file is denied."""
    
    def __init__(self, file_path: str):
        super().__init__(f"Access denied to PST file: {file_path}", "PST_ACCESS_DENIED", {"file_path": file_path})
        self.file_path = file_path

class PSTReadException(PSTException):
    """Raised when error occurs reading PST file content."""
    
    def __init__(self, file_path: str, read_error: str):
        super().__init__(f"Error reading PST file {file_path}: {read_error}", "PST_READ_ERROR", {
            "file_path": file_path,
            "read_error": read_error
        })
        self.file_path = file_path
        self.read_error = read_error


# === Dynamics 365 Related Exceptions ===

class DynamicsException(PSTDynamicsException):
    """Base exception for Dynamics 365 related errors."""
    pass

class DynamicsAuthenticationException(DynamicsException):
    """Raised when Dynamics 365 authentication fails."""
    
    def __init__(self, username: str = None, auth_error: str = None):
        message = "Dynamics 365 authentication failed"
        if username:
            message += f" for user: {username}"
        if auth_error:
            message += f" - {auth_error}"
        super().__init__(message, "DYNAMICS_AUTH_FAILED", {
            "username": username,
            "auth_error": auth_error
        })
        self.username = username

class DynamicsAPIException(DynamicsException):
    """Raised when Dynamics 365 API calls fail."""
    
    def __init__(self, endpoint: str, status_code: int = None, api_error: str = None):
        message = f"Dynamics 365 API error at {endpoint}"
        if status_code:
            message += f" (HTTP {status_code})"
        if api_error:
            message += f": {api_error}"
        super().__init__(message, "DYNAMICS_API_ERROR", {
            "endpoint": endpoint,
            "status_code": status_code,
            "api_error": api_error
        })
        self.endpoint = endpoint
        self.status_code = status_code

class DynamicsConnectionException(DynamicsException):
    """Raised when connection to Dynamics 365 fails."""
    
    def __init__(self, url: str, connection_error: str = None):
        message = f"Failed to connect to Dynamics 365: {url}"
        if connection_error:
            message += f" - {connection_error}"
        super().__init__(message, "DYNAMICS_CONNECTION_FAILED", {
            "url": url,
            "connection_error": connection_error
        })
        self.url = url

class DynamicsRateLimitException(DynamicsException):
    """Raised when Dynamics 365 rate limit is exceeded."""
    
    def __init__(self, retry_after: int = None):
        message = "Dynamics 365 rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, "DYNAMICS_RATE_LIMIT", {"retry_after": retry_after})
        self.retry_after = retry_after


# === Import Process Exceptions ===

class ImportException(PSTDynamicsException):
    """Base exception for import process errors."""
    pass

class EmailImportException(ImportException):
    """Raised when individual email import fails."""
    
    def __init__(self, email_subject: str = None, sender: str = None, import_error: str = None):
        message = "Email import failed"
        if email_subject:
            message += f" for email: '{email_subject}'"
        if sender:
            message += f" from: {sender}"
        if import_error:
            message += f" - {import_error}"
        super().__init__(message, "EMAIL_IMPORT_FAILED", {
            "email_subject": email_subject,
            "sender": sender,
            "import_error": import_error
        })
        self.email_subject = email_subject
        self.sender = sender

class ContactCreationException(ImportException):
    """Raised when contact creation fails."""
    
    def __init__(self, contact_email: str, creation_error: str = None):
        message = f"Failed to create contact: {contact_email}"
        if creation_error:
            message += f" - {creation_error}"
        super().__init__(message, "CONTACT_CREATION_FAILED", {
            "contact_email": contact_email,
            "creation_error": creation_error
        })
        self.contact_email = contact_email

class DuplicateDetectionException(ImportException):
    """Raised when duplicate detection process fails."""
    
    def __init__(self, detection_error: str):
        super().__init__(f"Duplicate detection failed: {detection_error}", "DUPLICATE_DETECTION_FAILED", {
            "detection_error": detection_error
        })

class BatchProcessingException(ImportException):
    """Raised when batch processing fails."""
    
    def __init__(self, batch_size: int, processed_count: int, batch_error: str = None):
        message = f"Batch processing failed after {processed_count}/{batch_size} items"
        if batch_error:
            message += f": {batch_error}"
        super().__init__(message, "BATCH_PROCESSING_FAILED", {
            "batch_size": batch_size,
            "processed_count": processed_count,
            "batch_error": batch_error
        })
        self.batch_size = batch_size
        self.processed_count = processed_count


# === Configuration Exceptions ===

class ConfigurationException(PSTDynamicsException):
    """Base exception for configuration related errors."""
    pass

class MissingConfigurationException(ConfigurationException):
    """Raised when required configuration is missing."""
    
    def __init__(self, config_key: str, config_section: str = None):
        message = f"Missing required configuration: {config_key}"
        if config_section:
            message += f" in section: {config_section}"
        super().__init__(message, "MISSING_CONFIGURATION", {
            "config_key": config_key,
            "config_section": config_section
        })
        self.config_key = config_key

class InvalidConfigurationException(ConfigurationException):
    """Raised when configuration values are invalid."""
    
    def __init__(self, config_key: str, config_value: str, validation_error: str):
        super().__init__(f"Invalid configuration for {config_key}='{config_value}': {validation_error}", 
                        "INVALID_CONFIGURATION", {
            "config_key": config_key,
            "config_value": config_value,
            "validation_error": validation_error
        })
        self.config_key = config_key
        self.config_value = config_value


# === Database Exceptions ===

class DatabaseException(PSTDynamicsException):
    """Base exception for database related errors."""
    pass

class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails."""
    
    def __init__(self, database_path: str, connection_error: str = None):
        message = f"Failed to connect to database: {database_path}"
        if connection_error:
            message += f" - {connection_error}"
        super().__init__(message, "DATABASE_CONNECTION_FAILED", {
            "database_path": database_path,
            "connection_error": connection_error
        })
        self.database_path = database_path

class DatabaseIntegrityException(DatabaseException):
    """Raised when database integrity check fails."""
    
    def __init__(self, database_path: str, integrity_error: str):
        super().__init__(f"Database integrity error in {database_path}: {integrity_error}", 
                        "DATABASE_INTEGRITY_ERROR", {
            "database_path": database_path,
            "integrity_error": integrity_error
        })
        self.database_path = database_path

class DatabaseQueryException(DatabaseException):
    """Raised when database query fails."""
    
    def __init__(self, query: str, query_error: str):
        super().__init__(f"Database query failed: {query_error}", "DATABASE_QUERY_FAILED", {
            "query": query,
            "query_error": query_error
        })
        self.query = query


# === Sync Engine Exceptions ===

class SyncException(PSTDynamicsException):
    """Base exception for sync engine errors."""
    pass

class SyncConflictException(SyncException):
    """Raised when sync conflicts cannot be resolved."""
    
    def __init__(self, field_name: str, source_value: str, target_value: str):
        super().__init__(f"Unresolvable sync conflict for field '{field_name}': {source_value} vs {target_value}", 
                        "SYNC_CONFLICT_UNRESOLVABLE", {
            "field_name": field_name,
            "source_value": source_value,
            "target_value": target_value
        })
        self.field_name = field_name
        self.source_value = source_value
        self.target_value = target_value

class SyncValidationException(SyncException):
    """Raised when sync data validation fails."""
    
    def __init__(self, validation_error: str, data_field: str = None):
        message = f"Sync validation failed: {validation_error}"
        if data_field:
            message += f" (field: {data_field})"
        super().__init__(message, "SYNC_VALIDATION_FAILED", {
            "validation_error": validation_error,
            "data_field": data_field
        })
        self.data_field = data_field


# === GUI Exceptions ===

class GUIException(PSTDynamicsException):
    """Base exception for GUI related errors."""
    pass

class WidgetInitializationException(GUIException):
    """Raised when GUI widget initialization fails."""
    
    def __init__(self, widget_name: str, init_error: str):
        super().__init__(f"Failed to initialize widget '{widget_name}': {init_error}", 
                        "WIDGET_INIT_FAILED", {
            "widget_name": widget_name,
            "init_error": init_error
        })
        self.widget_name = widget_name

class ThemeLoadException(GUIException):
    """Raised when theme loading fails."""
    
    def __init__(self, theme_name: str, load_error: str):
        super().__init__(f"Failed to load theme '{theme_name}': {load_error}", 
                        "THEME_LOAD_FAILED", {
            "theme_name": theme_name,
            "load_error": load_error
        })
        self.theme_name = theme_name


# === Utility Functions ===

def handle_exception(func):
    """Decorator to handle exceptions and convert them to PSTDynamicsException if needed."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PSTDynamicsException:
            # Re-raise our custom exceptions as-is
            raise
        except FileNotFoundError as e:
            if str(e).endswith('.pst'):
                raise PSTFileNotFoundException(str(e).split("'")[1])
            raise DatabaseConnectionException(str(e), "File not found")
        except PermissionError as e:
            if str(e).endswith('.pst'):
                raise PSTAccessDeniedException(str(e).split("'")[1])
            raise ConfigurationException(f"Permission denied: {e}")
        except ConnectionError as e:
            raise DynamicsConnectionException("Unknown", str(e))
        except Exception as e:
            # Convert unknown exceptions to base exception
            raise PSTDynamicsException(f"Unexpected error in {func.__name__}: {str(e)}", 
                                     "UNEXPECTED_ERROR", {"function": func.__name__})
    return wrapper

def get_user_friendly_message(exception: Exception) -> str:
    """Convert technical exceptions to user-friendly messages."""
    if isinstance(exception, PSTFileNotFoundException):
        return f"The PST file could not be found. Please check the file path: {exception.file_path}"
    elif isinstance(exception, PSTFileCorruptedException):
        return "The PST file appears to be corrupted. Please try with a different PST file or repair the current one."
    elif isinstance(exception, DynamicsAuthenticationException):
        return "Failed to sign in to Dynamics 365. Please check your username and password."
    elif isinstance(exception, DynamicsConnectionException):
        return "Could not connect to Dynamics 365. Please check your internet connection and try again."
    elif isinstance(exception, DynamicsRateLimitException):
        retry_msg = f" Please wait {exception.retry_after} seconds before trying again." if exception.retry_after else ""
        return f"Too many requests to Dynamics 365. The service is temporarily limiting requests.{retry_msg}"
    elif isinstance(exception, MissingConfigurationException):
        return f"Configuration is incomplete. Please set up: {exception.config_key}"
    elif isinstance(exception, PSTDynamicsException):
        return exception.message
    else:
        return f"An unexpected error occurred: {str(exception)}"

def log_exception(exception: Exception, logger, context: dict = None):
    """Log exceptions with proper formatting and context."""
    context = context or {}
    
    if isinstance(exception, PSTDynamicsException):
        logger.error(f"[{exception.error_code}] {exception.message}")
        if exception.details:
            logger.error(f"Details: {exception.details}")
    else:
        logger.error(f"Unexpected exception: {str(exception)}")
    
    if context:
        logger.error(f"Context: {context}")
    
    # Log stack trace for debugging
    import traceback
    logger.debug(f"Stack trace: {traceback.format_exc()}") 