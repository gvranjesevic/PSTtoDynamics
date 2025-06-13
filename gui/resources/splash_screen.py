"""
Splash Screen for PST-to-Dynamics Application
============================================

Professional splash screen shown during application startup.
"""

from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QLinearGradient
from .app_icon import get_app_pixmap


class SplashScreen(QSplashScreen):
    """Professional splash screen with progress indicator."""
    
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        # Create splash pixmap
        pixmap = self._create_splash_pixmap()
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint)
        self.progress = 0
        self.message = "Initializing..."
        
        # Connect progress signal
        self.progress_updated.connect(self._update_progress)
        
        # Auto-close timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.close)
    
    def _create_splash_pixmap(self) -> QPixmap:
        """Create the splash screen pixmap."""
        width, height = 400, 300
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(74, 144, 226))  # Blue
        gradient.setColorAt(1, QColor(35, 122, 189))  # Darker blue
        painter.fillRect(0, 0, width, height, gradient)
        
        # Application icon
        try:
            icon_pixmap = get_app_pixmap(80)
            icon_x = (width - 80) // 2
            icon_y = 50
            painter.drawPixmap(icon_x, icon_y, icon_pixmap)
        except (Exception, AttributeError, TypeError, ValueError):
            # Fallback: draw simple icon
            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(160, 50, 80, 80)
            
            painter.setPen(QColor(74, 144, 226))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(160, 50, 80, 80, Qt.AlignmentFlag.AlignCenter, "PST")
        
        # Application title
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(0, 150, width, 30, Qt.AlignmentFlag.AlignCenter, "PST to Dynamics 365")
        
        # Subtitle
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(0, 180, width, 20, Qt.AlignmentFlag.AlignCenter, "AI-Powered Email Import System")
        
        # Version
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(0, 210, width, 15, Qt.AlignmentFlag.AlignCenter, "Version 1.0.0")
        
        # Progress area (will be updated dynamically)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(20, 250, width-40, 20, Qt.AlignmentFlag.AlignLeft, "Initializing...")
        
        painter.end()
        return pixmap
    
    def _update_progress(self, progress: int, message: str):
        """Update progress and message."""
        self.progress = progress
        self.message = message
        
        # Update the message on the splash screen
        self.showMessage(
            f"{message} ({progress}%)",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
            QColor(255, 255, 255)
        )
    
    def update_progress(self, progress: int, message: str = None):
        """Public method to update progress."""
        if message is None:
            message = self.message
        self.progress_updated.emit(progress, message)
    
    def auto_close(self, delay_ms: int = 2000):
        """Automatically close the splash screen after a delay."""
        self.timer.start(delay_ms)


def show_splash_screen() -> SplashScreen:
    """Show splash screen and return the instance."""
    splash = SplashScreen()
    splash.show()
    return splash 