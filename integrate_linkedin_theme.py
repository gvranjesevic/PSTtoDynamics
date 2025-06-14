#!/usr/bin/env python3
"""
Comprehensive LinkedIn Blue Theme Integration
============================================

This script integrates the LinkedIn Blue theme into all GUI components
of the PST-to-Dynamics 365 application.

Features:
- Applies LinkedIn Blue theme to all widgets
- Integrates theme manager into main components
- Ensures consistent styling across all GUI elements
- Handles theme persistence and real-time switching
"""

import sys
import os
import logging
from typing import Dict, Any, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_theme_integration():
    """Ensure theme manager is properly integrated into all GUI components"""
    
    # List of GUI files that need theme integration
    gui_files = [
        'gui/main_window.py',
        'gui/widgets/import_wizard.py',
        'gui/widgets/analytics_dashboard.py',
        'gui/widgets/ai_intelligence_dashboard.py',
        'gui/widgets/contact_management_dashboard.py',
        'gui/widgets/sync_monitoring_dashboard.py',
        'gui/widgets/configuration_manager.py',
        'gui/widgets/welcome_dialog.py'
    ]
    
    logger.info("🎨 Integrating LinkedIn Blue theme into GUI components...")
    
    for file_path in gui_files:
        if os.path.exists(file_path):
            integrate_theme_into_file(file_path)
        else:
            logger.warning(f"⚠️ File not found: {file_path}")
    
    logger.info("✅ Theme integration completed!")

def integrate_theme_into_file(file_path: str):
    """Integrate theme manager into a specific GUI file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if theme manager is already imported
        if 'from gui.themes.theme_manager import' not in content:
            # Add theme manager import
            import_section = content.find('from PyQt6.QtWidgets import')
            if import_section != -1:
                # Find the end of the PyQt6 imports
                next_import = content.find('\n\n', import_section)
                if next_import != -1:
                    new_content = (
                        content[:next_import] + 
                        '\n\n# Import theme manager\n' +
                        'try:\n' +
                        '    from gui.themes.theme_manager import ThemeManager, get_theme_manager\n' +
                        '    THEME_MANAGER_AVAILABLE = True\n' +
                        'except ImportError:\n' +
                        '    THEME_MANAGER_AVAILABLE = False\n' +
                        '    logger.warning("⚠️ Theme manager not available")\n' +
                        content[next_import:]
                    )
                    
                    # Save the updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    logger.info(f"✅ Theme integration added to {file_path}")
                else:
                    logger.warning(f"⚠️ Could not find import section in {file_path}")
            else:
                logger.warning(f"⚠️ Could not find PyQt6 imports in {file_path}")
        else:
            logger.info(f"ℹ️ Theme manager already integrated in {file_path}")
            
    except Exception as e:
        logger.error(f"❌ Error integrating theme into {file_path}: {e}")

def apply_linkedin_theme():
    """Apply LinkedIn Blue theme as the application default"""
    try:
        # Import theme manager
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gui.themes.theme_manager import ThemeManager, ThemeType
        
        # Create theme manager instance
        theme_manager = ThemeManager()
        
        # Set LinkedIn Blue as the default theme
        theme_manager.set_theme(ThemeType.LINKEDIN_BLUE, save_preference=True)
        
        print("✅ LinkedIn Blue theme applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying LinkedIn theme: {e}")
        return False

def create_theme_css():
    """Create comprehensive LinkedIn Blue CSS file"""
    linkedin_css = """
/* LinkedIn Blue Theme - Complete Application Stylesheet */
/* Generated automatically by LinkedIn theme integration */

/* =============================================================================
   MAIN APPLICATION STYLING
   ============================================================================= */

QMainWindow {
    background-color: #F3F6F8;
    color: #000000;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* =============================================================================
   NAVIGATION AND SIDEBAR
   ============================================================================= */

QFrame[objectName="NavigationSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #D0D7DE;
    border-radius: 8px;
    padding: 10px;
}

/* Navigation Buttons */
QPushButton[objectName="nav_button"] {
    background-color: transparent;
    color: #000000;
    border: none;
    padding: 12px 16px;
    text-align: left;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton[objectName="nav_button"]:hover {
    background-color: #0077B5;
    color: #FFFFFF;
}

QPushButton[objectName="nav_button"]:pressed {
    background-color: #005885;
}

/* =============================================================================
   BUTTONS
   ============================================================================= */

QPushButton {
    background-color: #0077B5;
    color: #FFFFFF;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
    min-height: 36px;
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
    border: 2px solid #0077B5;
}

QPushButton[class="secondary"]:hover {
    background-color: #0077B5;
    color: #FFFFFF;
}

/* Danger Buttons */
QPushButton[class="danger"] {
    background-color: #CC1016;
    color: #FFFFFF;
}

QPushButton[class="danger"]:hover {
    background-color: #A00D13;
}

/* =============================================================================
   INPUT FIELDS
   ============================================================================= */

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 2px solid #D0D7DE;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0077B5;
    outline: none;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #F9FAFB;
    color: #666666;
    border-color: #E8EBED;
}

/* =============================================================================
   LABELS
   ============================================================================= */

QLabel {
    color: #000000;
    font-size: 14px;
    line-height: 1.4;
}

QLabel[class="title"] {
    font-size: 22px;
    font-weight: 600;
    color: #0077B5;
    margin-bottom: 8px;
}

QLabel[class="heading"] {
    font-size: 18px;
    font-weight: 500;
    color: #000000;
    margin-bottom: 6px;
}

QLabel[class="secondary"] {
    color: #666666;
}

QLabel[class="muted"] {
    color: #999999;
}

QLabel[class="success"] {
    color: #057642;
    font-weight: 500;
}

QLabel[class="warning"] {
    color: #B8860B;
    font-weight: 500;
}

QLabel[class="error"] {
    color: #CC1016;
    font-weight: 500;
}

/* =============================================================================
   TABLES
   ============================================================================= */

QTableWidget, QTableView {
    background-color: #FFFFFF;
    alternate-background-color: #F9FAFB;
    gridline-color: #E8EBED;
    border: 1px solid #D0D7DE;
    border-radius: 8px;
    selection-background-color: #0077B5;
}

QTableWidget::item, QTableView::item {
    padding: 12px 8px;
    border-bottom: 1px solid #E8EBED;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #F9FAFB;
    color: #000000;
    padding: 12px 8px;
    border: none;
    border-bottom: 2px solid #0077B5;
    font-weight: 600;
    font-size: 14px;
}

/* =============================================================================
   PROGRESS BARS
   ============================================================================= */

QProgressBar {
    background-color: #F9FAFB;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
    min-height: 24px;
}

QProgressBar::chunk {
    background-color: #0077B5;
    border-radius: 6px;
}

/* =============================================================================
   COMBO BOXES
   ============================================================================= */

QComboBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 2px solid #D0D7DE;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
}

QComboBox:focus {
    border-color: #0077B5;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666666;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    selection-background-color: #0077B5;
    selection-color: #FFFFFF;
}

/* =============================================================================
   CHECKBOXES AND RADIO BUTTONS
   ============================================================================= */

QCheckBox, QRadioButton {
    color: #000000;
    font-size: 14px;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #D0D7DE;
    border-radius: 3px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #0077B5;
    border-color: #0077B5;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #0077B5;
}

/* =============================================================================
   TABS
   ============================================================================= */

QTabWidget::pane {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 8px;
    padding: 16px;
}

QTabBar::tab {
    background-color: #F9FAFB;
    color: #666666;
    padding: 12px 24px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QTabBar::tab:hover {
    background-color: #004471;
    color: #FFFFFF;
}

/* =============================================================================
   SCROLL BARS
   ============================================================================= */

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

/* =============================================================================
   MENU AND STATUS BAR
   ============================================================================= */

QMenuBar {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom: 1px solid #D0D7DE;
    padding: 4px;
}

QMenuBar::item {
    padding: 8px 16px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0077B5;
    color: #FFFFFF;
}

QStatusBar {
    background-color: #FFFFFF;
    color: #666666;
    border-top: 1px solid #D0D7DE;
    font-size: 12px;
}

/* =============================================================================
   TOOL BAR
   ============================================================================= */

QToolBar {
    background-color: #FFFFFF;
    border: none;
    spacing: 8px;
    padding: 8px;
}

QToolButton {
    background-color: transparent;
    color: #000000;
    border: none;
    padding: 8px;
    border-radius: 6px;
    min-height: 32px;
    min-width: 32px;
}

QToolButton:hover {
    background-color: #0077B5;
    color: #FFFFFF;
}

QToolButton:pressed {
    background-color: #005885;
}

/* =============================================================================
   GROUPS AND FRAMES
   ============================================================================= */

QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
    font-weight: 500;
}

QGroupBox::title {
    color: #0077B5;
    font-size: 16px;
    font-weight: 600;
    padding: 0 8px;
}

QFrame {
    background-color: #FFFFFF;
    border: 1px solid #E8EBED;
    border-radius: 6px;
}

/* =============================================================================
   SPLITTER
   ============================================================================= */

QSplitter::handle {
    background-color: #D0D7DE;
    width: 4px;
    border-radius: 2px;
}

QSplitter::handle:hover {
    background-color: #0077B5;
}

QSplitter::handle:vertical {
    height: 4px;
}

/* =============================================================================
   TOOLTIPS
   ============================================================================= */

QToolTip {
    background-color: #000000;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-size: 12px;
}

/* =============================================================================
   DIALOG BOXES
   ============================================================================= */

QDialog {
    background-color: #F3F6F8;
    color: #000000;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
    margin: 0 4px;
}

/* =============================================================================
   CUSTOM WIDGET STYLES
   ============================================================================= */

/* Welcome Dialog */
QDialog[objectName="WelcomeDialog"] {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 12px;
}

/* Import Wizard */
QWidget[objectName="ImportWizard"] {
    background-color: #F3F6F8;
}

/* Dashboard Cards */
QFrame[objectName="DashboardCard"] {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 8px;
    padding: 16px;
}

/* Status Indicators */
QLabel[objectName="StatusIndicator"] {
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 500;
    font-size: 12px;
}

QLabel[objectName="StatusIndicator"][status="success"] {
    background-color: #057642;
    color: #FFFFFF;
}

QLabel[objectName="StatusIndicator"][status="warning"] {
    background-color: #F5C75D;
    color: #000000;
}

QLabel[objectName="StatusIndicator"][status="error"] {
    background-color: #CC1016;
    color: #FFFFFF;
}

QLabel[objectName="StatusIndicator"][status="info"] {
    background-color: #0077B5;
    color: #FFFFFF;
}
"""
    
    try:
        with open('linkedin_blue_complete.css', 'w', encoding='utf-8') as f:
            f.write(linkedin_css)
        logger.info("✅ Complete LinkedIn Blue stylesheet created!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating stylesheet: {e}")
        return False

def update_main_window():
    """Update main window to use LinkedIn Blue theme"""
    main_window_file = 'gui/main_window.py'
    
    if not os.path.exists(main_window_file):
        logger.error(f"❌ Main window file not found: {main_window_file}")
        return False
    
    try:
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if theme manager initialization is already present
        if 'theme_manager = get_theme_manager()' not in content:
            # Find the __init__ method of MainWindow class
            init_method = content.find('def __init__(self):')
            if init_method != -1:
                # Find the end of __init__ method setup
                super_call = content.find('super().__init__()', init_method)
                if super_call != -1:
                    next_line = content.find('\n', super_call)
                    if next_line != -1:
                        # Add theme manager initialization
                        theme_init = '''
        # Initialize theme manager
        if THEME_MANAGER_AVAILABLE:
            self.theme_manager = get_theme_manager()
            self.theme_manager.theme_changed.connect(self.on_theme_changed)
            # Apply current theme
            self.apply_current_theme()
'''
                        
                        new_content = content[:next_line] + theme_init + content[next_line:]
                        
                        # Add theme change handler method
                        class_end = new_content.rfind('class MainWindow')
                        next_class = new_content.find('\nclass ', class_end + 1)
                        if next_class == -1:
                            next_class = len(new_content)
                        
                        theme_methods = '''
    def on_theme_changed(self, theme_name: str):
        """Handle theme change events"""
        self.apply_current_theme()
    
    def apply_current_theme(self):
        """Apply the current theme to the main window"""
        if hasattr(self, 'theme_manager'):
            theme_def = self.theme_manager.get_theme_definition()
            if theme_def:
                self.setStyleSheet(self.theme_manager.get_stylesheet_for_widget('QMainWindow'))
                logger.info(f"Applied theme: {theme_def.get('name', 'Unknown')}")
'''
                        
                        new_content = new_content[:next_class] + theme_methods + new_content[next_class:]
                        
                        # Save the updated content
                        with open(main_window_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        logger.info("✅ Main window updated with theme support")
                        return True
                        
        else:
            logger.info("ℹ️ Main window already has theme support")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error updating main window: {e}")
        return False

def main():
    """Main function to integrate LinkedIn Blue theme"""
    print("🚀 Applying LinkedIn Blue theme to all GUI elements...")
    
    if apply_linkedin_theme():
        print("✅ LinkedIn Blue theme has been applied to all GUI elements!")
        print("🎨 Theme features:")
        print("   • LinkedIn signature blue (#0077B5) throughout the UI")
        print("   • Professional light background (#F3F6F8)")
        print("   • Clean white surfaces with subtle blue accents")
        print("   • Consistent styling across all components")
        print("🚀 Launch the application to see the LinkedIn Blue theme!")
    else:
        print("❌ Failed to apply LinkedIn Blue theme")

if __name__ == "__main__":
    main() 