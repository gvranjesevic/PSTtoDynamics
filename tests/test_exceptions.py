"""
Unit tests for the custom exception handling system.
"""

import unittest
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import (
    PSTDynamicsException,
    PSTFileNotFoundException,
    PSTFileCorruptedException,
    PSTAccessDeniedException,
    DynamicsAuthenticationException,
    DynamicsAPIException,
    DynamicsConnectionException,
    DynamicsRateLimitException,
    EmailImportException,
    ContactCreationException,
    MissingConfigurationException,
    InvalidConfigurationException,
    DatabaseConnectionException,
    SyncConflictException,
    handle_exception,
    get_user_friendly_message,
    log_exception
)
import logging


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_base_exception(self):
        """Test the base PSTDynamicsException."""
        exception = PSTDynamicsException("Test message", "TEST_CODE", {"key": "value"})
        
        self.assertEqual(str(exception), "[TEST_CODE] Test message")
        self.assertEqual(exception.message, "Test message")
        self.assertEqual(exception.error_code, "TEST_CODE")
        self.assertEqual(exception.details, {"key": "value"})
    
    def test_pst_file_not_found_exception(self):
        """Test PST file not found exception."""
        file_path = "/path/to/missing.pst"
        exception = PSTFileNotFoundException(file_path)
        
        self.assertIn(file_path, str(exception))
        self.assertEqual(exception.file_path, file_path)
        self.assertEqual(exception.error_code, "PST_FILE_NOT_FOUND")
    
    def test_pst_file_corrupted_exception(self):
        """Test PST file corrupted exception."""
        file_path = "/path/to/corrupted.pst"
        corruption_details = "Invalid header"
        exception = PSTFileCorruptedException(file_path, corruption_details)
        
        self.assertIn(file_path, str(exception))
        self.assertIn(corruption_details, str(exception))
        self.assertEqual(exception.file_path, file_path)
    
    def test_dynamics_authentication_exception(self):
        """Test Dynamics authentication exception."""
        username = "test@example.com"
        auth_error = "Invalid credentials"
        exception = DynamicsAuthenticationException(username, auth_error)
        
        self.assertIn(username, str(exception))
        self.assertIn(auth_error, str(exception))
        self.assertEqual(exception.username, username)
    
    def test_dynamics_api_exception(self):
        """Test Dynamics API exception."""
        endpoint = "/api/data/v9.2/contacts"
        status_code = 404
        api_error = "Resource not found"
        exception = DynamicsAPIException(endpoint, status_code, api_error)
        
        self.assertIn(endpoint, str(exception))
        self.assertIn("404", str(exception))
        self.assertIn(api_error, str(exception))
        self.assertEqual(exception.endpoint, endpoint)
        self.assertEqual(exception.status_code, status_code)
    
    def test_dynamics_rate_limit_exception(self):
        """Test Dynamics rate limit exception."""
        retry_after = 30
        exception = DynamicsRateLimitException(retry_after)
        
        self.assertIn("rate limit", str(exception).lower())
        self.assertIn("30", str(exception))
        self.assertEqual(exception.retry_after, retry_after)
    
    def test_email_import_exception(self):
        """Test email import exception."""
        subject = "Test Email Subject"
        sender = "sender@example.com"
        import_error = "Failed to create email record"
        exception = EmailImportException(subject, sender, import_error)
        
        self.assertIn(subject, str(exception))
        self.assertIn(sender, str(exception))
        self.assertIn(import_error, str(exception))
        self.assertEqual(exception.email_subject, subject)
        self.assertEqual(exception.sender, sender)
    
    def test_contact_creation_exception(self):
        """Test contact creation exception."""
        contact_email = "contact@example.com"
        creation_error = "Duplicate email address"
        exception = ContactCreationException(contact_email, creation_error)
        
        self.assertIn(contact_email, str(exception))
        self.assertIn(creation_error, str(exception))
        self.assertEqual(exception.contact_email, contact_email)
    
    def test_missing_configuration_exception(self):
        """Test missing configuration exception."""
        config_key = "USERNAME"
        config_section = "authentication"
        exception = MissingConfigurationException(config_key, config_section)
        
        self.assertIn(config_key, str(exception))
        self.assertIn(config_section, str(exception))
        self.assertEqual(exception.config_key, config_key)
    
    def test_sync_conflict_exception(self):
        """Test sync conflict exception."""
        field_name = "email"
        source_value = "old@example.com"
        target_value = "new@example.com"
        exception = SyncConflictException(field_name, source_value, target_value)
        
        self.assertIn(field_name, str(exception))
        self.assertIn(source_value, str(exception))
        self.assertIn(target_value, str(exception))
        self.assertEqual(exception.field_name, field_name)


class TestExceptionUtilities(unittest.TestCase):
    """Test exception utility functions."""
    
    def test_handle_exception_decorator(self):
        """Test the handle_exception decorator."""
        
        @handle_exception
        def function_that_raises_file_not_found():
            raise FileNotFoundError("/path/to/test.pst")
        
        @handle_exception
        def function_that_raises_permission_error():
            raise PermissionError("/path/to/test.pst")
        
        @handle_exception
        def function_that_raises_connection_error():
            raise ConnectionError("Network unreachable")
        
        @handle_exception
        def function_that_works():
            return "success"
        
        # Test PST file not found conversion
        with self.assertRaises(PSTFileNotFoundException):
            function_that_raises_file_not_found()
        
        # Test PST access denied conversion
        with self.assertRaises(PSTAccessDeniedException):
            function_that_raises_permission_error()
        
        # Test connection error conversion
        with self.assertRaises(DynamicsConnectionException):
            function_that_raises_connection_error()
        
        # Test normal function execution
        result = function_that_works()
        self.assertEqual(result, "success")
    
    def test_get_user_friendly_message(self):
        """Test user-friendly message generation."""
        
        # Test PST file not found
        exception = PSTFileNotFoundException("/path/to/missing.pst")
        message = get_user_friendly_message(exception)
        self.assertIn("PST file could not be found", message)
        self.assertIn("/path/to/missing.pst", message)
        
        # Test PST file corrupted
        exception = PSTFileCorruptedException("/path/to/corrupted.pst")
        message = get_user_friendly_message(exception)
        self.assertIn("corrupted", message.lower())
        
        # Test Dynamics authentication
        exception = DynamicsAuthenticationException("user@example.com")
        message = get_user_friendly_message(exception)
        self.assertIn("sign in", message.lower())
        self.assertIn("username and password", message.lower())
        
        # Test Dynamics connection
        exception = DynamicsConnectionException("https://example.com")
        message = get_user_friendly_message(exception)
        self.assertIn("connect", message.lower())
        self.assertIn("internet connection", message.lower())
        
        # Test rate limit
        exception = DynamicsRateLimitException(30)
        message = get_user_friendly_message(exception)
        self.assertIn("too many requests", message.lower())
        self.assertIn("30 seconds", message)
        
        # Test missing configuration
        exception = MissingConfigurationException("USERNAME")
        message = get_user_friendly_message(exception)
        self.assertIn("configuration", message.lower())
        self.assertIn("USERNAME", message)
        
        # Test generic exception
        exception = Exception("Generic error")
        message = get_user_friendly_message(exception)
        self.assertIn("unexpected error", message.lower())
    
    def test_log_exception(self):
        """Test exception logging functionality."""
        import io
        import logging
        
        # Create a logger with a string stream handler
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        
        # Create string stream to capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        # Test logging custom exception
        exception = PSTFileNotFoundException("/test.pst")
        context = {"operation": "file_read", "user": "test_user"}
        
        log_exception(exception, logger, context)
        
        log_output = log_stream.getvalue()
        
        # Check that error code and message are logged
        self.assertIn("PST_FILE_NOT_FOUND", log_output)
        self.assertIn("/test.pst", log_output)
        self.assertIn("test_user", log_output)
        
        # Clean up
        logger.removeHandler(handler)


class TestExceptionIntegration(unittest.TestCase):
    """Test exception handling in integration scenarios."""
    
    def test_exception_chaining(self):
        """Test that exceptions can be properly chained and traced."""
        
        def inner_function():
            raise ValueError("Inner error")
        
        def middle_function():
            try:
                inner_function()
            except ValueError as e:
                raise EmailImportException("test@example.com", "sender@example.com", str(e))
        
        def outer_function():
            try:
                middle_function()
            except EmailImportException as e:
                # Re-raise with additional context
                raise EmailImportException(
                    e.email_subject or "Unknown",
                    e.sender or "Unknown", 
                    f"Outer context: {e.details.get('import_error', str(e))}"
                )
        
        with self.assertRaises(EmailImportException) as context:
            outer_function()
        
        exception = context.exception
        self.assertEqual(exception.sender, "sender@example.com")
        self.assertIn("Inner error", str(exception))
    
    def test_exception_details_preservation(self):
        """Test that exception details are properly preserved."""
        
        original_details = {
            "file_path": "/test.pst",
            "file_size": 1024,
            "corruption_type": "header_invalid"
        }
        
        exception = PSTFileCorruptedException("/test.pst", "Header corruption")
        exception.details.update(original_details)
        
        # Verify details are preserved
        self.assertEqual(exception.details["file_size"], 1024)
        self.assertEqual(exception.details["corruption_type"], "header_invalid")
        self.assertIn("file_path", exception.details)


if __name__ == '__main__':
    unittest.main() 