#!/usr/bin/env python3
"""
PST-to-Dynamics 365 GUI Launcher
================================

Phase 5.1 Foundation Launch Script
Quick launcher for the desktop GUI application.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
        print("✅ PyQt6: Available")
    except ImportError:
        missing_deps.append("PyQt6")
        print("❌ PyQt6: Not available")
    
    try:
        import qtawesome
        print("✅ QtAwesome: Available")
    except ImportError:
        print("⚠️ QtAwesome: Not available (optional)")
    
    try:
        import pyqtgraph
        print("✅ PyQtGraph: Available")
    except ImportError:
        print("⚠️ PyQtGraph: Not available (optional)")
    
    if missing_deps:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install with: pip install PyQt6")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application"""
    print("🚀 Launching PST-to-Dynamics 365 GUI...")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    print("\n📋 Phase 5.1 Foundation Features:")
    print("   ✅ Main window framework")
    print("   ✅ Navigation sidebar")
    print("   ✅ Menu and toolbar system")
    print("   ✅ Status monitoring")
    print("   ✅ Professional styling")
    
    print("\n🎯 Starting application...")
    print("=" * 50)
    
    try:
        # Import and run the GUI
        from gui.main_window import main
        return main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all files are in the correct location.")
        return 1
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(launch_gui()) 