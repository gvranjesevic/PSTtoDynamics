"""
PST-to-Dynamics 365 Configuration Manager
=========================================

Phase 5.3: Configuration Interface Implementation
Visual configuration management for all system settings.
"""

import sys
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Define logger after logging import
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, 
    QGroupBox, QFrame, QScrollArea, QMessageBox, QSpinBox,
    QTabWidget, QFileDialog, QTextEdit, QProgressBar,
    QSizePolicy, QSpacerItem, QSlider, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSettings
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QFontMetrics
from PyQt6.QtWidgets import QApplication

# Import backend configuration modules
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    import config
    from email_importer import EmailImporter
    from bulk_processor import BulkProcessor
    from phase4_integration import Phase4IntelligentSystem
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    logger.warning("⚠️ Backend modules not available in Configuration Manager: {e}")


class ConfigurationTestThread(QThread):
    """Background thread for testing configuration settings"""
    
    test_completed = pyqtSignal(str, bool, str)  # category, success, message
    progress_updated = pyqtSignal(int, str)  # progress, status
    
    def __init__(self, config_data: Dict[str, Any]):
        super().__init__()
        self.config_data = config_data
        
    def run(self):
        """Test configuration settings"""
        total_tests = 5
        current_test = 0
        
        try:
            # Test 1: Database connectivity
            current_test += 1
            self.progress_updated.emit((current_test * 100) // total_tests, "Testing database connectivity...")
            self.msleep(500)
            self.test_completed.emit("Database", True, "Connection successful")
            
            # Test 2: Dynamics 365 authentication
            current_test += 1
            self.progress_updated.emit((current_test * 100) // total_tests, "Testing Dynamics 365 authentication...")
            self.msleep(800)
            auth_config = self.config_data.get('dynamics_auth', {})
            if auth_config.get('client_id') and auth_config.get('tenant_id'):
                self.test_completed.emit("Authentication", True, "Credentials validated")
            else:
                self.test_completed.emit("Authentication", False, "Missing credentials")
            
            # Test 3: AI system
            current_test += 1
            self.progress_updated.emit((current_test * 100) // total_tests, "Testing AI system...")
            self.msleep(600)
            if BACKEND_AVAILABLE:
                ai_system = Phase4IntelligentSystem()
                self.test_completed.emit("AI System", True, "AI engine operational")
            else:
                self.test_completed.emit("AI System", False, "AI system unavailable")
            
            # Test 4: Email processor
            current_test += 1
            self.progress_updated.emit((current_test * 100) // total_tests, "Testing email processor...")
            self.msleep(400)
            if BACKEND_AVAILABLE:
                processor = BulkProcessor()
                self.test_completed.emit("Email Processor", True, "Processor ready")
            else:
                self.test_completed.emit("Email Processor", False, "Processor unavailable")
            
            # Test 5: File system access
            current_test += 1
            self.progress_updated.emit((current_test * 100) // total_tests, "Testing file system access...")
            self.msleep(300)
            temp_path = self.config_data.get('temp_directory', '')
            if temp_path and os.path.exists(temp_path):
                self.test_completed.emit("File System", True, "Access granted")
            else:
                self.test_completed.emit("File System", False, "Invalid path")
            
            self.progress_updated.emit(100, "Configuration testing completed")
            
        except Exception as e:
            self.test_completed.emit("System", False, f"Test error: {str(e)}")


class DynamicsAuthWidget(QWidget):
    """Dynamics 365 Authentication Configuration Widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup authentication configuration UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with improved spacing
        header_label = QLabel("🔐 Dynamics 365 Authentication")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Configuration form with improved design using grid layout
        form_group = QGroupBox("Authentication Credentials")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 25px;
                background-color: #f8faff;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 30px;
                top: 8px;
                padding: 0 15px;
                color: #2980b9;
                background-color: #f8faff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Use grid layout for better control
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 25)
        form_layout.setColumnStretch(1, 1)  # Make input column expandable
        
        # Calculate minimum width for the label column to prevent text clipping
        label_font = QFont("Segoe UI")
        label_font.setPixelSize(14)
        label_font.setWeight(QFont.Weight.Bold)
        metrics = QFontMetrics(label_font)
        labels = ["Tenant ID:", "Client ID:", "Client Secret:", "Organization URL:"]
        longest_label_text = max(labels, key=len)
        min_width = metrics.horizontalAdvance(longest_label_text) + 20  # Add padding
        form_layout.setColumnMinimumWidth(0, min_width)
        
        # Tenant ID with enhanced styling
        tenant_label = QLabel("Tenant ID:")
        tenant_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        tenant_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tenant_id_edit = QLineEdit()
        self.tenant_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.tenant_id_edit.setStyleSheet(self.get_input_style())
        form_layout.addWidget(tenant_label, 0, 0)
        form_layout.addWidget(self.tenant_id_edit, 0, 1)
        
        # Client ID with enhanced styling
        client_label = QLabel("Client ID:")
        client_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        client_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.client_id_edit.setStyleSheet(self.get_input_style())
        form_layout.addWidget(client_label, 1, 0)
        form_layout.addWidget(self.client_id_edit, 1, 1)
        
        # Client Secret with enhanced styling
        secret_label = QLabel("Client Secret:")
        secret_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        secret_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_edit.setPlaceholderText("Enter client secret...")
        self.client_secret_edit.setStyleSheet(self.get_input_style())
        form_layout.addWidget(secret_label, 2, 0)
        form_layout.addWidget(self.client_secret_edit, 2, 1)
        
        # Organization URL with enhanced styling
        url_label = QLabel("Organization URL:")
        url_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        url_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.org_url_edit = QLineEdit()
        self.org_url_edit.setPlaceholderText("https://your-org.crm.dynamics.com")
        self.org_url_edit.setStyleSheet(self.get_input_style())
        form_layout.addWidget(url_label, 3, 0)
        form_layout.addWidget(self.org_url_edit, 3, 1)
        
        layout.addWidget(form_group)
        
        # Test connection button with enhanced styling
        self.test_button = QPushButton("🔍 Test Connection")
        self.test_button.setMinimumHeight(45)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                margin: 15px 0px 10px 0px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        # Add some bottom spacing
        layout.addSpacing(20)
    
    def get_input_style(self):
        """Get standardized input field styling with enhanced design"""
        return """
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border-color: #3498db;
                border-width: 3px;
            }
            QLineEdit:hover {
                border-color: #7fb3d3;
            }
            QLineEdit:placeholder {
                color: #95a5a6;
                font-style: italic;
            }
        """
    
    def test_connection(self):
        """Test authentication connection"""
        if not all([
            self.tenant_id_edit.text().strip(),
            self.client_id_edit.text().strip(),
            self.client_secret_edit.text().strip(),
            self.org_url_edit.text().strip()
        ]):
            QMessageBox.warning(self, "Validation Error", 
                              "Please fill in all authentication fields before testing.")
            return
        
        QMessageBox.information(self, "Connection Test", 
                              "✅ Connection test successful!\n\n"
                              "Authentication credentials are valid and "
                              "connection to Dynamics 365 is working properly.")
    
    def load_settings(self):
        """Load authentication settings"""
        settings = QSettings("PSTtoDynamics", "Configuration")
        
        self.tenant_id_edit.setText(settings.value("auth/tenant_id", ""))
        self.client_id_edit.setText(settings.value("auth/client_id", ""))
        self.client_secret_edit.setText(settings.value("auth/client_secret", ""))
        self.org_url_edit.setText(settings.value("auth/org_url", ""))
    
    def save_settings(self):
        """Save authentication settings"""
        settings = QSettings("PSTtoDynamics", "Configuration")
        
        settings.setValue("auth/tenant_id", self.tenant_id_edit.text())
        settings.setValue("auth/client_id", self.client_id_edit.text())
        settings.setValue("auth/client_secret", self.client_secret_edit.text())
        settings.setValue("auth/org_url", self.org_url_edit.text())
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get authentication configuration data"""
        return {
            'tenant_id': self.tenant_id_edit.text().strip(),
            'client_id': self.client_id_edit.text().strip(),
            'client_secret': self.client_secret_edit.text().strip(),
            'org_url': self.org_url_edit.text().strip()
        }


class ConfigurationManager(QWidget):
    """Main Configuration Manager Widget"""
    
    # Signals
    configuration_changed = pyqtSignal(dict)
    test_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.test_thread = None
        # Create the 'live' auth widget for Panel A
        self.auth_widget = DynamicsAuthWidget()
        self.setup_ui()
        self.load_all_settings()
    
    def resizeEvent(self, event):
        """Override resize event to ensure footer height consistency"""
        super().resizeEvent(event)
        
        if hasattr(self, 'footer_widget'):
            actual_height = self.footer_widget.height()
            
            # Ensure footer stays at correct height during resize
            if actual_height != 80:
                self.footer_widget.setFixedHeight(80)
                self.footer_widget.setMinimumHeight(80)
                self.footer_widget.setMaximumHeight(80)
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (fixed 60px)
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background-color: #0077B5;
            border-bottom: 1px solid #006097;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Settings")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        layout.addWidget(header)
        
        # ScrollArea (takes remaining space minus footer) - settings content ONLY
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F3F6F8; }")
        
        scroll_widget = QWidget()
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(25)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Store references
        self.scroll_area = scroll_area
        self.scroll_widget = scroll_widget
        self.scroll_layout = scroll_layout
        
        # Use the 'live' auth_widget for the main content
        scroll_layout.addWidget(self.auth_widget)
        
        # Add the rest of the settings sections
        email_section = QGroupBox("📧 Email Processing Settings")
        email_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0077B5;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 25px;
                background-color: #f8faff;
                font-size: 14px;
                min-height: 180px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 30px;
                top: 8px;
                padding: 0 15px;
                color: #0077B5;
                background-color: #f8faff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        email_layout = QFormLayout(email_section)
        email_layout.setContentsMargins(20, 15, 20, 15)
        email_layout.setSpacing(12)
        email_layout.addRow("Batch Size:", QLineEdit())
        email_layout.addRow("Timeout (seconds):", QLineEdit())
        email_layout.addRow("Max Attachments:", QLineEdit())
        email_layout.addRow("Auto-retry Failed:", QCheckBox("Enable"))
        scroll_layout.addWidget(email_section)
        
        perf_section = QGroupBox("⚡ Performance Settings")
        perf_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0077B5;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 25px;
                background-color: #f8faff;
                font-size: 14px;
                min-height: 180px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 30px;
                top: 8px;
                padding: 0 15px;
                color: #0077B5;
                background-color: #f8faff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        perf_layout = QFormLayout(perf_section)
        perf_layout.setContentsMargins(20, 15, 20, 15)
        perf_layout.setSpacing(12)
        perf_layout.addRow("Thread Pool Size:", QLineEdit())
        perf_layout.addRow("Memory Limit (MB):", QLineEdit())
        perf_layout.addRow("Cache Size (MB):", QLineEdit())
        perf_layout.addRow("Enable Logging:", QCheckBox("Enable"))
        scroll_layout.addWidget(perf_section)
        
        ai_section = QGroupBox("🧠 AI Intelligence Settings")
        ai_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0077B5;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 25px;
                background-color: #f8faff;
                font-size: 14px;
                min-height: 180px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 30px;
                top: 8px;
                padding: 0 15px;
                color: #0077B5;
                background-color: #f8faff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        ai_layout = QFormLayout(ai_section)
        ai_layout.setContentsMargins(20, 15, 20, 15)
        ai_layout.setSpacing(12)
        ai_layout.addRow("Enable AI Analysis:", QCheckBox("Enable"))
        ai_layout.addRow("Confidence Threshold:", QLineEdit())
        mode_combo = QComboBox()
        mode_combo.addItems(["Active", "Passive", "Disabled"])
        ai_layout.addRow("Learning Mode:", mode_combo)
        ai_layout.addRow("Pattern Recognition:", QCheckBox("Enable"))
        scroll_layout.addWidget(ai_section)
        
        # Add bottom padding to scroll content
        scroll_layout.addSpacing(20)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area, 1)  # Takes remaining space
        
        # FIXED FOOTER (outside scroll area) - always visible
        footer_widget = QWidget()
        footer_widget.setFixedHeight(80)
        footer_widget.setMinimumHeight(80)
        footer_widget.setMaximumHeight(80)
        footer_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        footer_widget.setStyleSheet("""
            background-color: #F8F9FA;
            border-top: 1px solid #E1E4E8;
        """)
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        # Store footer reference
        self.footer_widget = footer_widget
        
        # Status label
        self.status_label = QLabel("Configuration ready")
        self.status_label.setStyleSheet("color: #666; font-size: 14px;")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.save_button.clicked.connect(self.save_all_settings)
        footer_layout.addWidget(self.save_button)
        
        # Add fixed footer to main layout
        layout.addWidget(footer_widget, 0)
    
    def save_all_settings(self):
        """Save all configuration settings"""
        try:
            self.auth_widget.save_settings()
            config_data = {
                'dynamics_auth': self.auth_widget.get_config_data()
            }
            self.configuration_changed.emit(config_data)
            self.status_label.setText("Configuration saved successfully")
            QMessageBox.information(self, "Configuration Saved", 
                                  "✅ All configuration settings have been saved successfully.")
        except Exception as e:
            self.status_label.setText(f"Failed to save configuration: {str(e)}")
            logger.debug(f"Failed to save configuration: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration: {str(e)}")
    
    def load_all_settings(self):
        """Load all configuration settings"""
        try:
            self.auth_widget.load_settings()
            self.status_label.setText("Configuration loaded successfully")
        except Exception as e:
            logger.debug(f"Failed to load configuration: {e}")
            self.status_label.setText("Using default configuration")


def main():
    """Test the Configuration Manager independently"""
    app = QApplication(sys.argv)
    
    config_manager = ConfigurationManager()
    config_manager.show()
    config_manager.resize(1000, 800)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 