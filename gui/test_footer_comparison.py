#!/usr/bin/env python3
"""
Footer Comparison Test
======================
Side-by-side comparison of Import Wizard vs Configuration Manager footers
to verify both work correctly in maximized windows.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QLabel, QPushButton, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import our widgets
from gui.widgets.import_wizard import ImportWizard
from gui.widgets.configuration_manager import ConfigurationManager


class FooterComparisonWindow(QMainWindow):
    """Main window for comparing footers"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Footer Comparison: Import Wizard vs Configuration Manager")
        self.setGeometry(100, 100, 1600, 900)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the comparison interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Footer Visibility Test: Maximize this window to test both panels")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "INSTRUCTIONS:\n"
            "1. Both panels should show their footers normally\n"
            "2. Click 'Maximize' button or maximize this window\n"
            "3. Both footers should remain visible (Import Wizard = 80px, Config Manager = 80px)\n"
            "4. If both footers stay visible, the fix worked!"
        )
        instructions.setFont(QFont("Segoe UI", 11))
        instructions.setStyleSheet("""
            color: #34495e; 
            background-color: #ecf0f1; 
            padding: 15px; 
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        maximize_btn = QPushButton("🗖 Maximize Window")
        maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        maximize_btn.clicked.connect(self.toggle_maximize)
        
        normal_btn = QPushButton("🗗 Normal Window")
        normal_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        normal_btn.clicked.connect(self.show_normal)
        
        button_layout.addWidget(maximize_btn)
        button_layout.addWidget(normal_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create splitter for side-by-side comparison
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #bdc3c7; width: 3px; }")
        
        # Left side: Import Wizard
        left_container = QFrame()
        left_container.setFrameStyle(QFrame.Shape.Box)
        left_container.setStyleSheet("""
            QFrame {
                border: 2px solid #27ae60;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        left_title = QLabel("✅ Import Wizard (Working)")
        left_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        left_title.setStyleSheet("color: #27ae60; padding: 5px; text-align: center;")
        left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(left_title)
        
        # Import Wizard
        try:
            import_wizard = ImportWizard()
            left_layout.addWidget(import_wizard, 1)
        except Exception as e:
            error_label = QLabel(f"Error loading Import Wizard: {e}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            left_layout.addWidget(error_label)
        
        splitter.addWidget(left_container)
        
        # Right side: Configuration Manager
        right_container = QFrame()
        right_container.setFrameStyle(QFrame.Shape.Box)
        right_container.setStyleSheet("""
            QFrame {
                border: 2px solid #0077B5;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        right_title = QLabel("🔧 Configuration Manager (Fixed)")
        right_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        right_title.setStyleSheet("color: #0077B5; padding: 5px; text-align: center;")
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_title)
        
        # Configuration Manager
        try:
            config_manager = ConfigurationManager()
            right_layout.addWidget(config_manager, 1)
        except Exception as e:
            error_label = QLabel(f"Error loading Configuration Manager: {e}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            right_layout.addWidget(error_label)
        
        splitter.addWidget(right_container)
        
        # Set equal sizes
        splitter.setSizes([800, 800])
        
        layout.addWidget(splitter, 1)
        
        # Status bar
        status = QLabel("Status: Ready for testing. Both footers should remain visible when maximized.")
        status.setStyleSheet("""
            background-color: #f8f9fa; 
            padding: 8px; 
            border-top: 1px solid #dee2e6;
            font-size: 11px;
            color: #6c757d;
        """)
        layout.addWidget(status)
    
    def toggle_maximize(self):
        """Toggle maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def show_normal(self):
        """Show normal window"""
        self.showNormal()


def main():
    """Run the footer comparison test"""
    app = QApplication(sys.argv)
    
    window = FooterComparisonWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 