"""
Windows Overlay Manager
======================

Handles Windows system overlays like Voice Access, ensuring the application
interface is not obscured by system UI elements.

Features:
- Voice Access detection and avoidance
- Dynamic window positioning
- Screen boundary detection
- Multi-monitor support
"""

import logging
import sys
from typing import Tuple, Optional
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QScreen

logger = logging.getLogger(__name__)

class WindowsOverlayManager:
    """Manager for handling Windows system overlays"""
    
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.voice_access_height = 60  # Typical Voice Access overlay height
        self.safe_margin = 20  # Additional safety margin
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_overlay_conflicts)
        
    def setup_overlay_avoidance(self):
        """Setup overlay avoidance for the main window"""
        try:
            logger.info("🔧 Setting up Windows overlay avoidance...")
            
            # Get screen information
            screen = self.get_primary_screen()
            if not screen:
                logger.warning("⚠️ Could not get screen information")
                return False
            
            # Calculate safe window positioning
            safe_geometry = self.calculate_safe_geometry(screen)
            
            # Apply safe positioning
            self.apply_safe_positioning(safe_geometry)
            
            # Start monitoring for overlay conflicts
            self.start_overlay_monitoring()
            
            logger.info("✅ Windows overlay avoidance configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up overlay avoidance: {e}")
            return False
    
    def get_primary_screen(self) -> Optional[QScreen]:
        """Get the primary screen information"""
        try:
            app = QApplication.instance()
            if app:
                return app.primaryScreen()
            return None
        except Exception as e:
            logger.error(f"❌ Error getting primary screen: {e}")
            return None
    
    def calculate_safe_geometry(self, screen: QScreen) -> QRect:
        """Calculate safe window geometry avoiding overlays"""
        try:
            # Get available screen geometry
            available_rect = screen.availableGeometry()
            
            # Calculate safe positioning
            # Voice Access typically appears at the top of the screen
            safe_top = available_rect.top() + self.voice_access_height + self.safe_margin
            safe_left = available_rect.left() + self.safe_margin
            
            # Calculate safe dimensions
            safe_width = min(1400, available_rect.width() - (self.safe_margin * 2))
            safe_height = min(900, available_rect.height() - self.voice_access_height - (self.safe_margin * 2))
            
            # Ensure minimum window size
            safe_width = max(safe_width, 1200)
            safe_height = max(safe_height, 800)
            
            # Adjust if window would be too large for screen
            if safe_left + safe_width > available_rect.right():
                safe_width = available_rect.right() - safe_left - self.safe_margin
            
            if safe_top + safe_height > available_rect.bottom():
                safe_height = available_rect.bottom() - safe_top - self.safe_margin
            
            return QRect(safe_left, safe_top, safe_width, safe_height)
            
        except Exception as e:
            logger.error(f"❌ Error calculating safe geometry: {e}")
            # Return fallback geometry
            return QRect(100, 120, 1200, 800)
    
    def apply_safe_positioning(self, safe_geometry: QRect):
        """Apply safe positioning to the main window"""
        try:
            # Set window geometry
            self.main_window.setGeometry(safe_geometry)
            
            # Set minimum size to prevent shrinking below usable size
            self.main_window.setMinimumSize(1200, 800)
            
            # Ensure window is visible and properly positioned
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            logger.info(f"✅ Window positioned safely at {safe_geometry.x()}, {safe_geometry.y()} "
                       f"with size {safe_geometry.width()}x{safe_geometry.height()}")
            
        except Exception as e:
            logger.error(f"❌ Error applying safe positioning: {e}")
    
    def start_overlay_monitoring(self):
        """Start monitoring for overlay conflicts"""
        try:
            # Check every 5 seconds for overlay conflicts (only for non-maximized windows)
            self.check_timer.start(5000)
            logger.info("🔍 Started overlay conflict monitoring")
        except Exception as e:
            logger.error(f"❌ Error starting overlay monitoring: {e}")
    
    def pause_monitoring(self):
        """Pause monitoring (for when window is maximized)"""
        try:
            if self.check_timer.isActive():
                self.check_timer.stop()
                logger.info("⏸️ Paused overlay monitoring (window maximized)")
        except Exception as e:
            logger.error(f"❌ Error pausing monitoring: {e}")
    
    def resume_monitoring(self):
        """Resume monitoring (when window is restored from maximized)"""
        try:
            if not self.check_timer.isActive():
                self.check_timer.start(5000)
                logger.info("▶️ Resumed overlay monitoring (window restored)")
        except Exception as e:
            logger.error(f"❌ Error resuming monitoring: {e}")
    
    def stop_overlay_monitoring(self):
        """Stop overlay monitoring"""
        try:
            self.check_timer.stop()
            logger.info("⏹️ Stopped overlay conflict monitoring")
        except Exception as e:
            logger.error(f"❌ Error stopping overlay monitoring: {e}")
    
    def check_overlay_conflicts(self):
        """Check for overlay conflicts and adjust window position if needed"""
        try:
            # CRITICAL: Skip ALL conflict detection for maximized windows
            # Maximized windows should NEVER be repositioned by this manager
            if self.main_window.isMaximized():
                logger.debug("🔒 Skipping conflict check - window is maximized")
                return
            
            # Double-check window state to prevent race conditions
            if self.main_window.windowState() & Qt.WindowState.WindowMaximized:
                logger.debug("🔒 Skipping conflict check - window state is maximized")
                return
            
            window_rect = self.main_window.geometry()
            screen = self.get_primary_screen()
            
            if not screen:
                return
            
            available_rect = screen.availableGeometry()
            
            # Check if window is in the Voice Access danger zone (only for non-maximized windows)
            voice_access_zone = available_rect.top() + self.voice_access_height
            
            if window_rect.top() < voice_access_zone:
                # Final safety check - NEVER move maximized windows
                if self.main_window.isMaximized():
                    logger.debug("🔒 Preventing move - window is maximized")
                    return
                
                # Window is in overlay zone, move it down
                new_top = voice_access_zone + self.safe_margin
                self.main_window.move(window_rect.left(), new_top)
                
                logger.info("🔧 Window repositioned to avoid Voice Access overlay")
                
                # Show notification to user
                self.show_repositioning_notification()
                
        except Exception as e:
            logger.error(f"❌ Error checking overlay conflicts: {e}")
    
    def show_repositioning_notification(self):
        """Show a brief notification that the window was repositioned"""
        try:
            # Update status bar if main window has one
            if hasattr(self.main_window, 'update_status'):
                # Get theme color dynamically
                try:
                    from gui.themes.theme_manager import get_theme_manager
                    colors = get_theme_manager().get_theme_definition()['colors']
                    brand_primary = colors.get('brand_primary', '#0077B5')
                except Exception:
                    brand_primary = '#0077B5'  # Fallback
                
                self.main_window.update_status(
                    "Window position adjusted to avoid Windows Voice Access overlay", 
                    brand_primary
                )
            
            logger.info("💡 Window repositioning notification shown")
            
        except Exception as e:
            logger.error(f"❌ Error showing repositioning notification: {e}")
    
    def handle_voice_access_detection(self) -> bool:
        """Detect if Windows Voice Access is active"""
        try:
            # Check if Voice Access process is running
            import subprocess
            
            # Use PowerShell to check for Voice Access process
            result = subprocess.run([
                'powershell', '-Command', 
                'Get-Process -Name "VoiceAccess" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                voice_access_active = count > 0
                
                if voice_access_active:
                    logger.info("🎤 Windows Voice Access detected as active")
                else:
                    logger.info("🔇 Windows Voice Access not detected")
                
                return voice_access_active
            else:
                logger.warning("⚠️ Could not check Voice Access status")
                return True  # Assume active for safety
                
        except Exception as e:
            logger.error(f"❌ Error detecting Voice Access: {e}")
            return True  # Assume active for safety
    
    def get_voice_access_dimensions(self) -> Tuple[int, int]:
        """Get Voice Access overlay dimensions"""
        try:
            # Voice Access typically has these dimensions
            # Height: ~60px, Width: ~300px (but can vary)
            return (300, 60)
        except Exception as e:
            logger.error(f"❌ Error getting Voice Access dimensions: {e}")
            return (300, 60)  # Default fallback
    
    def cleanup(self):
        """Clean up the overlay manager"""
        try:
            self.stop_overlay_monitoring()
            logger.info("🧹 Overlay manager cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during overlay manager cleanup: {e}")

def create_overlay_manager(main_window: QMainWindow) -> WindowsOverlayManager:
    """Create and configure an overlay manager for the main window"""
    try:
        manager = WindowsOverlayManager(main_window)
        manager.setup_overlay_avoidance()
        return manager
    except Exception as e:
        logger.error(f"❌ Error creating overlay manager: {e}")
        return None

def apply_overlay_fixes(main_window: QMainWindow) -> bool:
    """Apply overlay fixes to a main window"""
    try:
        logger.info("🔧 Applying Windows overlay fixes...")
        
        # Create overlay manager
        overlay_manager = create_overlay_manager(main_window)
        
        if overlay_manager:
            # Store manager reference in window for cleanup
            main_window.overlay_manager = overlay_manager
            logger.info("✅ Overlay fixes applied successfully")
            return True
        else:
            logger.error("❌ Failed to create overlay manager")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error applying overlay fixes: {e}")
        return False 