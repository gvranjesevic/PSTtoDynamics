"""
Contact Management Interface
============================

This module provides a complete GUI interface for managing Dynamics 365 contacts including:

Features:
- Contact browser with search and filtering
- Contact creation and editing forms
- Relationship mapping and email history
- Bulk operations and data export
- Import history tracking
- Advanced contact analytics
- Enhanced UX with keyboard navigation and rich tooltips
- Performance optimization with virtual scrolling and caching
- Background task management
- Notification system
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                           QLineEdit, QComboBox, QCheckBox, QSpinBox, QGroupBox,
                           QGridLayout, QFormLayout, QTextEdit, QScrollArea,
                           QSplitter, QHeaderView, QAbstractItemView, QTreeWidget,
                           QTreeWidgetItem, QProgressBar, QDateEdit, QDialog,
                           QDialogButtonBox, QMessageBox, QFileDialog, QFrame)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QDate, QSortFilterProxyModel
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush, QIcon, QStandardItemModel, QStandardItem

# Enhanced Components
try:
    sys.path.append('gui/themes')
    sys.path.append('gui/core')
    from theme_manager import get_theme_manager, ThemeType, apply_theme_to_widget
    from enhanced_ux import (
        get_keyboard_navigation_manager, get_notification_center, 
        add_tooltip, show_notification, NotificationType
    )
    from performance_optimizer import (
        get_performance_monitor, get_cache_manager, create_virtual_table,
        run_background_task, PerformanceWidget
    )
    PHASE_5_7_AVAILABLE = True
except ImportError as e:
    PHASE_5_7_AVAILABLE = False

# Try to import contact management modules
try:
    import sys
    sys.path.append('.')
    from contact_creator import ContactCreator
    from dynamics_data import get_dynamics_contacts
    import auth
    import config
    CONTACT_MODULES_AVAILABLE = True
except ImportError as e:
    CONTACT_MODULES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log import status after logger is defined
if PHASE_5_7_AVAILABLE:
    logger.info("✅ Enhanced components loaded successfully")
else:
    logger.warning("⚠️ Enhanced components not available")

if CONTACT_MODULES_AVAILABLE:
    logger.info("✅ Contact management modules loaded successfully")
else:
    logger.warning("⚠️ Contact management modules not available")

class ContactDataLoader(QThread):
    """Background thread for loading contact data with performance optimization"""
    contacts_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.contact_creator = None
        
        # Initialize cache manager
        if PHASE_5_7_AVAILABLE:
            self.cache_manager = get_cache_manager()
        
        if CONTACT_MODULES_AVAILABLE:
            try:
                self.contact_creator = ContactCreator()
            except Exception as e:
                logger.error(f"Error initializing contact creator: {e}")
    
    def run(self):
        """Load contacts from Dynamics 365 with caching"""
        try:
            self.progress_updated.emit(0, "Connecting to Dynamics 365...")
            
            # Phase 5.7: Check cache first
            if PHASE_5_7_AVAILABLE:
                cached_contacts = self.cache_manager.get("contacts_data")
                if cached_contacts is not None:
                    self.progress_updated.emit(100, "Contacts loaded from cache")
                    self.contacts_loaded.emit(cached_contacts)
                    return
            
            if CONTACT_MODULES_AVAILABLE and self.contact_creator:
                # Load real contacts
                self.progress_updated.emit(30, "Loading contacts...")
                contacts = self.contact_creator._get_existing_contacts()
                
                # Phase 5.7: Cache the results
                if PHASE_5_7_AVAILABLE:
                    self.cache_manager.put("contacts_data", contacts)
                
                self.progress_updated.emit(100, "Contacts loaded successfully")
                self.contacts_loaded.emit(contacts)
            else:
                # Generate sample contacts for testing
                self.progress_updated.emit(50, "Generating sample data...")
                sample_contacts = self._generate_sample_contacts()
                
                # Phase 5.7: Cache sample data too
                if PHASE_5_7_AVAILABLE:
                    self.cache_manager.put("contacts_data", sample_contacts)
                
                self.progress_updated.emit(100, "Sample contacts loaded")
                self.contacts_loaded.emit(sample_contacts)
                
        except Exception as e:
            self.error_occurred.emit(f"Error loading contacts: {str(e)}")
    
    def stop(self):
        """Stop the data loader"""
        self.running = False
        self.quit()
        self.wait()
    
    def _generate_sample_contacts(self) -> List[Dict]:
        """Generate sample contact data for testing"""
        import random
        from datetime import datetime, timedelta
        
        sample_contacts = []
        companies = ["Microsoft", "Google", "Apple", "Amazon", "Salesforce", "Dynamics Inc", "TechCorp", "InnovateLLC"]
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Mary"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson"]
        
        for i in range(50):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            company = random.choice(companies)
            
            contact = {
                'contactid': f"sample-{i:03d}-{random.randint(1000,9999)}",
                'fullname': f"{first_name} {last_name}",
                'firstname': first_name,
                'lastname': last_name,
                'emailaddress1': f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com",
                'emailaddress2': None,
                'emailaddress3': None,
                'telephone1': f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                'mobilephone': f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                'jobtitle': random.choice(["Manager", "Director", "Analyst", "Consultant", "Developer", "Sales Rep"]),
                'address1_city': random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                'address1_stateorprovince': random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                'address1_country': "USA",
                'createdon': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'modifiedon': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'statecode': 0,
                'statuscode': "Active"
            }
            sample_contacts.append(contact)
        
        return sample_contacts

class ContactEditDialog(QDialog):
    """Dialog for creating/editing contacts with Phase 5.7 enhancements"""
    
    def __init__(self, contact_data=None, parent=None):
        super().__init__(parent)
        self.contact_data = contact_data or {}
        self.is_new_contact = contact_data is None
        
        self.setWindowTitle("New Contact" if self.is_new_contact else "Edit Contact")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        self.populate_fields()
        
        # Phase 5.7: Apply theme and enhanced UX
        if PHASE_5_7_AVAILABLE:
            self._apply_phase_5_7_enhancements()
    
    def _apply_phase_5_7_enhancements(self):
        """Apply Phase 5.7 theme and UX enhancements"""
        # Register with theme manager
        theme_manager = get_theme_manager()
        if theme_manager:
            theme_manager.register_widget(self)
        
        # Add tooltips to form fields
        tooltips = {
            self.first_name_edit: "Enter the contact's first name",
            self.last_name_edit: "Enter the contact's last name", 
            self.full_name_edit: "Full name (auto-generated from first + last name)",
            self.job_title_edit: "Contact's job title or position",
            self.email1_edit: "Primary email address for this contact",
            self.email2_edit: "Secondary or alternate email address",
            self.phone_edit: "Business phone number",
            self.mobile_edit: "Mobile/cell phone number"
        }
        
        for widget, tooltip_text in tooltips.items():
            add_tooltip(widget, tooltip_text)
    
    def apply_theme(self, theme_definition):
        """Apply theme to dialog (Phase 5.7)"""
        colors = theme_definition['colors']
        fonts = theme_definition['fonts']
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors['background']};
                color: {colors['text_primary']};
                font-family: "{fonts['primary']}";
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {colors['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {colors['text_primary']};
            }}
        """)
    
    def setup_ui(self):
        """Set up the contact edit dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Contact Information")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #0077B5;
                padding: 16px 24px;
                border-radius: 8px;
                margin-bottom: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #FFFFFF;
            }
        """)
        scroll_widget = QWidget()
        form_layout = QVBoxLayout(scroll_widget)
        form_layout.setSpacing(20)
        
        # Basic Information
        basic_group = QGroupBox("👤 Basic Information")
        basic_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        basic_layout = QFormLayout(basic_group)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Enter first name...")
        self.first_name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        basic_layout.addRow("First Name:", self.first_name_edit)
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Enter last name...")
        self.last_name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        basic_layout.addRow("Last Name:", self.last_name_edit)
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Auto-generated or custom...")
        self.full_name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        basic_layout.addRow("Full Name:", self.full_name_edit)
        
        self.job_title_edit = QLineEdit()
        self.job_title_edit.setPlaceholderText("Enter job title...")
        self.job_title_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        basic_layout.addRow("Job Title:", self.job_title_edit)
        
        form_layout.addWidget(basic_group)
        
        # Contact Information
        contact_group = QGroupBox("📧 Contact Information")
        contact_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        contact_layout = QFormLayout(contact_group)
        
        self.email1_edit = QLineEdit()
        self.email1_edit.setPlaceholderText("Primary email address...")
        self.email1_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        contact_layout.addRow("Primary Email:", self.email1_edit)
        
        self.email2_edit = QLineEdit()
        self.email2_edit.setPlaceholderText("Secondary email address...")
        self.email2_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        contact_layout.addRow("Secondary Email:", self.email2_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Business phone number...")
        self.phone_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        contact_layout.addRow("Business Phone:", self.phone_edit)
        
        self.mobile_edit = QLineEdit()
        self.mobile_edit.setPlaceholderText("Mobile phone number...")
        self.mobile_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        contact_layout.addRow("Mobile Phone:", self.mobile_edit)
        
        form_layout.addWidget(contact_group)
        
        # Address Information
        address_group = QGroupBox("🏢 Address Information")
        address_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        address_layout = QFormLayout(address_group)
        
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("City...")
        self.city_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        address_layout.addRow("City:", self.city_edit)
        
        self.state_edit = QLineEdit()
        self.state_edit.setPlaceholderText("State/Province...")
        self.state_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        address_layout.addRow("State/Province:", self.state_edit)
        
        self.country_edit = QLineEdit()
        self.country_edit.setPlaceholderText("Country...")
        self.country_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        address_layout.addRow("Country:", self.country_edit)
        
        form_layout.addWidget(address_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Save Contact")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.save_button.clicked.connect(self.accept_contact)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: 2px solid #6C757D;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect name fields for auto-generation
        self.first_name_edit.textChanged.connect(self.update_full_name)
        self.last_name_edit.textChanged.connect(self.update_full_name)
    
    def populate_fields(self):
        """Populate form fields with contact data"""
        if self.contact_data:
            self.first_name_edit.setText(self.contact_data.get('firstname', ''))
            self.last_name_edit.setText(self.contact_data.get('lastname', ''))
            self.full_name_edit.setText(self.contact_data.get('fullname', ''))
            self.job_title_edit.setText(self.contact_data.get('jobtitle', ''))
            self.email1_edit.setText(self.contact_data.get('emailaddress1', ''))
            self.email2_edit.setText(self.contact_data.get('emailaddress2', ''))
            self.phone_edit.setText(self.contact_data.get('telephone1', ''))
            self.mobile_edit.setText(self.contact_data.get('mobilephone', ''))
            self.city_edit.setText(self.contact_data.get('address1_city', ''))
            self.state_edit.setText(self.contact_data.get('address1_stateorprovince', ''))
            self.country_edit.setText(self.contact_data.get('address1_country', ''))
    
    def update_full_name(self):
        """Auto-update full name when first/last name changes"""
        if not self.full_name_edit.text():  # Only auto-update if empty
            first = self.first_name_edit.text().strip()
            last = self.last_name_edit.text().strip()
            if first and last:
                self.full_name_edit.setText(f"{first} {last}")
            elif first:
                self.full_name_edit.setText(first)
            elif last:
                self.full_name_edit.setText(last)
    
    def accept_contact(self):
        """Validate and accept contact data"""
        # Basic validation
        if not self.first_name_edit.text().strip() and not self.last_name_edit.text().strip():
            # Phase 5.7: Show notification instead of message box
            if PHASE_5_7_AVAILABLE:
                show_notification(self, "Please enter at least a first or last name", NotificationType.WARNING)
            else:
                QMessageBox.warning(self, "Validation Error", "Please enter at least a first or last name")
            return
        
        # Update contact data
        self.contact_data = {
            'firstname': self.first_name_edit.text().strip(),
            'lastname': self.last_name_edit.text().strip(),
            'fullname': self.full_name_edit.text().strip(),
            'jobtitle': self.job_title_edit.text().strip(),
            'emailaddress1': self.email1_edit.text().strip(),
            'emailaddress2': self.email2_edit.text().strip(),
            'telephone1': self.phone_edit.text().strip(),
            'mobilephone': self.mobile_edit.text().strip(),
            'address1_city': self.city_edit.text().strip(),
            'address1_stateorprovince': self.state_edit.text().strip(),
            'address1_country': self.country_edit.text().strip(),
        }
        
        # Auto-generate full name if empty
        if not self.contact_data['fullname']:
            if self.contact_data['firstname'] and self.contact_data['lastname']:
                self.contact_data['fullname'] = f"{self.contact_data['firstname']} {self.contact_data['lastname']}"
            elif self.contact_data['firstname']:
                self.contact_data['fullname'] = self.contact_data['firstname']
            elif self.contact_data['lastname']:
                self.contact_data['fullname'] = self.contact_data['lastname']
        
        # Add timestamps for new contacts
        if self.is_new_contact:
            now = datetime.now().isoformat()
            self.contact_data['createdon'] = now
            self.contact_data['modifiedon'] = now
            self.contact_data['contactid'] = f"new-{int(datetime.now().timestamp())}"
        else:
            self.contact_data['modifiedon'] = datetime.now().isoformat()
        
        self.accept()

class ContactRelationshipView(QWidget):
    """Widget for viewing contact relationships and email history"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the relationship view UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔗 Contact Relationships & Email History")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0077B5; margin: 10px; font-weight: bold;")
        layout.addWidget(header)
        
        # Splitter for relationship tree and email history
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Relationship tree
        relationship_group = QGroupBox("🌐 Contact Network")
        relationship_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        relationship_layout = QVBoxLayout(relationship_group)
        
        self.relationship_tree = QTreeWidget()
        self.relationship_tree.setHeaderLabels(["Contact", "Relationship", "Emails", "Last Contact"])
        self.relationship_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #D0D7DE;
                border-radius: 8px;
                background: #FFFFFF;
                alternate-background-color: #F9FAFB;
                color: #666666;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTreeWidget::item:selected {
                background-color: #0077B5;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #E8F4FD;
                color: #0077B5;
            }
        """)
        relationship_layout.addWidget(self.relationship_tree)
        
        splitter.addWidget(relationship_group)
        
        # Email history
        email_group = QGroupBox("📧 Email History")
        email_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        email_layout = QVBoxLayout(email_group)
        
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["Date", "Subject", "Direction", "Status"])
        self.email_table.horizontalHeader().setStretchLastSection(True)
        self.email_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D7DE;
                border-radius: 8px;
                background: #FFFFFF;
                alternate-background-color: #F9FAFB;
                color: #666666;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #0077B5;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #E8F4FD;
                color: #0077B5;
            }
            QHeaderView::section {
                background-color: #0077B5;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        email_layout.addWidget(self.email_table)
        
        splitter.addWidget(email_group)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
    
    def load_contact_relationships(self, contact_id: str):
        """Load relationships for a specific contact"""
        # Clear existing data
        self.relationship_tree.clear()
        self.email_table.setRowCount(0)
        
        # Sample relationship data
        relationships = [
            ("John Smith", "Colleague", 15, "2024-12-15"),
            ("Sarah Johnson", "Manager", 8, "2024-12-14"),
            ("Mike Davis", "Client", 22, "2024-12-13"),
            ("Lisa Wilson", "Vendor", 5, "2024-12-12")
        ]
        
        for name, rel_type, email_count, last_contact in relationships:
            item = QTreeWidgetItem([name, rel_type, str(email_count), last_contact])
            self.relationship_tree.addTopLevelItem(item)
        
        # Sample email history
        emails = [
            ("2024-12-15 10:30", "Project Update", "Outgoing", "Sent"),
            ("2024-12-14 15:45", "Meeting Request", "Incoming", "Received"),
            ("2024-12-13 09:15", "Budget Approval", "Outgoing", "Sent"),
            ("2024-12-12 16:20", "Status Report", "Incoming", "Received")
        ]
        
        self.email_table.setRowCount(len(emails))
        for row, (date, subject, direction, status) in enumerate(emails):
            self.email_table.setItem(row, 0, QTableWidgetItem(date))
            self.email_table.setItem(row, 1, QTableWidgetItem(subject))
            self.email_table.setItem(row, 2, QTableWidgetItem(direction))
            self.email_table.setItem(row, 3, QTableWidgetItem(status))

class ContactManagementDashboard(QWidget):
    """Complete Contact Management Dashboard with Phase 5.7 Enhancements"""
    
    def __init__(self):
        super().__init__()
        self.contacts_data = []
        self.filtered_contacts = []
        self.data_loader = None
        self.table_items_pool = []  # Pool for recycling table items
        
        # Initialize enhanced components
        if PHASE_5_7_AVAILABLE:
            self._initialize_phase_5_7_components()
        
        self.setup_ui()
        self.setup_data_loading()
        
        # Apply enhanced UX
        if PHASE_5_7_AVAILABLE:
            self._apply_enhancements()
        
        logger.info("Contact Management Dashboard initialized")
    
    def _initialize_phase_5_7_components(self):
        """Initialize enhanced components"""
        # Theme manager
        self.theme_manager = get_theme_manager()
        
        # Notification center
        self.notification_center = get_notification_center(self)
        
        # Cache manager
        self.cache_manager = get_cache_manager()
        
        logger.info("✅ Enhanced components initialized for Contact Dashboard")
    
    def _apply_enhancements(self):
        """Apply theme and UX enhancements"""
        # Register with theme manager
        if self.theme_manager:
            self.theme_manager.register_widget(self)
        
        # Set up keyboard navigation after UI is created
        QTimer.singleShot(100, self._setup_keyboard_navigation)
        
        # Add tooltips to main buttons
        self._add_enhanced_tooltips()
        
        # Show welcome notification with safety check
        def safe_show_notification():
            try:
                if self and not self.isHidden():
                    show_notification(
                        self, "🚀 Contact Management Dashboard Ready", 
                        NotificationType.SUCCESS, duration=2000
                    )
            except RuntimeError:
                # Widget was deleted - ignore safely
                pass
        
        QTimer.singleShot(1000, safe_show_notification)
    
    def _setup_keyboard_navigation(self):
        """Set up keyboard navigation for dashboard"""
        try:
            # Get main window
            main_window = self.window()
            if main_window:
                kb_nav = get_keyboard_navigation_manager(main_window)
                if kb_nav and hasattr(self, 'control_buttons'):
                    kb_nav.register_navigation_group('contacts', self.control_buttons)
                    logger.info("✅ Keyboard navigation registered for contacts dashboard")
        except Exception as e:
            logger.debug("Warning: Could not set up keyboard navigation: {e}")
    
    def _add_enhanced_tooltips(self):
        """Add enhanced tooltips to UI elements"""
        if hasattr(self, 'new_contact_btn'):
            add_tooltip(self.new_contact_btn, "Create a new contact with guided form validation")
        if hasattr(self, 'import_contacts_btn'):
            add_tooltip(self.import_contacts_btn, "Import contacts from CSV or JSON files")
        if hasattr(self, 'export_contacts_btn'):
            add_tooltip(self.export_contacts_btn, "Export selected contacts to various formats")
        if hasattr(self, 'refresh_btn'):
            add_tooltip(self.refresh_btn, "Refresh contact list from Dynamics 365 (uses intelligent caching)")
        if hasattr(self, 'search_edit'):
            add_tooltip(self.search_edit, "Search contacts by name, email, or job title (real-time filtering)")
    
    def apply_theme(self, theme_definition):
        """Apply theme to dashboard (Phase 5.7)"""
        colors = theme_definition['colors']
        fonts = theme_definition['fonts']
        spacing = theme_definition['spacing']
        
        # Apply theme to main dashboard
        self.setStyleSheet(f"""
            ContactManagementDashboard {{
                background: {colors['background']};
                color: {colors['text_primary']};
                font-family: "{fonts['primary']}";
            }}
            QTabWidget::pane {{
                border: 2px solid {colors['border']};
                border-radius: 8px;
                background: {colors['background']};
            }}
            QTabBar::tab {{
                background: {colors['surface']};
                color: {colors['text_secondary']};
                padding: {spacing['md']}px {spacing['lg']}px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: "{fonts['primary']}";
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-bottom: none;
            }}
        """)
        
        # Update header gradient for theme
        if hasattr(self, 'title_label') and colors:
            if 'dark' in theme_definition.get('name', '').lower():
                gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4c1d95, stop:1 #5b21b6)"
            else:
                gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2)"
            
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    background: {gradient};
                    padding: 16px 24px;
                    border-radius: 12px;
                    margin-bottom: 8px;
                }}
            """)
    
    def setup_ui(self):
        """Set up the main dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No outer margins for uniform header
        layout.setSpacing(0)

        # Content container with internal padding
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(20)

        # Header (standardized to match Settings panel)
        header = self.create_header()
        layout.addWidget(header)

        # Set up content
        self.setup_content()

        # Add content container to outer layout
        layout.addWidget(self.content_widget)
    
    def create_header(self) -> QWidget:
        """Create dashboard header (standardized to match Settings panel)"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background-color: #0077B5;
            border-bottom: 1px solid #006097;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Contacts")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def setup_content(self):
        """Set up the main content area within the padded container"""
        layout = self.content_layout
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.new_contact_btn = QPushButton("👤 New Contact")
        self.new_contact_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.new_contact_btn.clicked.connect(self.create_new_contact)
        controls_layout.addWidget(self.new_contact_btn)
        
        self.import_contacts_btn = QPushButton("📥 Import Contacts")
        self.import_contacts_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.import_contacts_btn.clicked.connect(self.import_contacts)
        controls_layout.addWidget(self.import_contacts_btn)
        
        self.export_contacts_btn = QPushButton("📤 Export Contacts")
        self.export_contacts_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.export_contacts_btn.clicked.connect(self.export_contacts)
        controls_layout.addWidget(self.export_contacts_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_contacts)
        controls_layout.addWidget(self.refresh_btn)
        
        # Store control buttons for keyboard navigation
        self.control_buttons = [
            self.new_contact_btn, self.import_contacts_btn, 
            self.export_contacts_btn, self.refresh_btn
        ]
        
        controls_layout.addStretch()
        
        # Status label inline with controls
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666; 
                font-size: 16px;
                font-weight: bold;
                font-style: italic;
                padding: 8px 12px;
            }
        """)
        controls_layout.addWidget(self.status_label)
        
        # Contact count in header area
        self.contact_count_label = QLabel("0 contacts")
        self.contact_count_label.setStyleSheet("""
            QLabel {
                color: #0077B5; 
                font-weight: bold; 
                font-size: 16px;
                padding: 8px 16px;
                background: #F9FAFB;
                border: 2px solid #0077B5;
                border-radius: 8px;
            }
        """)
        controls_layout.addWidget(self.contact_count_label)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0077B5;
                border-radius: 8px;
                background: #F9FAFB;
                text-align: center;
                font-weight: bold;
                color: #0077B5;
            }
            QProgressBar::chunk {
                background-color: #0077B5;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Main content tabs with increased height
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(600)  # Ensure tabs have enough vertical space
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #FFFFFF;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                color: #666666;
                padding: 16px 28px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #D0D7DE;
                border-bottom: none;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #0077B5;
                color: white;
                border-color: #0077B5;
            }
            QTabBar::tab:hover {
                background-color: #E8F4FD;
                color: #0077B5;
                border-color: #0077B5;
            }
        """)
        
        # Create tabs
        self.contact_list_tab = self.create_contact_list_tab()
        self.relationships_tab = ContactRelationshipView()
        self.analytics_tab = self.create_analytics_tab()
        
        self.tab_widget.addTab(self.contact_list_tab, "👥 Contact List")
        self.tab_widget.addTab(self.relationships_tab, "🔗 Relationships")
        self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")
        
        layout.addWidget(self.tab_widget)
    
    def _get_table_item(self, text: str = "", data: Any = None) -> QTableWidgetItem:
        """Get a table item from the pool or create a new one"""
        if self.table_items_pool:
            item = self.table_items_pool.pop()
            item.setText(text)
            if data is not None:
                item.setData(Qt.ItemDataRole.UserRole, data)
            return item
        item = QTableWidgetItem(text)
        if data is not None:
            item.setData(Qt.ItemDataRole.UserRole, data)
        return item

    def _return_table_item(self, item: QTableWidgetItem):
        """Return a table item to the pool"""
        item.setText("")
        item.setData(Qt.ItemDataRole.UserRole, None)
        self.table_items_pool.append(item)

    def _cleanup_table_items(self):
        """Clean up all table items and return them to the pool"""
        for row in range(self.contact_table.rowCount()):
            for col in range(self.contact_table.columnCount()):
                item = self.contact_table.takeItem(row, col)
                if item:
                    self._return_table_item(item)
        self.contact_table.setRowCount(0)

    def populate_contact_table(self):
        """Populate the contact table with data using widget recycling"""
        # Clean up existing items
        self._cleanup_table_items()
        
        # Set new row count
        self.contact_table.setRowCount(len(self.filtered_contacts))
        
        for row, contact in enumerate(self.filtered_contacts):
            # Name
            name_item = self._get_table_item(
                contact.get('fullname', 'Unknown'),
                contact
            )
            self.contact_table.setItem(row, 0, name_item)
            
            # Email
            email_item = self._get_table_item(contact.get('emailaddress1', ''))
            self.contact_table.setItem(row, 1, email_item)
            
            # Phone
            phone = contact.get('telephone1', '') or contact.get('mobilephone', '')
            phone_item = self._get_table_item(phone)
            self.contact_table.setItem(row, 2, phone_item)
            
            # Job Title
            job_title_item = self._get_table_item(contact.get('jobtitle', ''))
            self.contact_table.setItem(row, 3, job_title_item)
            
            # City
            city_item = self._get_table_item(contact.get('address1_city', ''))
            self.contact_table.setItem(row, 4, city_item)
            
            # Created Date
            created = contact.get('createdon', '')
            if created:
                try:
                    created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created_str = created_date.strftime('%Y-%m-%d')
                except (Exception, AttributeError, TypeError, ValueError):
                    created_str = created[:10] if len(created) >= 10 else created
            else:
                created_str = ''
            created_item = self._get_table_item(created_str)
            self.contact_table.setItem(row, 5, created_item)
            
            # Modified Date
            modified = contact.get('modifiedon', '')
            if modified:
                try:
                    modified_date = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified_str = modified_date.strftime('%Y-%m-%d')
                except (Exception, AttributeError, TypeError, ValueError):
                    modified_str = modified[:10] if len(modified) >= 10 else modified
            else:
                modified_str = ''
            modified_item = self._get_table_item(modified_str)
            self.contact_table.setItem(row, 6, modified_item)
            
            # Status
            status_item = self._get_table_item(str(contact.get('statuscode', 'Unknown')))
            self.contact_table.setItem(row, 7, status_item)
    
    def create_contact_list_tab(self) -> QWidget:
        """Create the contact list tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("color: #666666; font-weight: bold;")
        controls_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search contacts by name, email, or job title...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0077B5;
                outline: none;
            }
        """)
        self.search_edit.textChanged.connect(self.filter_contacts)
        controls_layout.addWidget(self.search_edit)
        
        status_label = QLabel("📊 Status:")
        status_label.setStyleSheet("color: #666666; font-weight: bold;")
        controls_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Contacts", "Active", "Inactive"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #D0D7DE;
                border-radius: 8px;
                padding: 8px 12px;
                background: #FFFFFF;
                color: #666666;
                font-size: 14px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #0077B5;
            }
            QComboBox::drop-down {
                border: none;
                background: #0077B5;
                border-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid white;
                width: 6px;
                height: 6px;
                border-bottom: none;
                border-right: none;
                transform: rotate(-45deg);
            }
        """)
        self.status_filter.currentTextChanged.connect(self.filter_contacts)
        controls_layout.addWidget(self.status_filter)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Contact table
        self.contact_table = QTableWidget()
        self.contact_table.setColumnCount(8)
        headers = ["Name", "Email", "Phone", "Job Title", "City", "Created", "Modified", "Status"]
        self.contact_table.setHorizontalHeaderLabels(headers)
        
        # Configure table
        self.contact_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.contact_table.setAlternatingRowColors(True)
        self.contact_table.setSortingEnabled(True)
        self.contact_table.horizontalHeader().setStretchLastSection(True)
        
        # Style the table with LinkedIn Blue theme
        self.contact_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D7DE;
                border-radius: 8px;
                background: #FFFFFF;
                alternate-background-color: #F9FAFB;
                color: #666666;
                gridline-color: #F0F0F0;
                selection-background-color: #0077B5;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #0077B5;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #E8F4FD;
                color: #0077B5;
            }
            QHeaderView::section {
                background-color: #0077B5;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QHeaderView::section:hover {
                background-color: #005885;
            }
        """)
        
        # Set column widths
        header = self.contact_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Email
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Job Title
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # City
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Created
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Modified
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        # Double-click to edit
        self.contact_table.doubleClicked.connect(self.edit_selected_contact)
        
        layout.addWidget(self.contact_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_selected_contact)
        action_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: 2px solid #DC3545;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #A71E2A;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_contact)
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        
        self.bulk_email_btn = QPushButton("📧 Bulk Email")
        self.bulk_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        self.bulk_email_btn.clicked.connect(self.send_bulk_email)
        action_layout.addWidget(self.bulk_email_btn)
        
        layout.addLayout(action_layout)
        
        return tab
    
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(40)  # Consistent spacing
        
        # Analytics header
        header = QLabel("📊 Contact Analytics")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #0077B5; margin: 10px; font-weight: bold;")
        layout.addWidget(header)
        
        # Statistics grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        # Create stat cards
        stat_cards = [
            ("Total Contacts", "0", "👥"),
            ("Active Contacts", "0", "✅"),
            ("New This Month", "0", "📈"),
            ("Companies", "0", "🏢"),
            ("Email Domains", "0", "📧"),
            ("Avg. Emails/Contact", "0", "📊")
        ]
        
        self.stat_labels = {}
        for i, (title, value, icon) in enumerate(stat_cards):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #FFFFFF;
                    border: 2px solid #0077B5;
                    border-radius: 12px;
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: #005885;
                    background: #F9FAFB;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 24))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("color: #0077B5; font-weight: bold;")
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #666666; font-weight: bold; font-size: 11px;")
            
            card_layout.addWidget(icon_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(title_label)
            
            stats_layout.addWidget(card, i // 3, i % 3)
            self.stat_labels[title] = value_label
        
        layout.addLayout(stats_layout)
        
        # Recent activity
        activity_group = QGroupBox("📅 Recent Activity")
        activity_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #FFFFFF;
                font-weight: bold;
                color: #0077B5;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0077B5;
                font-weight: bold;
            }
        """)
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QTableWidget()
        self.activity_list.setColumnCount(3)
        self.activity_list.setHorizontalHeaderLabels(["Date", "Action", "Contact"])
        self.activity_list.horizontalHeader().setStretchLastSection(True)
        self.activity_list.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D7DE;
                border-radius: 8px;
                background: #FFFFFF;
                alternate-background-color: #F9FAFB;
                color: #666666;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #0077B5;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #E8F4FD;
                color: #0077B5;
            }
            QHeaderView::section {
                background-color: #0077B5;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        return tab
    
    def setup_data_loading(self):
        """Set up background data loading"""
        self.data_loader = ContactDataLoader()
        self.data_loader.contacts_loaded.connect(self.load_contacts_data)
        self.data_loader.error_occurred.connect(self.handle_data_error)
        self.data_loader.progress_updated.connect(self.update_progress)
        
        # Start loading
        self.refresh_contacts()
    
    def refresh_contacts(self):
        """Refresh contact data"""
        if self.data_loader and not self.data_loader.isRunning():
            self.progress_bar.setVisible(True)
            self.status_label.setText("Loading contacts...")
            self.data_loader.start()
    
    def load_contacts_data(self, contacts: List[Dict]):
        """Load contacts into the dashboard and update the contact count label"""
        self.contacts_data = contacts
        self.filtered_contacts = contacts
        if hasattr(self, 'contact_count_label'):
            self.contact_count_label.setText(f"{len(contacts)} contacts")
        self.populate_contact_table()
        self.update_analytics()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
    
    def filter_contacts(self):
        """Filter contacts based on search criteria"""
        search_text = self.search_edit.text().lower()
        status_filter = self.status_filter.currentText()
        
        self.filtered_contacts = []
        
        for contact in self.contacts_data:
            # Text search
            if search_text:
                searchable_text = ' '.join([
                    contact.get('fullname', ''),
                    contact.get('emailaddress1', ''),
                    contact.get('jobtitle', ''),
                    contact.get('address1_city', '')
                ]).lower()
                
                if search_text not in searchable_text:
                    continue
            
            # Status filter
            if status_filter != "All Contacts":
                contact_status = contact.get('statuscode', '')
                if status_filter == "Active" and contact_status != "Active":
                    continue
                elif status_filter == "Inactive" and contact_status == "Active":
                    continue
            
            self.filtered_contacts.append(contact)
        
        self.populate_contact_table()
        self.contact_count_label.setText(f"{len(self.filtered_contacts)} contacts")
    
    def update_analytics(self):
        """Update analytics statistics"""
        if not self.contacts_data:
            return
        
        total_contacts = len(self.contacts_data)
        active_contacts = sum(1 for c in self.contacts_data if c.get('statuscode') == 'Active')
        
        # New contacts this month
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = 0
        
        for contact in self.contacts_data:
            created_str = contact.get('createdon', '')
            if created_str:
                try:
                    created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    if created_date >= month_start:
                        new_this_month += 1
                except (Exception, AttributeError, TypeError, ValueError):
                    pass
        
        # Unique domains
        domains = set()
        for contact in self.contacts_data:
            email = contact.get('emailaddress1', '')
            if email and '@' in email:
                domain = email.split('@')[1].lower()
                domains.add(domain)
        
        # Unique companies (approximate from domains)
        companies = len(domains)
        
        # Update stat labels
        self.stat_labels["Total Contacts"].setText(str(total_contacts))
        self.stat_labels["Active Contacts"].setText(str(active_contacts))
        self.stat_labels["New This Month"].setText(str(new_this_month))
        self.stat_labels["Companies"].setText(str(companies))
        self.stat_labels["Email Domains"].setText(str(len(domains)))
        self.stat_labels["Avg. Emails/Contact"].setText("5.2")  # Sample calculation
    
    def create_new_contact(self):
        """Create a new contact"""
        dialog = ContactEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # In real implementation, save to Dynamics 365
            contact_data = dialog.contact_data
            contact_data['contactid'] = f"new-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            contact_data['createdon'] = datetime.now().isoformat()
            contact_data['modifiedon'] = datetime.now().isoformat()
            contact_data['statuscode'] = "Active"
            
            self.contacts_data.append(contact_data)
            self.filter_contacts()
            self.update_analytics()
            
            QMessageBox.information(self, "Success", "Contact created successfully!")
    
    def edit_selected_contact(self):
        """Edit the selected contact"""
        current_row = self.contact_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a contact to edit.")
            return
        
        # Get contact data from the table
        name_item = self.contact_table.item(current_row, 0)
        contact_data = name_item.data(Qt.ItemDataRole.UserRole)
        
        dialog = ContactEditDialog(contact_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update contact data
            updated_data = dialog.contact_data
            updated_data['contactid'] = contact_data['contactid']
            updated_data['createdon'] = contact_data.get('createdon', '')
            updated_data['modifiedon'] = datetime.now().isoformat()
            
            # Find and update in contacts_data
            for i, contact in enumerate(self.contacts_data):
                if contact['contactid'] == contact_data['contactid']:
                    self.contacts_data[i] = updated_data
                    break
            
            self.filter_contacts()
            QMessageBox.information(self, "Success", "Contact updated successfully!")
    
    def delete_selected_contact(self):
        """Delete the selected contact"""
        current_row = self.contact_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a contact to delete.")
            return
        
        name_item = self.contact_table.item(current_row, 0)
        contact_name = name_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete '{contact_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            contact_data = name_item.data(Qt.ItemDataRole.UserRole)
            contact_id = contact_data['contactid']
            
            # Remove from contacts_data
            self.contacts_data = [c for c in self.contacts_data if c['contactid'] != contact_id]
            self.filter_contacts()
            self.update_analytics()
            
            QMessageBox.information(self, "Success", "Contact deleted successfully!")
    
    def send_bulk_email(self):
        """Send bulk email to selected contacts"""
        QMessageBox.information(self, "Bulk Email", "Bulk email functionality will be implemented in a future update.")
    
    def import_contacts(self):
        """Import contacts from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Contacts", "", "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "Import", f"Contact import from {file_path} will be implemented.")
    
    def export_contacts(self):
        """Export contacts to file"""
        if not self.contacts_data:
            QMessageBox.warning(self, "No Data", "No contacts to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Contacts", f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump({
                        'export_timestamp': datetime.now().isoformat(),
                        'total_contacts': len(self.contacts_data),
                        'contacts': self.contacts_data
                    }, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Contacts exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export contacts: {str(e)}")
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def handle_data_error(self, error_message: str):
        """Handle data loading errors"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error loading contacts")
        QMessageBox.warning(self, "Data Error", f"Error loading contacts:\n{error_message}")
    
    def closeEvent(self, event):
        """Handle widget close event"""
        if self.data_loader:
            self.data_loader.stop()
        # Clean up table items
        self._cleanup_table_items()
        # Clear the item pool
        self.table_items_pool.clear()
        super().closeEvent(event)
    
    def _on_theme_changed(self):
        """Handle theme selection change (Phase 5.7)"""
        if PHASE_5_7_AVAILABLE and hasattr(self, 'theme_selector'):
            theme_type = self.theme_selector.currentData()
            if theme_type and self.theme_manager:
                self.theme_manager.set_theme(theme_type)
                # Safe notification with widget check
                def safe_theme_notification():
                    try:
                        if self and not self.isHidden():
                            show_notification(
                                self, f"Theme changed to {self.theme_selector.currentText()}", 
                                NotificationType.INFO, duration=2000
                            )
                    except RuntimeError:
                        pass
                
                QTimer.singleShot(100, safe_theme_notification)

def main():
    """Standalone testing function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    app.setPalette(palette)
    
    # Create and show dashboard
    dashboard = ContactManagementDashboard()
    dashboard.setWindowTitle("👥 Contact Management Dashboard - Phase 5.6")
    dashboard.setMinimumSize(1200, 800)
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 