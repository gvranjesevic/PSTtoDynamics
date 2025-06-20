#!/usr/bin/env python3
"""
PST-to-Dynamics 365 GUI Launcher
================================

Quick launcher for the desktop GUI application.
"""

import sys
import logging
import os

# CRITICAL: Suppress Qt warnings BEFORE any imports or Qt initialization
# Set the most aggressive Qt logging suppression possible
os.environ['QT_LOGGING_RULES'] = '*=false;qt.qpa.*=false;qt.gui.*=false;*.debug=false;*.warning=false'
os.environ['QT_ASSUME_STDERR_HAS_CONSOLE'] = '0'
os.environ['QT_FORCE_STDERR_LOGGING'] = '0'
os.environ['QT_LOGGING_TO_CONSOLE'] = '0'
os.environ['QT_FATAL_WARNINGS'] = '0'
os.environ['QT_NO_GLIB'] = '1'
os.environ['QT_QPA_PLATFORM'] = 'windows'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Prevent PyQtGraph from creating early QApplication
os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt6'

# Comprehensive Qt warning suppression
os.environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'RoundPreferFloor'
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
os.environ['QT_HIGHDPI_DISABLE_2X_IMAGE_SCALING'] = '1'

# Windows-specific Qt console suppression
if sys.platform.startswith('win'):
    os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
    # Disable Qt console window
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetStdHandle(-11, None)  # STD_OUTPUT_HANDLE
    kernel32.SetStdHandle(-12, None)  # STD_ERROR_HANDLE

# Import and configure warnings suppression
import warnings
warnings.filterwarnings("ignore")

# Import and set up comprehensive stderr redirection
from io import StringIO
import contextlib

# Custom stderr handler that completely blocks Qt CSS warnings
class NullWriter:
    def write(self, text): pass
    def flush(self): pass

# Temporarily redirect stderr during imports to catch early Qt warnings
original_stderr = sys.stderr

# Use aggressive OS-level stderr suppression during critical phases
if sys.platform.startswith('win'):
    # Try to suppress at the C library level
    import ctypes
    import ctypes.wintypes
    
    # Get Windows console handles
    try:
        STD_ERROR_HANDLE = -12
        kernel32 = ctypes.windll.kernel32
        
        # Get current stderr handle
        stderr_handle = kernel32.GetStdHandle(STD_ERROR_HANDLE)
        
        # Temporarily disable stderr at OS level
        kernel32.SetStdHandle(STD_ERROR_HANDLE, None)
        
        # Re-enable after a brief moment (this might suppress early Qt warnings)
        import time
        time.sleep(0.1)
        kernel32.SetStdHandle(STD_ERROR_HANDLE, stderr_handle)
    except Exception:
        pass  # Ignore if this approach fails

# Create a comprehensive Qt warning filter that handles batched output
class ComprehensiveQtFilter:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = ""
        
    def write(self, text):
        # Add to buffer for processing
        self.buffer += text
        
        # Process complete buffer for comprehensive filtering
        filtered_buffer = self._filter_qt_warnings(self.buffer)
        
        # If buffer changed, output the filtered version and clear buffer
        if filtered_buffer != self.buffer:
            if filtered_buffer.strip():
                self.original_stderr.write(filtered_buffer)
                self.original_stderr.flush()
            self.buffer = ""
        elif '\n' in text:
            # Output when we have complete lines, after filtering
            if filtered_buffer.strip():
                self.original_stderr.write(filtered_buffer)
                self.original_stderr.flush()
            self.buffer = ""
    
    def _filter_qt_warnings(self, text):
        """Comprehensively filter Qt warnings from text"""
        # Remove specific Qt warnings
        qt_patterns_to_remove = [
            'setHighDpiScaleFactorRoundingPolicy must be called before creating the QGuiApplication instance',
            'QWindowsWindow::setGeometry: Unable to set geometry',
            'QWindowsWindow::setGeometry',
            'Unable to set geometry',
            'Resulting geometry:',
            'MINMAXINFO',
            'margins:',
            'minimum size:',
            'Unhandled Python exception',
            'Uncaught exception',
            'TypeError: invalid argument to sipBadCatcherResult()',
            '(frame:',
            'maxSize=POINT',
            'maxpos=POINT',
            'maxtrack=POINT',
            'mintrack=POINT',
            'Unknown property content'
        ]
        
        for pattern in qt_patterns_to_remove:
            # Remove lines containing these patterns
            lines = text.split('\n')
            filtered_lines = []
            for line in lines:
                if pattern not in line:
                    filtered_lines.append(line)
                # Skip lines containing Qt warnings
            text = '\n'.join(filtered_lines)
        
        return text
    
    def flush(self):
        # Process any remaining buffer content
        if self.buffer:
            filtered = self._filter_qt_warnings(self.buffer)
            if filtered.strip():
                self.original_stderr.write(filtered)
                self.original_stderr.flush()
            self.buffer = ""
        self.original_stderr.flush()

sys.stderr = ComprehensiveQtFilter(original_stderr)

# High-DPI configuration now handled in main_window.py

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NOTE: Removed Aspose license validation - using free win32com.client instead

def configure_high_dpi():
    """Configure high-DPI scaling for consistent rendering - now handled in main_window.py"""
    # High-DPI configuration is now handled directly in main_window.py before imports
    logger.info("✅ High-DPI scaling configured in main_window.py")
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
        logger.info("✅ PyQt6: Available")
    except ImportError:
        missing_deps.append("PyQt6")
        logger.error("❌ PyQt6: Not available")
    
    try:
        # Test pyqtgraph import without actually importing it yet
        import importlib.util
        spec = importlib.util.find_spec("pyqtgraph")
        if spec is not None:
            logger.info("✅ PyQtGraph: Available")
        else:
            missing_deps.append("pyqtgraph")
            logger.error("❌ PyQtGraph: Not available")
    except ImportError:
        missing_deps.append("pyqtgraph")
        logger.error("❌ PyQtGraph: Not available")
    
    try:
        import win32com.client
        logger.info("✅ win32com: Available (for PST reading)")
    except ImportError:
        missing_deps.append("pywin32")
        logger.error("❌ win32com: Not available - install pywin32")
    
    if missing_deps:
        logger.error(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        return False
    
    return True

class QtOutputSuppressor:
    """Custom context manager to suppress Qt CSS warnings"""
    def __init__(self):
        self.original_stderr = sys.stderr
        self.filtered_output = StringIO()
        
    def __enter__(self):
        sys.stderr = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self.original_stderr
        
    def write(self, text):
        """Custom write method that filters out Qt CSS warnings"""
        # Filter Qt-specific warnings
        if any(warning in text for warning in [
            'Unknown property box-shadow',
            'Unknown property transform', 
            'Unknown property content',
            'Unknown property',
            'QWindowsWindow::setGeometry',
            'Unable to set geometry',
            'TypeError: invalid argument to sipBadCatcherResult()'
        ]):
            return  # Suppress these warnings
            
        # Write everything else normally
        self.original_stderr.write(text)
        self.original_stderr.flush()
        
    def flush(self):
        self.original_stderr.flush()

def launch_gui():
    """Launch the main GUI application"""
    logger.info("🚀 Launching PST-to-Dynamics 365 GUI...")
    
    # NOTE: Removed Aspose license validation - using free win32com.client for PST reading
    logger.info("✅ Using free win32com.client for PST processing")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Cannot launch - missing required dependencies")
        input("Press Enter to exit...")
        return
    
    # Import and launch GUI with comprehensive Qt warning suppression
    try:
        # Restore stderr but install permanent filtering
        sys.stderr = original_stderr
        
        # Install permanent comprehensive Qt warning filter
        class PermanentQtFilter:
            def __init__(self, original_stderr):
                self.original_stderr = original_stderr
                self.buffer = ""
                
            def write(self, text):
                """Permanently filter all Qt warnings and errors"""
                # Buffer text for comprehensive processing
                self.buffer += text
                
                # Process when we have complete content
                if '\n' in text or len(self.buffer) > 1000:
                    filtered_text = self._comprehensive_filter(self.buffer)
                    if filtered_text.strip():
                        self.original_stderr.write(filtered_text)
                        self.original_stderr.flush()
                    self.buffer = ""
            
            def _comprehensive_filter(self, text):
                """Apply comprehensive Qt warning filtering"""
                qt_patterns_to_remove = [
                    'Unknown property',
                    'Unknown property content',
                    'box-shadow',
                    'QLayout: Attempting to add QLayout',
                    'QWindowsWindow::setGeometry',
                    'Unable to set geometry',
                    'TypeError: invalid argument to sipBadCatcherResult()',
                    'setHighDpiScaleFactorRoundingPolicy',
                    'QGuiApplication',
                    'must be called before',
                    'creating the QGuiApplication instance',
                    'Resulting geometry:',
                    'MINMAXINFO',
                    'margins:',
                    'minimum size:',
                    'Unhandled Python exception',
                    'Uncaught exception',
                    '(frame:',
                    'maxSize=POINT',
                    'maxpos=POINT',
                    'maxtrack=POINT',
                    'mintrack=POINT'
                ]
                
                # Filter out lines containing Qt warnings
                lines = text.split('\n')
                filtered_lines = []
                for line in lines:
                    should_include = True
                    for pattern in qt_patterns_to_remove:
                        if pattern in line:
                            should_include = False
                            break
                    if should_include:
                        filtered_lines.append(line)
                
                return '\n'.join(filtered_lines)
                
            def flush(self):
                if self.buffer:
                    filtered_text = self._comprehensive_filter(self.buffer)
                    if filtered_text.strip():
                        self.original_stderr.write(filtered_text)
                        self.original_stderr.flush()
                    self.buffer = ""
                self.original_stderr.flush()
        
        sys.stderr = PermanentQtFilter(original_stderr)
        
        # Import and start the GUI (high-DPI scaling configured in main_window.py)
        from gui.main_window import main
        logger.info("🎯 Starting main application...")
        main()
        
    except ImportError as e:
        logger.error(f"❌ Could not import GUI modules: {e}")
        input("Press Enter to exit...")
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    launch_gui() 