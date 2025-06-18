#!/usr/bin/env python3
"""
Test Enhanced Authentication Widget
==================================
Demonstrates the improved Dynamics 365 authentication widget with:
- Comprehensive step-by-step instructions
- Help buttons for each field
- User-friendly guidance for finding authentication data
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.widgets.configuration_manager import DynamicsAuthWidget


class AuthWidgetTestWindow(QMainWindow):
    """Test window for the enhanced authentication widget"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Dynamics 365 Authentication Widget Test")
        self.setGeometry(100, 100, 900, 800)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the test interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Test title
        title = QLabel("Enhanced Dynamics 365 Authentication Widget")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "This enhanced widget now includes:\n"
            "• Comprehensive step-by-step instructions for finding authentication data\n"
            "• Help buttons (?) next to each field with specific guidance\n"
            "• Clickable links to Azure Portal and Power Platform Admin Center\n"
            "• Tooltips and detailed help dialogs\n\n"
            "Perfect for users who are not familiar with Azure or Dynamics 365 administration!"
        )
        description.setFont(QFont("Segoe UI", 11))
        description.setStyleSheet("""
            color: #34495e; 
            background-color: #ecf0f1; 
            padding: 15px; 
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Authentication widget
        auth_widget = DynamicsAuthWidget()
        layout.addWidget(auth_widget, 1)  # Takes remaining space
        
        # Instructions
        instructions = QLabel(
            "💡 Try clicking the blue '?' buttons next to each field for specific help!"
        )
        instructions.setFont(QFont("Segoe UI", 10))
        instructions.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)


def main():
    """Run the authentication widget test"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Auth Widget Test")
    app.setApplicationVersion("1.0")
    
    window = AuthWidgetTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 