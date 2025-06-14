#!/usr/bin/env python3
"""
PST-to-Dynamics 365 GUI Launcher
================================

logger = logging.getLogger(__name__)

Phase 5.1 Foundation Launch Script
Quick launcher for the desktop GUI application.
"""

import sys
import logging
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Aspose license validator
from aspose_license_validator import require_aspose_license

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
        import qtawesome
        logger.info("✅ QtAwesome: Available")
    except ImportError:
        logger.warning("⚠️ QtAwesome: Not available (optional)")
    
    try:
        import pyqtgraph
        logger.info("✅ PyQtGraph: Available")
    except ImportError:
        logger.warning("⚠️ PyQtGraph: Not available (optional)")
    
    if missing_deps:
        logger.debug("\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        logger.debug("Please install with: pip install PyQt6")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application"""
    logger.info("🚀 Launching PST-to-Dynamics 365 GUI...")
    logger.debug("=" * 50)
    
    # Validate Aspose license first (allow evaluation mode for testing)
    try:
        require_aspose_license(allow_evaluation=True)
        logger.info("✅ Aspose.Email license validated")
    except Exception as e:
        logger.error(f"❌ Aspose.Email license validation failed: {e}")
        logger.error("Please ensure you have a valid Aspose.Email license or are running in evaluation mode")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    logger.debug("\n📋 Phase 5.1 Foundation Features:")
    logger.debug("   ✅ Main window framework")
    logger.debug("   ✅ Navigation sidebar")
    logger.debug("   ✅ Menu and toolbar system")
    logger.debug("   ✅ Status monitoring")
    logger.debug("   ✅ Professional styling")
    
    logger.debug("\n🎯 Starting application...")
    logger.debug("=" * 50)
    
    try:
        # Import and run the GUI
        from gui.main_window import main
        return main()
        
    except ImportError as e:
        logger.error("❌ Import error: {e}")
        logger.debug("Please ensure all files are in the correct location.")
        return 1
    except Exception as e:
        logger.error("❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(launch_gui()) 