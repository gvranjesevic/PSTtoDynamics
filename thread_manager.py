"""
Thread Manager
==============

Manages QThread lifecycle to prevent memory leaks and ensure proper cleanup.
"""

import logging
from typing import List, Optional
from PyQt6.QtCore import QThread, QObject, pyqtSignal
import weakref
import atexit

logger = logging.getLogger(__name__)


class ThreadManager(QObject):
    """Manages QThread instances and ensures proper cleanup."""
    
    # Signal emitted when all threads are cleaned up
    all_threads_cleaned = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._threads: List[weakref.ref] = []
        self._cleanup_timeout = 5000  # 5 seconds
        self._cleanup_registered = False
        
        # Register cleanup on exit (only once)
        if not self._cleanup_registered:
            atexit.register(self._safe_cleanup_all_threads)
            self._cleanup_registered = True
    
    def register_thread(self, thread: QThread) -> None:
        """
        Register a thread for management.
        
        Args:
            thread: QThread instance to manage
        """
        if not isinstance(thread, QThread):
            raise TypeError("Only QThread instances can be registered")
        
        # Use weak reference to avoid circular references
        weak_ref = weakref.ref(thread, self._thread_cleanup_callback)
        self._threads.append(weak_ref)
        
        logger.debug(f"Registered thread: {thread.__class__.__name__}")
    
    def _thread_cleanup_callback(self, weak_ref):
        """Callback when a thread is garbage collected."""
        if weak_ref in self._threads:
            self._threads.remove(weak_ref)
            logger.debug("Thread garbage collected and removed from registry")
    
    def cleanup_thread(self, thread: QThread, timeout: Optional[int] = None) -> bool:
        """
        Safely cleanup a single thread.
        
        Args:
            thread: Thread to cleanup
            timeout: Timeout in milliseconds (default: 5000)
            
        Returns:
            True if cleanup successful, False otherwise
        """
        if not thread or not thread.isRunning():
            return True
        
        timeout = timeout or self._cleanup_timeout
        
        try:
            logger.debug(f"Cleaning up thread: {thread.__class__.__name__}")
            
            # Request thread to quit
            thread.quit()
            
            # Wait for thread to finish
            if thread.wait(timeout):
                logger.debug(f"Thread {thread.__class__.__name__} cleaned up successfully")
                return True
            else:
                logger.warning(f"Thread {thread.__class__.__name__} did not quit within {timeout}ms")
                
                # Force terminate if it doesn't quit gracefully
                thread.terminate()
                if thread.wait(1000):  # Give 1 second for termination
                    logger.warning(f"Thread {thread.__class__.__name__} forcefully terminated")
                    return True
                else:
                    logger.error(f"Failed to terminate thread {thread.__class__.__name__}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error cleaning up thread {thread.__class__.__name__}: {e}")
            return False
    
    def cleanup_all_threads(self, timeout: Optional[int] = None) -> bool:
        """
        Cleanup all registered threads.
        
        Args:
            timeout: Timeout in milliseconds for each thread
            
        Returns:
            True if all threads cleaned up successfully
        """
        if not self._threads:
            logger.debug("No threads to cleanup")
            self.all_threads_cleaned.emit()
            return True
        
        logger.info(f"Cleaning up {len(self._threads)} registered threads...")
        
        success_count = 0
        total_threads = len(self._threads)
        
        # Create a copy of the list since it may be modified during iteration
        threads_to_cleanup = []
        for weak_ref in self._threads[:]:
            thread = weak_ref()
            if thread is not None:
                threads_to_cleanup.append(thread)
        
        for thread in threads_to_cleanup:
            if self.cleanup_thread(thread, timeout):
                success_count += 1
        
        # Clear the registry
        self._threads.clear()
        
        success = success_count == len(threads_to_cleanup)
        if success:
            logger.info("✅ All threads cleaned up successfully")
        else:
            logger.warning(f"⚠️ {len(threads_to_cleanup) - success_count} threads failed to cleanup")
        
        # Safely emit signal only if Qt objects are still valid
        try:
            if hasattr(self, 'all_threads_cleaned'):
                self.all_threads_cleaned.emit()
        except (RuntimeError, AttributeError):
            # Qt objects have been destroyed, ignore the signal emission
            logger.debug("🔧 Qt objects destroyed, skipping signal emission")
        
        return success
    
    def _safe_cleanup_all_threads(self):
        """Safe cleanup for atexit - doesn't emit signals"""
        if not self._threads:
            return
        
        try:
            logger.debug("🧹 Safe cleanup of threads during exit...")
            
            # Create a copy of the list since it may be modified during iteration
            threads_to_cleanup = []
            for weak_ref in self._threads[:]:
                thread = weak_ref()
                if thread is not None:
                    threads_to_cleanup.append(thread)
            
            for thread in threads_to_cleanup:
                try:
                    if thread.isRunning():
                        thread.quit()
                        thread.wait(1000)  # Short timeout during exit
                except (RuntimeError, AttributeError):
                    # Qt objects may be destroyed, ignore
                    pass
            
            # Clear the registry
            self._threads.clear()
            logger.debug("🧹 Safe thread cleanup completed")
            
        except Exception as e:
            # Ignore all errors during exit cleanup
            pass
    
    def get_active_threads(self) -> List[QThread]:
        """
        Get list of currently active threads.
        
        Returns:
            List of active QThread instances
        """
        active_threads = []
        for weak_ref in self._threads[:]:
            thread = weak_ref()
            if thread is not None and thread.isRunning():
                active_threads.append(thread)
        
        return active_threads
    
    def get_thread_count(self) -> int:
        """
        Get count of registered threads.
        
        Returns:
            Number of registered threads
        """
        # Clean up dead references
        self._threads = [ref for ref in self._threads if ref() is not None]
        return len(self._threads)


class ManagedThread(QThread):
    """
    QThread subclass that automatically registers with ThreadManager.
    """
    
    def __init__(self, parent=None, auto_register=True):
        super().__init__(parent)
        
        if auto_register:
            thread_manager.register_thread(self)
    
    def cleanup(self) -> bool:
        """
        Cleanup this thread.
        
        Returns:
            True if cleanup successful
        """
        return thread_manager.cleanup_thread(self)


# Global thread manager instance (singleton)
_thread_manager_instance = None

def get_thread_manager():
    """Get the global thread manager instance (singleton pattern)"""
    global _thread_manager_instance
    if _thread_manager_instance is None:
        _thread_manager_instance = ThreadManager()
    return _thread_manager_instance

thread_manager = get_thread_manager()


def register_thread(thread: QThread) -> None:
    """
    Register a thread with the global thread manager.
    
    Args:
        thread: QThread to register
    """
    thread_manager.register_thread(thread)


def cleanup_all_threads(timeout: Optional[int] = None) -> bool:
    """
    Cleanup all registered threads.
    
    Args:
        timeout: Timeout in milliseconds for each thread
        
    Returns:
        True if all threads cleaned up successfully
    """
    return thread_manager.cleanup_all_threads(timeout)


def get_active_thread_count() -> int:
    """
    Get count of active threads.
    
    Returns:
        Number of active threads
    """
    return len(thread_manager.get_active_threads())


if __name__ == "__main__":
    # Test thread management
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    
    app = QApplication(sys.argv)
    
    class TestThread(ManagedThread):
        def run(self):
            self.msleep(2000)  # Sleep for 2 seconds
            print("Test thread finished")
    
    # Create and start test threads
    threads = []
    for i in range(3):
        thread = TestThread()
        thread.start()
        threads.append(thread)
        print(f"Started test thread {i+1}")
    
    # Setup cleanup after 1 second
    def test_cleanup():
        print(f"Active threads before cleanup: {get_active_thread_count()}")
        success = cleanup_all_threads()
        print(f"Cleanup successful: {success}")
        app.quit()
    
    QTimer.singleShot(1000, test_cleanup)
    
    sys.exit(app.exec()) 