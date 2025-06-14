"""
Structured Logging Module for PST-to-Dynamics 365
================================================

Provides standardized, structured logging with JSON output, log rotation,
and centralized configuration for the entire application.
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
import traceback
from enum import Enum


class LogLevel(Enum):
    """Standard log levels with numeric values"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs with consistent fields.
    """
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 
                              'exc_text', 'stack_info']:
                    try:
                        # Ensure value is JSON serializable
                        json.dumps(value)
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        extra_fields[key] = str(value)
            
            if extra_fields:
                log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for console output with colors and emojis.
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    # Emojis for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def __init__(self, use_colors: bool = True, use_emojis: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_emojis = use_emojis
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human readability"""
        
        # Get color and emoji for level
        level_name = record.levelname
        color = self.COLORS.get(level_name, '') if self.use_colors else ''
        reset = self.COLORS['RESET'] if self.use_colors else ''
        emoji = self.EMOJIS.get(level_name, '') if self.use_emojis else ''
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build the log message
        parts = []
        if emoji:
            parts.append(emoji)
        
        parts.extend([
            f"{color}{timestamp}{reset}",
            f"{color}[{level_name}]{reset}",
            f"{record.name}:{record.funcName}:{record.lineno}",
            f"{color}{record.getMessage()}{reset}"
        ])
        
        message = " ".join(parts)
        
        # Add exception information if present
        if record.exc_info:
            message += f"\n{color}Exception: {record.exc_info[1]}{reset}"
            if record.levelno >= logging.ERROR:
                message += f"\n{traceback.format_exception(*record.exc_info)[-1].strip()}"
        
        return message


class StructuredLogger:
    """
    Main structured logging class that provides centralized logging configuration.
    """
    
    def __init__(self, 
                 name: str = "pst_dynamics",
                 log_level: Union[str, int] = "INFO",
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_output: bool = True,
                 file_output: bool = True,
                 structured_format: bool = True):
        
        self.name = name
        self.log_level = self._parse_log_level(log_level)
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_output = console_output
        self.file_output = file_output
        self.structured_format = structured_format
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _parse_log_level(self, level: Union[str, int]) -> int:
        """Parse log level from string or int"""
        if isinstance(level, str):
            return getattr(logging, level.upper(), logging.INFO)
        return level
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            if self.structured_format:
                console_formatter = StructuredFormatter()
            else:
                console_formatter = HumanReadableFormatter()
            
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.file_output:
            log_file = self.log_dir / f"{self.name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            
            # Always use structured format for file output
            file_formatter = StructuredFormatter()
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Error file handler (separate file for errors)
        if self.file_output:
            error_log_file = self.log_dir / f"{self.name}_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_formatter = StructuredFormatter()
            error_handler.setFormatter(error_formatter)
            self.logger.addHandler(error_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(f"{self.name}.{name}")
        return self.logger
    
    def log_operation(self, 
                     operation: str, 
                     status: str, 
                     duration: Optional[float] = None,
                     **kwargs):
        """Log an operation with structured data"""
        extra_data = {
            "operation": operation,
            "status": status,
            "operation_type": "business_operation"
        }
        
        if duration is not None:
            extra_data["duration_seconds"] = duration
        
        extra_data.update(kwargs)
        
        level = logging.INFO if status == "success" else logging.ERROR
        self.logger.log(level, f"Operation {operation} {status}", extra=extra_data)
    
    def log_performance(self, 
                       metric_name: str, 
                       value: Union[int, float], 
                       unit: str = "",
                       **kwargs):
        """Log performance metrics"""
        extra_data = {
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "metric_type": "performance"
        }
        extra_data.update(kwargs)
        
        self.logger.info(f"Performance metric: {metric_name} = {value} {unit}", extra=extra_data)
    
    def log_security_event(self, 
                          event_type: str, 
                          severity: str, 
                          description: str,
                          **kwargs):
        """Log security-related events"""
        extra_data = {
            "security_event_type": event_type,
            "security_severity": severity,
            "event_type": "security"
        }
        extra_data.update(kwargs)
        
        level = logging.WARNING if severity == "medium" else logging.ERROR
        self.logger.log(level, f"Security event: {event_type} - {description}", extra=extra_data)
    
    def log_user_action(self, 
                       user_id: str, 
                       action: str, 
                       resource: str,
                       **kwargs):
        """Log user actions for audit trail"""
        extra_data = {
            "user_id": user_id,
            "user_action": action,
            "resource": resource,
            "event_type": "user_action"
        }
        extra_data.update(kwargs)
        
        self.logger.info(f"User {user_id} performed {action} on {resource}", extra=extra_data)


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def setup_logging(config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """
    Setup global structured logging with configuration.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        StructuredLogger instance
    """
    global _global_logger
    
    # Default configuration
    default_config = {
        "name": "pst_dynamics",
        "log_level": "INFO",
        "log_dir": "logs",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        "console_output": True,
        "file_output": True,
        "structured_format": False  # Human readable for console by default
    }
    
    # Override with provided config
    if config:
        default_config.update(config)
    
    _global_logger = StructuredLogger(**default_config)
    return _global_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance from the global structured logger.
    
    Args:
        name: Optional logger name suffix
    
    Returns:
        Logger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = setup_logging()
    
    return _global_logger.get_logger(name)


def log_operation(operation: str, status: str, **kwargs):
    """Convenience function for logging operations"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    _global_logger.log_operation(operation, status, **kwargs)


def log_performance(metric_name: str, value: Union[int, float], unit: str = "", **kwargs):
    """Convenience function for logging performance metrics"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    _global_logger.log_performance(metric_name, value, unit, **kwargs)


def log_security_event(event_type: str, severity: str, description: str, **kwargs):
    """Convenience function for logging security events"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    _global_logger.log_security_event(event_type, severity, description, **kwargs)


def log_user_action(user_id: str, action: str, resource: str, **kwargs):
    """Convenience function for logging user actions"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    _global_logger.log_user_action(user_id, action, resource, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logger_config = {
        "log_level": "DEBUG",
        "structured_format": False,  # Human readable for testing
        "console_output": True,
        "file_output": True
    }
    
    structured_logger = setup_logging(logger_config)
    logger = get_logger("test")
    
    # Test different log levels
    logger.debug("Debug message for testing")
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("An error occurred during processing")
    
    # Test structured logging functions
    log_operation("email_import", "success", duration=45.2, email_count=150)
    log_performance("import_speed", 3.33, "emails/second", batch_size=50)
    log_security_event("license_validation", "high", "Aspose license validated successfully")
    log_user_action("admin", "start_import", "pst_file", file_size="2.5GB")
    
    # Test exception logging
    try:
        raise ValueError("Test exception for logging")
    except Exception as e:
        logger.error("Exception occurred during test", exc_info=True)
    
    print("✅ Structured logging test completed. Check logs/ directory for output files.") 