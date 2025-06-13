"""
Comprehensive Logging Configuration System
==========================================

This module provides a centralized logging configuration for the PST-to-Dynamics
application with multiple output formats, log rotation, and performance monitoring.

Features:
- Multiple log levels and handlers
- File rotation and compression
- Real-time log streaming for GUI
- Performance metrics logging
- Error aggregation and alerting
- Structured logging for analytics

Author: AI Assistant
Version: 1.0
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
from queue import Queue, Empty
import traceback


class PerformanceFilter(logging.Filter):
    """Filter to capture performance-related log entries."""
    
    def filter(self, record):
        # Add performance metrics to log records
        if hasattr(record, 'duration'):
            record.performance_data = {
                'duration_ms': getattr(record, 'duration', 0) * 1000,
                'operation': getattr(record, 'operation', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
        return True


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add performance data if present
        if hasattr(record, 'performance_data'):
            log_data['performance'] = record.performance_data
        
        # Add custom fields
        for key, value in record.__dict__.items():
            if key.startswith('custom_'):
                log_data[key[7:]] = value  # Remove 'custom_' prefix
        
        return json.dumps(log_data, ensure_ascii=False)


class GuiLogHandler(logging.Handler):
    """Custom handler for sending logs to GUI components."""
    
    def __init__(self):
        super().__init__()
        self.log_queue = Queue()
        self.gui_callbacks: List[callable] = []
    
    def emit(self, record):
        """Emit a log record to the GUI queue."""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'formatted': self.format(record)
            }
            
            self.log_queue.put(log_entry)
            
            # Notify GUI callbacks
            for callback in self.gui_callbacks:
                try:
                    callback(log_entry)
                except Exception:
                    pass  # Don't let GUI errors break logging
                    
        except Exception:
            self.handleError(record)
    
    def add_gui_callback(self, callback: callable):
        """Add a callback for GUI log updates."""
        self.gui_callbacks.append(callback)
    
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries for GUI display."""
        logs = []
        try:
            while len(logs) < count:
                log_entry = self.log_queue.get_nowait()
                logs.append(log_entry)
        except Empty:
            pass
        return logs[-count:]  # Return most recent entries


class LoggingManager:
    """
    Centralized logging manager for the entire application.
    
    This class provides comprehensive logging capabilities including:
    - Multiple output formats (text, JSON, GUI)
    - Automatic log rotation and compression
    - Performance monitoring integration
    - Error aggregation and alerting
    - Real-time log streaming for monitoring
    """
    
    def __init__(self, log_dir: str = "logs", app_name: str = "PST-to-Dynamics"):
        """
        Initialize the logging manager.
        
        Args:
            log_dir: Directory for log files
            app_name: Application name for log identification
        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.gui_handler = None
        self.performance_logger = None
        self.error_count = 0
        self.warning_count = 0
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize logging configuration
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration."""
        
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Console Handler (for development and immediate feedback)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # Main Application Log (rotating file)
        app_log_file = self.log_dir / f"{self.app_name.lower().replace(' ', '_')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
        
        # Error Log (separate file for errors only)
        error_log_file = self.log_dir / f"{self.app_name.lower().replace(' ', '_')}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        root_logger.addHandler(error_handler)
        
        # Performance Log (JSON format for analytics)
        performance_log_file = self.log_dir / f"{self.app_name.lower().replace(' ', '_')}_performance.json"
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.addFilter(PerformanceFilter())
        performance_handler.setFormatter(JsonFormatter())
        
        # Create performance logger
        self.performance_logger = logging.getLogger('performance')
        self.performance_logger.addHandler(performance_handler)
        self.performance_logger.setLevel(logging.INFO)
        
        # GUI Handler (for real-time display)
        self.gui_handler = GuiLogHandler()
        self.gui_handler.setLevel(logging.INFO)
        gui_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.gui_handler.setFormatter(gui_format)
        root_logger.addHandler(self.gui_handler)
        
        # Setup module-specific loggers
        self._setup_module_loggers()
        
        print(f"🔧 Logging system initialized")
        print(f"   📁 Log directory: {self.log_dir.absolute()}")
        print(f"   📝 Main log: {app_log_file}")
        print(f"   ❌ Error log: {error_log_file}")
        print(f"   📊 Performance log: {performance_log_file}")
    
    def _setup_module_loggers(self):
        """Setup loggers for specific modules with appropriate levels."""
        
        module_configs = {
            'sync_engine': logging.INFO,
            'email_importer': logging.INFO,
            'contact_manager': logging.INFO,
            'auth': logging.WARNING,  # Reduce noise from auth
            'gui': logging.INFO,
            'database': logging.WARNING,
            'exceptions': logging.ERROR,
            'performance': logging.INFO
        }
        
        for module_name, level in module_configs.items():
            logger = logging.getLogger(module_name)
            logger.setLevel(level)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        Log performance metrics for operations.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional performance data
        """
        extra_data = {
            'operation': operation,
            'duration': duration,
            **{f'custom_{k}': v for k, v in kwargs.items()}
        }
        
        self.performance_logger.info(
            f"Performance: {operation} completed in {duration:.3f}s",
            extra=extra_data
        )
    
    def log_error_with_context(self, logger: logging.Logger, error: Exception, 
                              context: Dict[str, Any] = None):
        """
        Log an error with additional context information.
        
        Args:
            logger: Logger instance to use
            error: Exception that occurred
            context: Additional context data
        """
        self.error_count += 1
        
        context = context or {}
        extra_data = {f'custom_{k}': v for k, v in context.items()}
        
        logger.error(
            f"Error occurred: {str(error)}",
            exc_info=True,
            extra=extra_data
        )
    
    def log_warning_with_context(self, logger: logging.Logger, message: str,
                                context: Dict[str, Any] = None):
        """
        Log a warning with additional context information.
        
        Args:
            logger: Logger instance to use
            message: Warning message
            context: Additional context data
        """
        self.warning_count += 1
        
        context = context or {}
        extra_data = {f'custom_{k}': v for k, v in context.items()}
        
        logger.warning(message, extra=extra_data)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get logging statistics for monitoring.
        
        Returns:
            Dictionary with logging statistics
        """
        return {
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'log_directory': str(self.log_dir.absolute()),
            'log_files': [f.name for f in self.log_dir.glob('*.log')],
            'total_log_size_mb': sum(f.stat().st_size for f in self.log_dir.glob('*')) / (1024 * 1024)
        }
    
    def add_gui_log_callback(self, callback: callable):
        """
        Add a callback for GUI log updates.
        
        Args:
            callback: Function to call with log entries
        """
        if self.gui_handler:
            self.gui_handler.add_gui_callback(callback)
    
    def get_recent_gui_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent log entries for GUI display.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            List of log entries
        """
        if self.gui_handler:
            return self.gui_handler.get_recent_logs(count)
        return []
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files to manage disk space.
        
        Args:
            days_to_keep: Number of days of logs to retain
        """
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        removed_count = 0
        for log_file in self.log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    removed_count += 1
                except OSError:
                    pass  # File might be in use
        
        print(f"🧹 Cleaned up {removed_count} old log files")


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager() -> LoggingManager:
    """
    Get the global logging manager instance.
    
    Returns:
        LoggingManager instance
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return get_logging_manager().get_logger(name)


def log_performance(operation: str, duration: float, **kwargs):
    """
    Convenience function to log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional performance data
    """
    get_logging_manager().log_performance(operation, duration, **kwargs)


def performance_timer(operation_name: str):
    """
    Decorator for automatic performance logging.
    
    Args:
        operation_name: Name of the operation to log
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(operation_name, duration, 
                              function=func.__name__, 
                              success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_performance(operation_name, duration,
                              function=func.__name__,
                              success=False,
                              error=str(e))
                raise
        return wrapper
    return decorator


# Initialize logging on module import
if __name__ != "__main__":
    import time
    # Only initialize if not running as main script
    try:
        get_logging_manager()
    except Exception as e:
        print(f"⚠️ Failed to initialize logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ) 