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
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QDate, QSortFilterProxyModel, QSettings
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
    from dynamics_data import DynamicsData
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


def get_contacts_with_oauth2(tenant_id: str, client_id: str, client_secret: str, org_url: str) -> List[Dict]:
    """
    Get contacts directly using OAuth2 authentication (same method as Configuration Manager)
    This is a standalone function to avoid circular imports.
    """
    try:
        import requests
        import json
        
        # Step 1: Get OAuth2 access token for Dynamics 365
        # Use v1.0 endpoint for Dynamics 365 which supports the resource parameter
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
        
        # Extract the base domain from org_url to construct the correct resource
        if org_url.startswith('http'):
            base_domain = org_url.split('//')[1].split('/')[0]
        else:
            base_domain = org_url.split('/')[0]
        
        # Use OAuth v1.0 parameters for Dynamics 365 authentication
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': f"https://{base_domain}"  # Resource parameter for Dynamics 365
        }
        
        logger.info(f"🔐 Using OAuth v1.0 endpoint for Dynamics 365")
        logger.info(f"🔐 Using resource: https://{base_domain}")
        
        logger.info("🔐 Getting OAuth2 access token...")
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code != 200:
            logger.error(f"❌ Failed to get access token: {token_response.status_code}")
            return []
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.error("❌ No access token received")
            return []
        
        logger.info("✅ OAuth2 access token obtained")
        
        # Step 2: Get contacts from Dynamics 365
        # Use the organization URL to construct the API endpoint
        if not org_url.startswith('http'):
            org_url = f"https://{org_url}"
        if not org_url.endswith('/api/data/v9.2'):
            org_url = f"{org_url}/api/data/v9.2"
        
        contacts_url = f"{org_url}/contacts"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0'
        }
        
        # Request specific fields we need for the contact table
        params = {
            '$select': 'contactid,fullname,firstname,lastname,emailaddress1,emailaddress2,emailaddress3,telephone1,mobilephone,jobtitle,address1_city,address1_stateorprovince,address1_country,createdon,modifiedon,statecode,statuscode',
            '$top': 100  # Limit to first 100 contacts for performance
        }
        
        logger.info("📞 Fetching contacts from Dynamics 365...")
        contacts_response = requests.get(contacts_url, headers=headers, params=params, timeout=30)
        
        if contacts_response.status_code == 200:
            contacts_data = contacts_response.json()
            contacts = contacts_data.get('value', [])
            logger.info(f"✅ Successfully retrieved {len(contacts)} contacts from Dynamics 365")
            return contacts
        elif contacts_response.status_code == 403:
            error_data = contacts_response.json() if contacts_response.content else {}
            error_message = error_data.get('error', {}).get('message', 'Permission denied')
            logger.error(f"❌ Permission denied (403): {error_message}")
            logger.error("🔧 This means your app registration needs additional permissions:")
            logger.error("   1. Go to Azure Portal → App registrations → Your app")
            logger.error("   2. Click 'API permissions'")
            logger.error("   3. Add 'Dynamics CRM' → 'user_impersonation' permission")
            logger.error("   4. Grant admin consent for the organization")
            logger.error("   5. Or use a service principal with proper Dynamics 365 roles")
            logger.warning("⚠️ Authentication succeeded but permissions insufficient, falling back to sample data")
            return []
        else:
            logger.error(f"❌ Failed to get contacts: {contacts_response.status_code} - {contacts_response.text}")
            return []
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout connecting to Dynamics 365")
        return []
    except requests.exceptions.ConnectionError:
        logger.error("❌ Network connection error to Dynamics 365")
        return []
    except Exception as e:
        logger.error(f"❌ Error fetching contacts: {str(e)}")
        return []

class ContactDataLoader(QThread):
    """Background thread for loading contact data with performance optimization"""
    contacts_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.contact_creator = None
        self.oauth2_credentials = None
        
        # Initialize cache manager
        if PHASE_5_7_AVAILABLE:
            self.cache_manager = get_cache_manager()
        
        # Load credentials from QSettings (where Configuration Manager saves them)
        settings = QSettings("PSTtoDynamics", "Configuration")
        
        # Check if we have saved credentials
        tenant_id = settings.value("auth/tenant_id", "")
        client_id = settings.value("auth/client_id", "")
        client_secret = settings.value("auth/client_secret", "")
        org_url = settings.value("auth/org_url", "")
        
        if tenant_id and client_id and client_secret and org_url:
            logger.info("✅ Found saved OAuth2 credentials in QSettings")
            self.oauth2_credentials = {
                'tenant_id': tenant_id,
                'client_id': client_id,
                'client_secret': client_secret,
                'org_url': org_url
            }
        else:
            logger.warning("⚠️ No saved OAuth2 credentials found in QSettings")
    
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
            
            # Try OAuth2 authentication first (same method as Configuration Manager)
            if self.oauth2_credentials:
                self.progress_updated.emit(20, "Authenticating with OAuth2...")
                
                self.progress_updated.emit(40, "Fetching contacts...")
                contacts = get_contacts_with_oauth2(
                    self.oauth2_credentials['tenant_id'],
                    self.oauth2_credentials['client_id'],
                    self.oauth2_credentials['client_secret'],
                    self.oauth2_credentials['org_url']
                )
                
                if contacts:
                    # Phase 5.7: Cache the results
                    if PHASE_5_7_AVAILABLE:
                        self.cache_manager.put("contacts_data", contacts)
                    
                    self.progress_updated.emit(100, f"✅ Live contacts loaded from Dynamics 365")
                    self.contacts_loaded.emit(contacts)
                    return
                else:
                    logger.warning("⚠️ Authentication succeeded but permissions insufficient, falling back to sample data")
                    # Emit a signal to show user-friendly permission guidance
                    self.error_occurred.emit("PERMISSIONS_NEEDED")
            
            # Fallback to sample contacts
            self.progress_updated.emit(60, "Generating sample data...")
            sample_contacts = self._generate_sample_contacts()
            
            # Phase 5.7: Cache sample data too
            if PHASE_5_7_AVAILABLE:
                self.cache_manager.put("contacts_data", sample_contacts)
            
            self.progress_updated.emit(100, "📋 Sample contacts loaded")
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
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['text_primary']};
            }}
        """)
    
    def setup_ui(self):
        """Set up the contact edit dialog UI"""
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        brand_primary = colors.get('brand_primary', '#0077B5')
        ui_surface = colors.get('ui_surface', '#FFFFFF')
        ui_border = colors.get('ui_border', '#D0D7DE')
        text_secondary = colors.get('text_secondary', '#666666')
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Contact Information")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                color: {text_inverse};
                background-color: {brand_primary};
                padding: 12px 24px;
                border-radius: 8px;
                margin-bottom: 8px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {ui_surface};
            }}
        """)
        scroll_widget = QWidget()
        form_layout = QVBoxLayout(scroll_widget)
        form_layout.setSpacing(20)
        
        # Basic Information
        basic_group = QGroupBox("👤 Basic Information")
        basic_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {brand_primary};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {ui_surface};
                font-weight: bold;
                color: {brand_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {brand_primary};
                font-weight: bold;
            }}
        """)
        basic_layout = QFormLayout(basic_group)
        
        # Create input field style
        input_style = f"""
            QLineEdit {{
                border: 2px solid {ui_border};
                border-radius: 8px;
                padding: 8px 12px;
                background: {ui_surface};
                color: {text_secondary};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {brand_primary};
                outline: none;
            }}
        """
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Enter first name...")
        self.first_name_edit.setStyleSheet(input_style)
        basic_layout.addRow("First Name:", self.first_name_edit)
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Enter last name...")
        self.last_name_edit.setStyleSheet(input_style)
        basic_layout.addRow("Last Name:", self.last_name_edit)
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Auto-generated or custom...")
        self.full_name_edit.setStyleSheet(input_style)
        basic_layout.addRow("Full Name:", self.full_name_edit)
        
        self.job_title_edit = QLineEdit()
        self.job_title_edit.setPlaceholderText("Enter job title...")
        self.job_title_edit.setStyleSheet(input_style)
        basic_layout.addRow("Job Title:", self.job_title_edit)
        
        form_layout.addWidget(basic_group)
        
        # Contact Information
        contact_group = QGroupBox("📧 Contact Information")
        contact_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {brand_primary};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {ui_surface};
                font-weight: bold;
                color: {brand_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {brand_primary};
                font-weight: bold;
            }}
        """)
        contact_layout = QFormLayout(contact_group)
        
        self.email1_edit = QLineEdit()
        self.email1_edit.setPlaceholderText("Primary email address...")
        self.email1_edit.setStyleSheet(input_style)
        contact_layout.addRow("Primary Email:", self.email1_edit)
        
        self.email2_edit = QLineEdit()
        self.email2_edit.setPlaceholderText("Secondary email address...")
        self.email2_edit.setStyleSheet(input_style)
        contact_layout.addRow("Secondary Email:", self.email2_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Business phone number...")
        self.phone_edit.setStyleSheet(input_style)
        contact_layout.addRow("Business Phone:", self.phone_edit)
        
        self.mobile_edit = QLineEdit()
        self.mobile_edit.setPlaceholderText("Mobile phone number...")
        self.mobile_edit.setStyleSheet(input_style)
        contact_layout.addRow("Mobile Phone:", self.mobile_edit)
        
        form_layout.addWidget(contact_group)
        
        # Address Information
        address_group = QGroupBox("🏢 Address Information")
        address_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {brand_primary};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {ui_surface};
                font-weight: bold;
                color: {brand_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {brand_primary};
                font-weight: bold;
            }}
        """)
        address_layout = QFormLayout(address_group)
        
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("City...")
        self.city_edit.setStyleSheet(input_style)
        address_layout.addRow("City:", self.city_edit)
        
        self.state_edit = QLineEdit()
        self.state_edit.setPlaceholderText("State/Province...")
        self.state_edit.setStyleSheet(input_style)
        address_layout.addRow("State/Province:", self.state_edit)
        
        self.country_edit = QLineEdit()
        self.country_edit.setPlaceholderText("Country...")
        self.country_edit.setStyleSheet(input_style)
        address_layout.addRow("Country:", self.country_edit)
        
        form_layout.addWidget(address_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Get button colors
        brand_primary_hover = colors.get('brand_primaryHover', '#005885')
        brand_primary_active = colors.get('brand_primaryActive', '#004A70')
        ui_button_dark = colors.get('ui_buttonDark', '#6C757D')
        ui_button_darker = colors.get('ui_buttonDarker', '#5A6268')
        text_dark = colors.get('text_dark', '#495057')
        
        self.save_button = QPushButton("💾 Save Contact")
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand_primary};
                color: {text_inverse};
                border: 2px solid {brand_primary};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {brand_primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        self.save_button.clicked.connect(self.accept_contact)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ui_button_dark};
                color: {text_inverse};
                border: 2px solid {ui_button_dark};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ui_button_darker};
            }}
            QPushButton:pressed {{
                background-color: {text_dark};
            }}
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
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        brand_primary = colors.get('brand_primary', '#0077B5')
        ui_surface = colors.get('ui_surface', '#FFFFFF')
        ui_border = colors.get('ui_border', '#D0D7DE')
        ui_surfaceAlt = colors.get('ui_surfaceAlt', '#F9FAFB')
        text_secondary = colors.get('text_secondary', '#666666')
        ui_gridline = colors.get('ui_gridline', '#F0F0F0')
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        ui_surfaceHoverAlt = colors.get('ui_surfaceHoverAlt', '#E8F4FD')
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔗 Contact Relationships & Email History")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {brand_primary}; margin: 10px; font-weight: bold;")
        layout.addWidget(header)
        
        # Splitter for relationship tree and email history
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Relationship tree
        relationship_group = QGroupBox("🌐 Contact Network")
        relationship_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {brand_primary};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {ui_surface};
                font-weight: bold;
                color: {brand_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {brand_primary};
                font-weight: bold;
            }}
        """)
        relationship_layout = QVBoxLayout(relationship_group)
        
        self.relationship_tree = QTreeWidget()
        self.relationship_tree.setHeaderLabels(["Contact", "Relationship", "Emails", "Last Contact"])
        self.relationship_tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid {ui_border};
                border-radius: 8px;
                background: {ui_surface};
                alternate-background-color: {ui_surfaceAlt};
                color: {text_secondary};
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {ui_gridline};
            }}
            QTreeWidget::item:selected {{
                background-color: {brand_primary};
                color: {text_inverse};
            }}
            QTreeWidget::item:hover {{
                background-color: {ui_surfaceHoverAlt};
                color: {brand_primary};
            }}
        """)
        relationship_layout.addWidget(self.relationship_tree)
        
        splitter.addWidget(relationship_group)
        
        # Email history
        email_group = QGroupBox("📧 Email History")
        email_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {brand_primary};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: {ui_surface};
                font-weight: bold;
                color: {brand_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {brand_primary};
                font-weight: bold;
            }}
        """)
        email_layout = QVBoxLayout(email_group)
        
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["Date", "Subject", "Direction", "Status"])
        self.email_table.horizontalHeader().setStretchLastSection(True)
        self.email_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {ui_border};
                border-radius: 8px;
                background: {ui_surface};
                alternate-background-color: {ui_surfaceAlt};
                color: {text_secondary};
                gridline-color: {ui_gridline};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {ui_gridline};
            }}
            QTableWidget::item:selected {{
                background-color: {brand_primary};
                color: {text_inverse};
            }}
            QTableWidget::item:hover {{
                background-color: {ui_surfaceHoverAlt};
                color: {brand_primary};
            }}
            QHeaderView::section {{
                background-color: {brand_primary};
                color: {text_inverse};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
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
                background: {colors['ui_canvas']};
                color: {colors['text_primary']};
                font-family: "{fonts['primary']}";
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {colors['ui_canvas']};
            }}
            QTabBar::tab {{
                background-color: {colors['ui_surfaceAlt']};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: {colors['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
            }}
            QTabBar::tab:hover {{
                background-color: {colors['border_light']};
                color: {colors['brand_primary']};
            }}
        """)
        
        # Update header for theme consistency
        if hasattr(self, 'title_label') and colors:
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors['text_inverse']};
                    background: {colors['brand_primary']};
                    padding: 12px 24px;
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
        self.content_layout.setContentsMargins(20, 20, 20, 20)
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
        # Get current theme colors
        colors = get_theme_manager().get_theme_definition()['colors']
        
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background-color: {colors['brand_primary']};
            border-bottom: 1px solid {colors['brand_primaryBorder']};
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Contacts")
        title.setStyleSheet(f"""
            color: {colors['text_inverse']};
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def setup_content(self):
        """Set up the main content area within the padded container"""
        layout = self.content_layout
        
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.new_contact_btn = QPushButton("👤 New Contact")
        self.new_contact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['brand_primaryActive']};
            }}
        """)
        self.new_contact_btn.clicked.connect(self.create_new_contact)
        controls_layout.addWidget(self.new_contact_btn)
        
        self.import_contacts_btn = QPushButton("📥 Import Contacts")
        self.import_contacts_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['brand_primaryActive']};
            }}
        """)
        self.import_contacts_btn.clicked.connect(self.import_contacts)
        controls_layout.addWidget(self.import_contacts_btn)
        
        self.export_contacts_btn = QPushButton("📤 Export Contacts")
        self.export_contacts_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['brand_primaryActive']};
            }}
        """)
        self.export_contacts_btn.clicked.connect(self.export_contacts)
        controls_layout.addWidget(self.export_contacts_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['brand_primaryActive']};
            }}
        """)
        self.refresh_btn.clicked.connect(self.refresh_contacts)
        controls_layout.addWidget(self.refresh_btn)
        
        # Store control buttons for keyboard navigation
        self.control_buttons = [
            self.new_contact_btn, self.import_contacts_btn, 
            self.export_contacts_btn, self.refresh_btn
        ]
        
        # Add some space between buttons and status
        controls_layout.addSpacing(20)
        
        # Status label positioned between buttons and contact count for full visibility
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_secondary']}; 
                font-size: 16px;
                font-weight: bold;
                font-style: italic;
                padding: 8px 12px;
                min-width: 180px;
            }}
        """)
        controls_layout.addWidget(self.status_label)
        
        # Add stretch to push contact count to the right
        controls_layout.addStretch()
        
        # Contact count in header area
        self.contact_count_label = QLabel("0 contacts")
        self.contact_count_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['brand_primary']}; 
                font-weight: bold; 
                font-size: 16px;
                padding: 8px 16px;
                background: {colors['ui_surfaceAlt']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
            }}
        """)
        controls_layout.addWidget(self.contact_count_label)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                background: {colors['ui_surfaceAlt']};
                text-align: center;
                font-weight: bold;
                color: {colors['brand_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {colors['brand_primary']};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Main content tabs with increased height
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(600)  # Ensure tabs have enough vertical space
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {colors['ui_canvas']};
            }}
            QTabBar::tab {{
                background-color: {colors['ui_surfaceAlt']};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: {colors['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
            }}
            QTabBar::tab:hover {{
                background-color: {colors['border_light']};
                color: {colors['brand_primary']};
            }}
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
        
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        controls_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search contacts by name, email, or job title...")
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {colors['ui_border']};
                border-radius: 8px;
                padding: 8px 12px;
                background: {colors['ui_surface']};
                color: {colors['text_secondary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors['ui_focus']};
                outline: none;
            }}
        """)
        self.search_edit.textChanged.connect(self.filter_contacts)
        controls_layout.addWidget(self.search_edit)
        
        status_label = QLabel("📊 Status:")
        status_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        controls_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Contacts", "Active", "Inactive"])
        self.status_filter.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid {colors['ui_border']};
                border-radius: 8px;
                padding: 8px 12px;
                background: {colors['ui_surface']};
                color: {colors['text_secondary']};
                font-size: 14px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {colors['ui_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                background: {colors['brand_primary']};
                border-radius: 4px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {colors['text_inverse']};
                width: 6px;
                height: 6px;
                border-bottom: none;
                border-right: none;
                transform: rotate(-45deg);
            }}
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
        self.contact_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {colors['ui_border']};
                border-radius: 8px;
                background: {colors['ui_surface']};
                alternate-background-color: {colors['ui_surfaceAlt']};
                color: {colors['text_secondary']};
                gridline-color: {colors['ui_gridline']};
                selection-background-color: {colors['brand_primary']};
                selection-color: {colors['text_inverse']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {colors['ui_gridline']};
            }}
            QTableWidget::item:selected {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
            }}
            QTableWidget::item:hover {{
                background-color: {colors['ui_surfaceHoverAlt']};
                color: {colors['brand_primary']};
            }}
            QHeaderView::section {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QHeaderView::section:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
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
        
        # Action buttons with dynamic theme colors
        action_layout = QHBoxLayout()
        
        brand_primary_active = colors.get('brand_primaryActive', '#004A70')
        state_error_button = colors.get('state_errorButton', '#DC3545')
        state_error = colors.get('state_error', '#C0392B')
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        self.edit_btn.clicked.connect(self.edit_selected_contact)
        action_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {state_error_button};
                color: {colors['text_inverse']};
                border: 2px solid {state_error_button};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {state_error};
            }}
            QPushButton:pressed {{
                background-color: {state_error};
            }}
        """)
        self.delete_btn.clicked.connect(self.delete_selected_contact)
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        
        self.bulk_email_btn = QPushButton("📧 Bulk Email")
        self.bulk_email_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        self.bulk_email_btn.clicked.connect(self.send_bulk_email)
        action_layout.addWidget(self.bulk_email_btn)
        
        layout.addLayout(action_layout)
        
        return tab
    
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        
        # Analytics header
        header = QLabel("📊 Contact Analytics")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {colors['brand_primary']}; margin: 10px; font-weight: bold;")
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
            card.setStyleSheet(f"""
                QFrame {{
                    background: {colors['ui_surface']};
                    border: 2px solid {colors['brand_primary']};
                    border-radius: 12px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    border-color: {colors['brand_primaryHover']};
                    background: {colors['ui_surfaceAlt']};
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 24))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(f"color: {colors['brand_primary']}; font-weight: bold;")
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold; font-size: 11px;")
            
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
                left: 15px;
                padding: 0 10px 0 10px;
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
        
        if error_message == "PERMISSIONS_NEEDED":
            self.status_label.setText("Using sample data - permissions needed for live data")
            self.show_permissions_guidance_dialog()
        else:
            self.status_label.setText("Error loading contacts")
            QMessageBox.warning(self, "Data Error", f"Error loading contacts:\n{error_message}")
    
    def show_permissions_guidance_dialog(self):
        """Show a helpful dialog explaining how to fix Dynamics 365 permissions"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔧 Dynamics 365 Permissions Setup")
        dialog.setMinimumSize(600, 500)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Header with explanation
        header = QLabel("✅ Authentication Successful - Permissions Configuration Needed")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0077B5; padding: 10px; background: #E8F4F8; border-radius: 5px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Explanation
        explanation = QLabel(
            "🎉 <b>Good news!</b> Your Azure AD authentication is working perfectly and you have a valid access token.<br><br>"
            "💡 The application is currently showing <b>sample data</b> because your app registration needs additional "
            "permissions to access live Dynamics 365 contact data."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("padding: 10px; background: #F0F8FF; border-radius: 5px; line-height: 1.4;")
        layout.addWidget(explanation)
        
        # Instructions
        instructions_text = """
🔧 **To Enable Live Dynamics 365 Data Access:**

**Step 1: Configure App Registration Permissions**
1. Go to Azure Portal (portal.azure.com)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Find your app registration
4. Click on "API permissions"
5. Click "Add a permission"
6. Select "Dynamics CRM"
7. Choose "Delegated permissions"
8. Add "user_impersonation" permission
9. Click "Grant admin consent for [your organization]"

**Step 2: Alternative - Service Principal Method**
1. In your app registration, go to "Certificates & secrets"
2. Ensure you have a valid client secret
3. In Dynamics 365 Admin Center:
   - Go to "Environments" → Your environment
   - Click "Settings" → "Users + permissions" → "Application users"
   - Create new application user with your Client ID
   - Assign appropriate security roles (e.g., "Salesperson" or "System Administrator")

**Step 3: Verify Organization URL**
- Ensure your Organization URL exactly matches your Dynamics 365 environment
- Format: https://[your-org].crm.dynamics.com (no trailing slashes)

**Current Status:**
✅ Azure AD Authentication: Working
✅ Access Token: Valid  
⚠️ Dynamics 365 API Access: Needs permissions
📊 Data Source: Sample data (50 demo contacts)

Once you complete the permission setup, restart the application and your live Dynamics 365 contacts will be displayed automatically!
        """
        
        instructions = QTextEdit()
        instructions.setPlainText(instructions_text)
        instructions.setReadOnly(True)
        instructions.setFont(QFont("Segoe UI", 10))
        instructions.setStyleSheet("""
            QTextEdit {
                background: #FFFFFF;
                border: 1px solid #D0D7DE;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        copy_button = QPushButton("📋 Copy Instructions")
        copy_button.clicked.connect(lambda: self.copy_instructions_to_clipboard(instructions_text))
        copy_button.setStyleSheet("""
            QPushButton {
                background: #0077B5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #005885;
            }
        """)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setDefault(True)
        ok_button.setStyleSheet("""
            QPushButton {
                background: #28A745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1E7E34;
            }
        """)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def copy_instructions_to_clipboard(self, text: str):
        """Copy instructions to clipboard"""
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Instructions copied to clipboard!")
        except Exception:
            pass
    
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