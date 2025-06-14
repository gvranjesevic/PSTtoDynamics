#!/usr/bin/env python3
"""
PST-to-Dynamics 365 GUI Launcher
================================

Quick launcher for the desktop GUI application.
"""

import sys
import logging
import os

# Suppress Qt warnings IMMEDIATELY before any other imports
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.stylesheet.parser.warning=false;qt.qpa.window.warning=false;qt.qpa.windows.warning=false;qt.qpa.windows.debug=false;qt.qpa.windows.info=false;qt.qpa.gl.warning=false;qt.qpa.xcb.warning=false;qt.qpa.screen.warning=false;qt.qpa.fonts.warning=false;qt.qpa.platform.warning=false;qt.qpa.platform.debug=false'
os.environ['QT_ASSUME_STDERR_HAS_CONSOLE'] = '1'
os.environ['QT_FORCE_STDERR_LOGGING'] = '0'

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NOTE: Removed Aspose license validation - using free win32com.client instead

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
        import pyqtgraph
        logger.info("✅ PyQtGraph: Available")
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

def launch_gui():
    """Launch the main GUI application"""
    logger.info("🚀 Launching PST-to-Dynamics 365 GUI...")
    
    # Qt warnings already suppressed at module level
    
    # NOTE: Removed Aspose license validation - using free win32com.client for PST reading
    logger.info("✅ Using free win32com.client for PST processing")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Cannot launch - missing required dependencies")
        input("Press Enter to exit...")
        return
    
    # Import and launch GUI
    try:
        # Additional Qt warning suppression right before GUI import
        import sys
        from io import StringIO
        
        # Temporarily redirect stderr to capture and filter Qt warnings
        original_stderr = sys.stderr
        filtered_stderr = StringIO()
        
        def filter_qt_warnings(text):
            """Filter out Qt geometry warnings"""
            if 'QWindowsWindow::setGeometry' in text:
                return  # Suppress this warning
            if 'Unable to set geometry' in text:
                return  # Suppress this warning
            original_stderr.write(text)
            original_stderr.flush()
        
        # Custom stderr that filters Qt warnings
        class FilteredStderr:
            def write(self, text):
                filter_qt_warnings(text)
            def flush(self):
                original_stderr.flush()
        
        sys.stderr = FilteredStderr()
        
        from gui.main_window import main
        logger.info("🎯 Starting main application...")
        main()
        
        # Restore original stderr
        sys.stderr = original_stderr
        
    except ImportError as e:
        logger.error(f"❌ Could not import GUI modules: {e}")
        input("Press Enter to exit...")
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    launch_gui() 