#!/usr/bin/env python3
"""
LinkedIn Blue Theme Application Script
=====================================

This script applies the LinkedIn Blue theme as the default theme
for the PST-to-Dynamics 365 application.
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def apply_linkedin_theme():
    """Apply LinkedIn Blue theme as the default"""
    try:
        # Import theme manager
        from gui.themes.theme_manager import ThemeManager, ThemeType
        
        # Create theme manager instance
        theme_manager = ThemeManager()
        
        # Set LinkedIn Blue as the default theme
        theme_manager.set_theme(ThemeType.LINKEDIN_BLUE, save_preference=True)
        
        print("✅ LinkedIn Blue theme has been set as the default!")
        print("🎨 Theme features:")
        print("   • LinkedIn signature blue (#0077B5) primary color")
        print("   • Professional light background (#F3F6F8)")
        print("   • Clean white surfaces with subtle borders")
        print("   • Optimized for business applications")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import theme manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error applying theme: {e}")
        return False

def create_linkedin_stylesheet():
    """Create a comprehensive LinkedIn Blue stylesheet"""
    linkedin_css = """
/* LinkedIn Blue Theme - Complete Application Stylesheet */

/* Main Application */
QMainWindow {
    background-color: #F3F6F8;
    color: #000000;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Navigation Sidebar */
QFrame[objectName="NavigationSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #D0D7DE;
    border-radius: 8px;
}

/* Navigation Buttons */
QPushButton {
    background-color: #0077B5;
    color: #FFFFFF;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #004471;
}

QPushButton:pressed {
    background-color: #003A5C;
}

QPushButton:disabled {
    background-color: #CCCCCC;
    color: #999999;
}

/* Secondary Buttons */
QPushButton[class="secondary"] {
    background-color: #FFFFFF;
    color: #0077B5;
    border: 1px solid #0077B5;
}

QPushButton[class="secondary"]:hover {
    background-color: #0077B5;
    color: #FFFFFF;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #D0D7DE;
    border-radius: 4px;
    padding: 8px;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0077B5;
    outline: none;
}

/* Labels */
QLabel {
    color: #000000;
    font-size: 14px;
}

QLabel[class="title"] {
    font-size: 20px;
    font-weight: 600;
    color: #0077B5;
}

QLabel[class="heading"] {
    font-size: 18px;
    font-weight: 500;
    color: #000000;
}

QLabel[class="secondary"] {
    color: #666666;
}

QLabel[class="muted"] {
    color: #999999;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    alternate-background-color: #F9FAFB;
    gridline-color: #E8EBED;
    border: 1px solid #D0D7DE;
    border-radius: 4px;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
    border-bottom: 1px solid #E8EBED;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #F9FAFB;
    color: #000000;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #0077B5;
    font-weight: 500;
}

/* Progress Bars */
QProgressBar {
    background-color: #F9FAFB;
    border: 1px solid #D0D7DE;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0077B5;
    border-radius: 4px;
}

/* Status Bar */
QStatusBar {
    background-color: #FFFFFF;
    color: #666666;
    border-top: 1px solid #D0D7DE;
}

/* Menu Bar */
QMenuBar {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom: 1px solid #D0D7DE;
}

QMenuBar::item {
    padding: 8px 16px;
}

QMenuBar::item:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

/* Tool Bar */
QToolBar {
    background-color: #FFFFFF;
    border: none;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    color: #000000;
    border: none;
    padding: 8px;
    border-radius: 4px;
}

QToolButton:hover {
    background-color: #0077B5;
    color: #FFFFFF;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #F9FAFB;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #666666;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #0077B5;
}

QScrollBar:horizontal {
    background-color: #F9FAFB;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #666666;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #0077B5;
}

/* Combo Boxes */
QComboBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #D0D7DE;
    border-radius: 4px;
    padding: 8px;
}

QComboBox:focus {
    border-color: #0077B5;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666666;
}

/* Tabs */
QTabWidget::pane {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #F9FAFB;
    color: #666666;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QTabBar::tab:hover {
    background-color: #004471;
    color: #FFFFFF;
}

/* Splitter */
QSplitter::handle {
    background-color: #D0D7DE;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #0077B5;
}
"""
    
    # Save stylesheet to file
    try:
        with open('linkedin_blue_theme.css', 'w', encoding='utf-8') as f:
            f.write(linkedin_css)
        print("✅ LinkedIn Blue stylesheet saved to 'linkedin_blue_theme.css'")
        return True
    except Exception as e:
        print(f"❌ Error saving stylesheet: {e}")
        return False

def main():
    """Main function"""
    print("🎨 Applying LinkedIn Blue Theme...")
    
    # Apply the theme
    if apply_linkedin_theme():
        print("✅ Theme application successful!")
    else:
        print("❌ Theme application failed!")
    
    # Create stylesheet file
    if create_linkedin_stylesheet():
        print("✅ Stylesheet creation successful!")
    else:
        print("❌ Stylesheet creation failed!")
    
    print("🚀 LinkedIn Blue theme is now ready!")
    print("   Next time you launch the application, it will use the LinkedIn Blue theme.")

if __name__ == "__main__":
    main() 