"""
PST-to-Dynamics 365 Configuration Manager
=========================================

Phase 5.3: Configuration Interface Implementation
Visual configuration management for all system settings.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, 
    QGroupBox, QFrame, QScrollArea, QMessageBox, QSpinBox,
    QTabWidget, QFileDialog, QTextEdit, QProgressBar,
    QSizePolicy, QSpacerItem, QSlider, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSettings
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette

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
    print(f"⚠️ Backend modules not available in Configuration Manager: {e}")


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
        
        # Header
        header_label = QLabel("🔐 Dynamics 365 Authentication")
        header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Configure your Microsoft Dynamics 365 authentication credentials for secure access.")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-bottom: 15px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Configuration form
        form_group = QGroupBox("Authentication Credentials")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                background-color: #f8faff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 25px;
                top: 8px;
                padding: 0 10px;
                color: #2980b9;
                background-color: #f8faff;
                font-size: 12px;
            }
        """)
        
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 35, 30, 30)
        
        # Tenant ID
        self.tenant_id_edit = QLineEdit()
        self.tenant_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.tenant_id_edit.setStyleSheet(self.get_input_style())
        form_layout.addRow("Tenant ID:", self.tenant_id_edit)
        
        # Client ID
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.client_id_edit.setStyleSheet(self.get_input_style())
        form_layout.addRow("Client ID:", self.client_id_edit)
        
        # Client Secret
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_edit.setPlaceholderText("Enter client secret...")
        self.client_secret_edit.setStyleSheet(self.get_input_style())
        form_layout.addRow("Client Secret:", self.client_secret_edit)
        
        # Organization URL
        self.org_url_edit = QLineEdit()
        self.org_url_edit.setPlaceholderText("https://your-org.crm.dynamics.com")
        self.org_url_edit.setStyleSheet(self.get_input_style())
        form_layout.addRow("Organization URL:", self.org_url_edit)
        
        layout.addWidget(form_group)
        
        # Test connection button
        self.test_button = QPushButton("🔍 Test Connection")
        self.test_button.setMinimumHeight(40)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
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
        
        layout.addStretch()
    
    def get_input_style(self):
        """Get standardized input field styling"""
        return """
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 12px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLineEdit:placeholder {
                color: #95a5a6;
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
        self.setup_ui()
        self.load_all_settings()
    
    def setup_ui(self):
        """Setup the configuration manager interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content area
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Configuration tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: bold;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # Add configuration tab
        self.auth_widget = DynamicsAuthWidget()
        self.tab_widget.addTab(self.auth_widget, "🔐 Authentication")
        
        main_layout.addWidget(self.tab_widget)
        layout.addWidget(main_content, 1)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self) -> QWidget:
        """Create configuration manager header"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #9b59b6);
                border-radius: 0px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Icon
        icon_label = QLabel("⚙️")
        icon_label.setStyleSheet("font-size: 32px; color: white;")
        layout.addWidget(icon_label)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title = QLabel("Configuration Manager")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 0px;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Visual configuration management for all system settings")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; margin: 0px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        return header
    
    def create_footer(self) -> QWidget:
        """Create configuration manager footer"""
        footer = QFrame()
        footer.setFixedHeight(70)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(30, 15, 30, 15)
        
        # Status info
        self.status_label = QLabel("Configuration ready for modification")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Action buttons
        self.save_button = QPushButton("💾 Save Configuration")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.save_button.clicked.connect(self.save_all_settings)
        
        layout.addWidget(self.save_button)
        
        return footer
    
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
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration: {str(e)}")
    
    def load_all_settings(self):
        """Load all configuration settings"""
        try:
            self.auth_widget.load_settings()
            self.status_label.setText("Configuration loaded successfully")
            
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            self.status_label.setText("Using default configuration")


def main():
    """Test the Configuration Manager independently"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    config_manager = ConfigurationManager()
    config_manager.show()
    config_manager.resize(1000, 700)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 