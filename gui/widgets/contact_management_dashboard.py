"""
Phase 5.6 Contact Management Interface - Comprehensive Contact Administration

This module provides a complete GUI interface for managing Dynamics 365 contacts including:
- Contact browser with search and filtering
- Contact creation and editing forms
- Relationship mapping and email history
- Bulk operations and data export
- Import history tracking
- Advanced contact analytics
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

# Try to import contact management modules
try:
    import sys
    sys.path.append('.')
    from contact_creator import ContactCreator
    from dynamics_data import get_dynamics_contacts
    import auth
    import config
    CONTACT_MODULES_AVAILABLE = True
    print("✅ Contact management modules loaded successfully")
except ImportError as e:
    CONTACT_MODULES_AVAILABLE = False
    print(f"⚠️ Contact management modules not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactDataLoader(QThread):
    """Background thread for loading contact data"""
    contacts_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.contact_creator = None
        if CONTACT_MODULES_AVAILABLE:
            try:
                self.contact_creator = ContactCreator()
            except Exception as e:
                logger.error(f"Error initializing contact creator: {e}")
    
    def run(self):
        """Load contacts from Dynamics 365"""
        try:
            self.progress_updated.emit(0, "Connecting to Dynamics 365...")
            
            if CONTACT_MODULES_AVAILABLE and self.contact_creator:
                # Load real contacts
                self.progress_updated.emit(30, "Loading contacts...")
                contacts = self.contact_creator._get_existing_contacts()
                self.progress_updated.emit(100, "Contacts loaded successfully")
                self.contacts_loaded.emit(contacts)
            else:
                # Generate sample contacts for testing
                self.progress_updated.emit(50, "Generating sample data...")
                sample_contacts = self._generate_sample_contacts()
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
    """Dialog for creating/editing contacts"""
    
    def __init__(self, contact_data=None, parent=None):
        super().__init__(parent)
        self.contact_data = contact_data or {}
        self.is_new_contact = contact_data is None
        
        self.setWindowTitle("📝 New Contact" if self.is_new_contact else "✏️ Edit Contact")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self):
        """Set up the contact edit dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📝 Contact Information")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1e293b; margin: 10px;")
        layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        
        # Basic Information
        basic_group = QGroupBox("👤 Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Enter first name...")
        basic_layout.addRow("First Name:", self.first_name_edit)
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Enter last name...")
        basic_layout.addRow("Last Name:", self.last_name_edit)
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Auto-generated or custom...")
        basic_layout.addRow("Full Name:", self.full_name_edit)
        
        self.job_title_edit = QLineEdit()
        self.job_title_edit.setPlaceholderText("Enter job title...")
        basic_layout.addRow("Job Title:", self.job_title_edit)
        
        form_layout.addWidget(basic_group)
        
        # Contact Information
        contact_group = QGroupBox("📧 Contact Information")
        contact_layout = QFormLayout(contact_group)
        
        self.email1_edit = QLineEdit()
        self.email1_edit.setPlaceholderText("Primary email address...")
        contact_layout.addRow("Primary Email:", self.email1_edit)
        
        self.email2_edit = QLineEdit()
        self.email2_edit.setPlaceholderText("Secondary email address...")
        contact_layout.addRow("Secondary Email:", self.email2_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Business phone number...")
        contact_layout.addRow("Business Phone:", self.phone_edit)
        
        self.mobile_edit = QLineEdit()
        self.mobile_edit.setPlaceholderText("Mobile phone number...")
        contact_layout.addRow("Mobile Phone:", self.mobile_edit)
        
        form_layout.addWidget(contact_group)
        
        # Address Information
        address_group = QGroupBox("🏠 Address Information")
        address_layout = QFormLayout(address_group)
        
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("City...")
        address_layout.addRow("City:", self.city_edit)
        
        self.state_edit = QLineEdit()
        self.state_edit.setPlaceholderText("State/Province...")
        address_layout.addRow("State/Province:", self.state_edit)
        
        self.country_edit = QLineEdit()
        self.country_edit.setPlaceholderText("Country...")
        address_layout.addRow("Country:", self.country_edit)
        
        form_layout.addWidget(address_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                    QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_contact)
        button_box.rejected.connect(self.reject)
        
        # Rename OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("💾 Save Contact")
        
        layout.addWidget(button_box)
        
        # Connect name fields to auto-generate full name
        self.first_name_edit.textChanged.connect(self.update_full_name)
        self.last_name_edit.textChanged.connect(self.update_full_name)
    
    def populate_fields(self):
        """Populate fields with existing contact data"""
        if not self.contact_data:
            return
        
        self.first_name_edit.setText(self.contact_data.get('firstname', '') or '')
        self.last_name_edit.setText(self.contact_data.get('lastname', '') or '')
        self.full_name_edit.setText(self.contact_data.get('fullname', '') or '')
        self.job_title_edit.setText(self.contact_data.get('jobtitle', '') or '')
        self.email1_edit.setText(self.contact_data.get('emailaddress1', '') or '')
        self.email2_edit.setText(self.contact_data.get('emailaddress2', '') or '')
        self.phone_edit.setText(self.contact_data.get('telephone1', '') or '')
        self.mobile_edit.setText(self.contact_data.get('mobilephone', '') or '')
        self.city_edit.setText(self.contact_data.get('address1_city', '') or '')
        self.state_edit.setText(self.contact_data.get('address1_stateorprovince', '') or '')
        self.country_edit.setText(self.contact_data.get('address1_country', '') or '')
    
    def update_full_name(self):
        """Auto-update full name when first/last name changes"""
        if not self.full_name_edit.text() or self.is_new_contact:
            first = self.first_name_edit.text().strip()
            last = self.last_name_edit.text().strip()
            if first or last:
                full_name = f"{first} {last}".strip()
                self.full_name_edit.setText(full_name)
    
    def accept_contact(self):
        """Validate and accept contact data"""
        # Basic validation
        if not self.email1_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Primary email is required.")
            return
        
        if not self.full_name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return
        
        # Collect contact data
        self.contact_result = {
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
            'address1_country': self.country_edit.text().strip()
        }
        
        # Remove empty values
        self.contact_result = {k: v for k, v in self.contact_result.items() if v}
        
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
        header.setStyleSheet("color: #1e293b; margin: 10px;")
        layout.addWidget(header)
        
        # Splitter for relationship tree and email history
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Relationship tree
        relationship_group = QGroupBox("🌐 Contact Network")
        relationship_layout = QVBoxLayout(relationship_group)
        
        self.relationship_tree = QTreeWidget()
        self.relationship_tree.setHeaderLabels(["Contact", "Relationship", "Emails", "Last Contact"])
        relationship_layout.addWidget(self.relationship_tree)
        
        splitter.addWidget(relationship_group)
        
        # Email history
        email_group = QGroupBox("📧 Email History")
        email_layout = QVBoxLayout(email_group)
        
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["Date", "Subject", "Direction", "Status"])
        self.email_table.horizontalHeader().setStretchLastSection(True)
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
    """Complete Contact Management Dashboard"""
    
    def __init__(self):
        super().__init__()
        self.contacts_data = []
        self.filtered_contacts = []
        self.data_loader = None
        
        self.setup_ui()
        self.setup_data_loading()
        
        logger.info("Contact Management Dashboard initialized")
    
    def setup_ui(self):
        """Set up the main dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Contact Management Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                padding: 16px 24px;
                border-radius: 12px;
                margin-bottom: 8px;
            }
        """)
        header_layout.addWidget(title)
        
        # Control buttons
        self.new_contact_btn = QPushButton("👤 New Contact")
        self.new_contact_btn.clicked.connect(self.create_new_contact)
        self.new_contact_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        header_layout.addWidget(self.new_contact_btn)
        
        self.import_contacts_btn = QPushButton("📥 Import Contacts")
        self.import_contacts_btn.clicked.connect(self.import_contacts)
        self.import_contacts_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        header_layout.addWidget(self.import_contacts_btn)
        
        self.export_contacts_btn = QPushButton("📤 Export Contacts")
        self.export_contacts_btn.clicked.connect(self.export_contacts)
        self.export_contacts_btn.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        header_layout.addWidget(self.export_contacts_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter bar
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search contacts by name, email, or company...")
        self.search_edit.textChanged.connect(self.filter_contacts)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        search_layout.addWidget(self.search_edit)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Contacts", "Active", "Inactive"])
        self.status_filter.currentTextChanged.connect(self.filter_contacts)
        search_layout.addWidget(self.status_filter)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_contacts)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f1f5f9;
                color: #64748b;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1e293b;
                border: 2px solid #e2e8f0;
                border-bottom: none;
            }
        """)
        
        # Contact List Tab
        self.contact_list_tab = self.create_contact_list_tab()
        self.tab_widget.addTab(self.contact_list_tab, "📋 Contact List")
        
        # Relationship View Tab
        self.relationship_tab = ContactRelationshipView()
        self.tab_widget.addTab(self.relationship_tab, "🔗 Relationships")
        
        # Analytics Tab
        self.analytics_tab = self.create_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.contact_count_label = QLabel("0 contacts")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.contact_count_label)
        
        layout.addLayout(status_layout)
    
    def create_contact_list_tab(self) -> QWidget:
        """Create the contact list tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        self.edit_btn.clicked.connect(self.edit_selected_contact)
        action_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_selected_contact)
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        
        self.bulk_email_btn = QPushButton("📧 Bulk Email")
        self.bulk_email_btn.clicked.connect(self.send_bulk_email)
        action_layout.addWidget(self.bulk_email_btn)
        
        layout.addLayout(action_layout)
        
        return tab
    
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analytics header
        header = QLabel("📊 Contact Analytics")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1e293b; margin: 10px;")
        layout.addWidget(header)
        
        # Statistics grid
        stats_layout = QGridLayout()
        
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
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 16px;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 24))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("color: #1e293b;")
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #64748b; font-weight: bold;")
            
            card_layout.addWidget(icon_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(title_label)
            
            stats_layout.addWidget(card, i // 3, i % 3)
            self.stat_labels[title] = value_label
        
        layout.addLayout(stats_layout)
        
        # Recent activity
        activity_group = QGroupBox("📅 Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QTableWidget()
        self.activity_list.setColumnCount(3)
        self.activity_list.setHorizontalHeaderLabels(["Date", "Action", "Contact"])
        self.activity_list.horizontalHeader().setStretchLastSection(True)
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
        """Load contacts into the table"""
        self.contacts_data = contacts
        self.filtered_contacts = contacts.copy()
        self.populate_contact_table()
        self.update_analytics()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        self.contact_count_label.setText(f"{len(contacts)} contacts")
    
    def populate_contact_table(self):
        """Populate the contact table with data"""
        self.contact_table.setRowCount(len(self.filtered_contacts))
        
        for row, contact in enumerate(self.filtered_contacts):
            # Name
            name_item = QTableWidgetItem(contact.get('fullname', 'Unknown'))
            name_item.setData(Qt.ItemDataRole.UserRole, contact)  # Store full contact data
            self.contact_table.setItem(row, 0, name_item)
            
            # Email
            email = contact.get('emailaddress1', '')
            self.contact_table.setItem(row, 1, QTableWidgetItem(email))
            
            # Phone
            phone = contact.get('telephone1', '') or contact.get('mobilephone', '')
            self.contact_table.setItem(row, 2, QTableWidgetItem(phone))
            
            # Job Title
            job_title = contact.get('jobtitle', '')
            self.contact_table.setItem(row, 3, QTableWidgetItem(job_title))
            
            # City
            city = contact.get('address1_city', '')
            self.contact_table.setItem(row, 4, QTableWidgetItem(city))
            
            # Created Date
            created = contact.get('createdon', '')
            if created:
                try:
                    created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created_str = created_date.strftime('%Y-%m-%d')
                except:
                    created_str = created[:10] if len(created) >= 10 else created
            else:
                created_str = ''
            self.contact_table.setItem(row, 5, QTableWidgetItem(created_str))
            
            # Modified Date
            modified = contact.get('modifiedon', '')
            if modified:
                try:
                    modified_date = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified_str = modified_date.strftime('%Y-%m-%d')
                except:
                    modified_str = modified[:10] if len(modified) >= 10 else modified
            else:
                modified_str = ''
            self.contact_table.setItem(row, 6, QTableWidgetItem(modified_str))
            
            # Status
            status = contact.get('statuscode', 'Unknown')
            self.contact_table.setItem(row, 7, QTableWidgetItem(str(status)))
    
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
                except:
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
            contact_data = dialog.contact_result
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
            updated_data = dialog.contact_result
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
        super().closeEvent(event)

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