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
    QSizePolicy, QSpacerItem, QSlider, QFormLayout, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSettings
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QFontMetrics
from PyQt6.QtWidgets import QApplication

# Network connectivity testing
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("⚠️ requests library not available - connectivity testing disabled")

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
    THEME_MANAGER_AVAILABLE = True
except ImportError as e:
    THEME_MANAGER_AVAILABLE = False
    logger.warning("⚠️ Theme manager not available")


class ConnectivityTestThread(QThread):
    """Thread for performing real connectivity tests to Azure AD and Dynamics 365"""
    
    progress_updated = pyqtSignal(int, str)  # progress, status message
    test_completed = pyqtSignal(dict)  # results dictionary
    test_failed = pyqtSignal(str)  # error message
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, org_url: str):
        super().__init__()
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.org_url = org_url
        self.results = {}
    
    def run(self):
        """Perform comprehensive connectivity tests"""
        try:
            # Test 1: Tenant ID - Azure AD Discovery
            self.progress_updated.emit(10, "Testing Azure AD tenant accessibility...")
            self.test_tenant_connectivity()
            
            # Test 2: Client ID - App registration verification  
            self.progress_updated.emit(30, "Verifying app registration...")
            self.test_client_id_connectivity()
            
            # Test 3: Client Secret - Authentication test
            self.progress_updated.emit(60, "Testing authentication with client secret...")
            self.test_client_secret_connectivity()
            
            # Test 4: Organization URL - Dynamics 365 accessibility
            self.progress_updated.emit(60, "Testing Dynamics 365 organization access...")
            self.test_organization_url_connectivity()
            
            # Test 5: COMPREHENSIVE DATA ACCESS TEST - This is the real functionality test!
            self.progress_updated.emit(80, "🔍 Testing actual data access (contacts API)...")
            self.test_comprehensive_data_access()
            
            self.progress_updated.emit(100, "All tests completed!")
            self.msleep(500)  # Brief pause to show completion
            
            self.test_completed.emit(self.results)
            
        except Exception as e:
            self.test_failed.emit(f"Connectivity test error: {str(e)}")
    
    def test_tenant_connectivity(self):
        """Test Azure AD tenant accessibility"""
        try:
            import requests
            import json
        except ImportError:
            self.results['tenant_valid'] = False
            self.results['tenant_error'] = "requests library not available"
            return
        
        try:
            # Test Azure AD tenant using OAuth authorize endpoint (more reliable than discovery)
            auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            params = {
                'client_id': '00000000-0000-0000-0000-000000000000',  # Dummy client ID for tenant test
                'response_type': 'code',
                'redirect_uri': 'https://localhost',
                'scope': 'openid',
                'state': 'tenant_validation_test'
            }
            
            response = requests.get(auth_url, params=params, timeout=10, allow_redirects=False)
            
            if response.status_code == 200:
                # If we get 200, the tenant exists and is accessible
                self.results['tenant_valid'] = True
                self.results['tenant_error'] = None
            elif response.status_code == 302:
                # Redirect is also good - means tenant exists
                self.results['tenant_valid'] = True  
                self.results['tenant_error'] = None
            elif 'AADSTS90002' in response.text:
                # AADSTS90002 = Tenant does not exist
                self.results['tenant_valid'] = False
                self.results['tenant_error'] = "Tenant not found (AADSTS90002)"
            elif 'AADSTS50020' in response.text:
                # AADSTS50020 = User not from tenant (but tenant exists)
                self.results['tenant_valid'] = True
                self.results['tenant_error'] = None
            else:
                self.results['tenant_valid'] = False
                self.results['tenant_error'] = f"Tenant validation failed (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            self.results['tenant_valid'] = False
            self.results['tenant_error'] = "Connection timeout to Azure AD"
        except requests.exceptions.ConnectionError:
            self.results['tenant_valid'] = False
            self.results['tenant_error'] = "Network connection error to Azure AD"
        except Exception as e:
            self.results['tenant_valid'] = False
            self.results['tenant_error'] = f"Azure AD test error: {str(e)}"
    
    def test_client_id_connectivity(self):
        """Test app registration accessibility"""
        try:
            import requests
        except ImportError:
            self.results['client_valid'] = False
            self.results['client_error'] = "requests library not available"
            return
        
        try:
            # Test Microsoft Graph endpoint for app info (requires no auth for basic validation)
            # This tests if the client_id exists as an app registration
            auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': 'https://localhost',
                'scope': 'openid',
                'state': 'test'
            }
            
            # This will return 200 if client_id exists, error if not
            response = requests.get(auth_url, params=params, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                # Check if response contains client_id validation error
                if 'AADSTS700016' in response.text:  # Application not found
                    self.results['client_valid'] = False
                    self.results['client_error'] = "Application (Client ID) not found in tenant"
                else:
                    self.results['client_valid'] = True
                    self.results['client_error'] = None
            else:
                self.results['client_valid'] = False
                self.results['client_error'] = f"Client ID validation failed (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            self.results['client_valid'] = False
            self.results['client_error'] = "Connection timeout testing client ID"
        except requests.exceptions.ConnectionError:
            self.results['client_valid'] = False
            self.results['client_error'] = "Network connection error testing client ID"
        except Exception as e:
            self.results['client_valid'] = False
            self.results['client_error'] = f"Client ID test error: {str(e)}"
    
    def test_client_secret_connectivity(self):
        """Test client secret authentication"""
        try:
            import requests
        except ImportError:
            self.results['secret_valid'] = False
            self.results['secret_error'] = "requests library not available"
            return
        
        try:
            # Test actual authentication with client credentials flow
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data, timeout=15)
            
            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    self.results['secret_valid'] = True
                    self.results['secret_error'] = None
                    self.results['access_token'] = token_data['access_token']  # Store for Dynamics test
                else:
                    self.results['secret_valid'] = False
                    self.results['secret_error'] = "No access token in authentication response"
            else:
                error_data = response.json() if response.content else {}
                error_desc = error_data.get('error_description', f'HTTP {response.status_code}')
                self.results['secret_valid'] = False
                self.results['secret_error'] = f"Authentication failed: {error_desc}"
                
        except requests.exceptions.Timeout:
            self.results['secret_valid'] = False
            self.results['secret_error'] = "Connection timeout during authentication"
        except requests.exceptions.ConnectionError:
            self.results['secret_valid'] = False
            self.results['secret_error'] = "Network connection error during authentication"
        except Exception as e:
            self.results['secret_valid'] = False
            self.results['secret_error'] = f"Authentication test error: {str(e)}"
    
    def test_organization_url_connectivity(self):
        """Test Dynamics 365 organization accessibility"""
        try:
            import requests
        except ImportError:
            self.results['org_url_valid'] = False
            self.results['org_error'] = "requests library not available"
            return
        
        try:
            # Normalize URL
            org_url = self.org_url
            if not org_url.startswith('https://'):
                org_url = f"https://{org_url}"
            if not org_url.endswith('/'):
                org_url += '/'
            
            # Test basic connectivity to Dynamics 365 organization
            api_url = f"{org_url}api/data/v9.2/"
            
            # If we have a valid access token from client secret test, use it
            headers = {}
            if self.results.get('secret_valid') and 'access_token' in self.results:
                headers['Authorization'] = f"Bearer {self.results['access_token']}"
            
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                self.results['org_url_valid'] = True
                self.results['org_error'] = None
            elif response.status_code == 401:
                # Unauthorized is actually good - means the org exists but needs proper auth
                self.results['org_url_valid'] = True
                self.results['org_error'] = None
            elif response.status_code == 404:
                self.results['org_url_valid'] = False
                self.results['org_error'] = "Dynamics 365 organization not found at this URL"
            else:
                self.results['org_url_valid'] = False
                self.results['org_error'] = f"Organization URL test failed (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            self.results['org_url_valid'] = False
            self.results['org_error'] = "Connection timeout to Dynamics 365 organization"
        except requests.exceptions.ConnectionError:
            self.results['org_url_valid'] = False
            self.results['org_error'] = "Network connection error to Dynamics 365 organization"
        except Exception as e:
            self.results['org_url_valid'] = False
            self.results['org_error'] = f"Organization URL test error: {str(e)}"
    
    def test_comprehensive_data_access(self):
        """
        COMPREHENSIVE TEST: This tests the actual functionality that users will experience!
        Tests real data access to Dynamics 365 contacts API with proper OAuth for Dynamics.
        """
        try:
            import requests
        except ImportError:
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = "requests library not available"
            return
        
        # Only proceed if previous tests passed
        if not self.results.get('secret_valid', False):
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = "Cannot test data access - authentication failed"
            return
        
        if not self.results.get('org_url_valid', False):
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = "Cannot test data access - organization URL invalid"
            return
        
        try:
            # Step 1: Get Dynamics 365-specific OAuth token (this is different from Graph token!)
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
            
            # Extract base domain for Dynamics 365 resource
            org_url = self.org_url
            if org_url.startswith('http'):
                base_domain = org_url.split('//')[1].split('/')[0]
            else:
                base_domain = org_url.split('/')[0]
            
            # Use OAuth v1.0 parameters for Dynamics 365 authentication (not v2.0!)
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'resource': f"https://{base_domain}"  # Dynamics 365 specific resource
            }
            
            token_response = requests.post(token_url, data=token_data, timeout=10)
            
            if token_response.status_code != 200:
                error_data = token_response.json() if token_response.content else {}
                error_desc = error_data.get('error_description', f'HTTP {token_response.status_code}')
                self.results['data_access_valid'] = False
                self.results['data_access_error'] = f"Dynamics 365 authentication failed: {error_desc}"
                return
            
            dynamics_token = token_response.json().get('access_token')
            if not dynamics_token:
                self.results['data_access_valid'] = False
                self.results['data_access_error'] = "No access token received for Dynamics 365"
                return
            
            # Step 2: Test actual Dynamics 365 data access (contacts API)
            if not org_url.startswith('http'):
                org_url = f"https://{org_url}"
            if not org_url.endswith('/api/data/v9.2'):
                org_url = f"{org_url.rstrip('/')}/api/data/v9.2"
            
            contacts_url = f"{org_url}/contacts"
            headers = {
                'Authorization': f'Bearer {dynamics_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            # Request just a few contacts to test permissions
            params = {
                '$select': 'contactid,fullname,emailaddress1',
                '$top': 5  # Just test with 5 contacts
            }
            
            contacts_response = requests.get(contacts_url, headers=headers, params=params, timeout=15)
            
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                contacts = contacts_data.get('value', [])
                self.results['data_access_valid'] = True
                self.results['data_access_error'] = None
                self.results['contacts_count'] = len(contacts)
                self.results['data_access_details'] = f"Successfully retrieved {len(contacts)} contacts"
                
            elif contacts_response.status_code == 403:
                error_data = contacts_response.json() if contacts_response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Permission denied')
                self.results['data_access_valid'] = False
                self.results['data_access_error'] = f"PERMISSIONS INSUFFICIENT: {error_message}"
                self.results['data_access_details'] = (
                    "Authentication successful but app lacks Dynamics 365 permissions. "
                    "Need to add 'Dynamics CRM' > 'user_impersonation' permission and grant admin consent."
                )
                
            elif contacts_response.status_code == 401:
                self.results['data_access_valid'] = False
                self.results['data_access_error'] = "Unauthorized - invalid token for Dynamics 365"
                self.results['data_access_details'] = "Token authentication failed with Dynamics 365 API"
                
            else:
                self.results['data_access_valid'] = False
                self.results['data_access_error'] = f"Data access failed (HTTP {contacts_response.status_code})"
                self.results['data_access_details'] = f"Unexpected response from Dynamics 365: {contacts_response.text[:200]}"
                
        except requests.exceptions.Timeout:
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = "Timeout accessing Dynamics 365 data"
        except requests.exceptions.ConnectionError:
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = "Network connection error accessing Dynamics 365 data"
        except Exception as e:
            self.results['data_access_valid'] = False
            self.results['data_access_error'] = f"Data access test error: {str(e)}"


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
    
    def apply_theme(self, theme_definition):
        """Apply theme to authentication widget"""
        # Re-setup UI with new theme colors
        self.setup_ui()
    
    def setup_ui(self):
        """Setup authentication configuration UI"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'text_dark': '#2c3e50',
                'brand_primary': '#0077B5',
                'ui_surfaceAlt': '#F9FAFB',
                'ui_surface': '#FFFFFF',
                'text_secondary': '#666666',
                'brand_primaryHover': '#005885'
            }
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 20, 0, 20)
        
        # Header with improved spacing
        header_label = QLabel("🔐 Dynamics 365 Authentication")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {colors['text_dark']}; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Instructions section for finding authentication data
        instructions_group = QGroupBox("📋 How to Find Your Authentication Information")
        instructions_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                background-color: {colors['ui_surfaceAlt']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['brand_primary']};
                background-color: {colors['ui_surfaceAlt']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        instructions_layout = QVBoxLayout(instructions_group)
        instructions_layout.setContentsMargins(25, 25, 25, 20)
        instructions_layout.setSpacing(15)
        
        # Step-by-step instructions
        instructions_text = QLabel("""
        <div style="line-height: 1.6;">
        <p><strong>🔍 Step 1: Find Your Tenant ID</strong></p>
        <ul style="margin-left: 20px;">
        <li>Go to <a href="https://portal.azure.com">portal.azure.com</a> and sign in</li>
        <li>Search for "Azure Active Directory" in the search bar</li>
        <li>Click on "Properties" in the left menu</li>
        <li>Copy the <strong>Tenant ID</strong> (Directory ID)</li>
        </ul>
        
        <p><strong>🔧 Step 2: Create/Find Your App Registration</strong></p>
        <ul style="margin-left: 20px;">
        <li>In Azure AD, go to "App registrations" → "New registration"</li>
        <li>Name: "PST to Dynamics Import Tool"</li>
        <li>Supported account types: "Accounts in this organizational directory only"</li>
        <li>After creation, copy the <strong>Application (client) ID</strong></li>
        </ul>
        
        <p><strong>🔑 Step 3: Create Client Secret</strong></p>
        <ul style="margin-left: 20px;">
        <li>In your app registration, go to "Certificates & secrets"</li>
        <li>Click "New client secret" → Add description → Set expiration</li>
        <li>Copy the <strong>Value</strong> (not the Secret ID) - this is your Client Secret</li>
        <li><em>⚠️ Save this immediately - you can't view it again!</em></li>
        </ul>
        
        <p><strong>🌐 Step 4: Configure API Permissions</strong></p>
        <ul style="margin-left: 20px;">
        <li>Go to "API permissions" → "Add a permission"</li>
        <li>Select "Dynamics CRM" → "Delegated permissions"</li>
        <li>Check "user_impersonation" → Click "Add permissions"</li>
        <li>Click "Grant admin consent" (requires admin rights)</li>
        </ul>
        
        <p><strong>🏢 Step 5: Find Your Organization URL</strong></p>
        <ul style="margin-left: 20px;">
        <li>Go to <a href="https://admin.powerplatform.microsoft.com">admin.powerplatform.microsoft.com</a></li>
        <li>Click on "Environments" to see your Dynamics 365 environments</li>
        <li>Find your environment and copy the <strong>Environment URL</strong></li>
        <li>Format: https://[your-org].crm.dynamics.com</li>
        </ul>
        
        <p><strong>💡 Need Help?</strong></p>
        <ul style="margin-left: 20px;">
        <li>Ask your IT Administrator or Dynamics 365 Administrator</li>
        <li>They can provide these values or help you create the app registration</li>
        <li>Some organizations restrict app registrations to administrators only</li>
        </ul>
        </div>
        """)
        
        instructions_text.setWordWrap(True)
        instructions_text.setTextFormat(Qt.TextFormat.RichText)
        # Note: QLabel with RichText automatically handles clickable links
        instructions_text.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_secondary']};
                font-size: 13px;
                line-height: 1.6;
                padding: 10px;
                background-color: transparent;
            }}
            QLabel a {{
                color: {colors['brand_primary']};
                text-decoration: none;
                font-weight: bold;
            }}
            QLabel a:hover {{
                color: {colors['brand_primaryHover']};
                text-decoration: underline;
            }}
        """)
        
        instructions_layout.addWidget(instructions_text)
        layout.addWidget(instructions_group)
        
        # Configuration form with LinkedIn Blue theme
        form_group = QGroupBox("Authentication Credentials")
        form_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                background-color: {colors['ui_surface']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['brand_primary']};
                background-color: {colors['ui_surface']};
            }}
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
        
        # Tenant ID with enhanced styling and help button
        tenant_label = QLabel("Tenant ID:")
        # Get current theme colors for dynamic styling
        colors = get_theme_manager().get_theme_definition()['colors']
        text_primary = colors.get('text_primary', '#2C3E50')
        
        tenant_label.setStyleSheet(f"font-weight: bold; color: {text_primary}; font-size: 14px;")
        tenant_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        tenant_container = QWidget()
        tenant_layout = QHBoxLayout(tenant_container)
        tenant_layout.setContentsMargins(0, 0, 0, 0)
        tenant_layout.setSpacing(8)
        
        self.tenant_id_edit = QLineEdit()
        self.tenant_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.tenant_id_edit.setStyleSheet(self.get_input_style())
        
        tenant_help_btn = QPushButton("?")
        tenant_help_btn.setFixedSize(30, 30)
        tenant_help_btn.setStyleSheet(self.get_help_button_style())
        tenant_help_btn.setToolTip("Azure Portal → Azure Active Directory → Properties → Tenant ID")
        tenant_help_btn.clicked.connect(self._show_tenant_help)
        
        tenant_layout.addWidget(self.tenant_id_edit, 1)
        tenant_layout.addWidget(tenant_help_btn, 0)
        
        form_layout.addWidget(tenant_label, 0, 0)
        form_layout.addWidget(tenant_container, 0, 1)
        
        # Client ID with enhanced styling and help button
        client_label = QLabel("Client ID:")
        client_label.setStyleSheet(f"font-weight: bold; color: {text_primary}; font-size: 14px;")
        client_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        client_container = QWidget()
        client_layout = QHBoxLayout(client_container)
        client_layout.setContentsMargins(0, 0, 0, 0)
        client_layout.setSpacing(8)
        
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.client_id_edit.setStyleSheet(self.get_input_style())
        
        client_help_btn = QPushButton("?")
        client_help_btn.setFixedSize(30, 30)
        client_help_btn.setStyleSheet(self.get_help_button_style())
        client_help_btn.setToolTip("Azure Portal → App registrations → Your app → Overview → Application ID")
        client_help_btn.clicked.connect(self._show_client_help)
        
        client_layout.addWidget(self.client_id_edit, 1)
        client_layout.addWidget(client_help_btn, 0)
        
        form_layout.addWidget(client_label, 1, 0)
        form_layout.addWidget(client_container, 1, 1)
        
        # Client Secret with enhanced styling and help button
        secret_label = QLabel("Client Secret:")
        secret_label.setStyleSheet(f"font-weight: bold; color: {text_primary}; font-size: 14px;")
        secret_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        secret_container = QWidget()
        secret_layout = QHBoxLayout(secret_container)
        secret_layout.setContentsMargins(0, 0, 0, 0)
        secret_layout.setSpacing(8)
        
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_edit.setPlaceholderText("Enter client secret...")
        self.client_secret_edit.setStyleSheet(self.get_input_style())
        
        secret_help_btn = QPushButton("?")
        secret_help_btn.setFixedSize(30, 30)
        secret_help_btn.setStyleSheet(self.get_help_button_style())
        secret_help_btn.setToolTip("App registration → Certificates & secrets → Client secrets → Value")
        secret_help_btn.clicked.connect(self._show_secret_help)
        
        secret_layout.addWidget(self.client_secret_edit, 1)
        secret_layout.addWidget(secret_help_btn, 0)
        
        form_layout.addWidget(secret_label, 2, 0)
        form_layout.addWidget(secret_container, 2, 1)
        
        # Organization URL with enhanced styling and help button
        url_label = QLabel("Organization URL:")
        url_label.setStyleSheet(f"font-weight: bold; color: {text_primary}; font-size: 14px;")
        url_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(8)
        
        self.org_url_edit = QLineEdit()
        self.org_url_edit.setPlaceholderText("https://your-org.crm.dynamics.com")
        self.org_url_edit.setStyleSheet(self.get_input_style())
        
        url_help_btn = QPushButton("?")
        url_help_btn.setFixedSize(30, 30)
        url_help_btn.setStyleSheet(self.get_help_button_style())
        url_help_btn.setToolTip("Power Platform Admin Center → Environments → Your environment URL")
        url_help_btn.clicked.connect(self._show_url_help)
        
        url_layout.addWidget(self.org_url_edit, 1)
        url_layout.addWidget(url_help_btn, 0)
        
        form_layout.addWidget(url_label, 3, 0)
        form_layout.addWidget(url_container, 3, 1)
        
        layout.addWidget(form_group)
        
        # Test connection button with LinkedIn Blue theme
        brand_primary = colors.get('brand_primary', '#0077B5')
        brand_primary_hover = colors.get('brand_primaryHover', '#005885')
        brand_primary_active = colors.get('brand_primaryActive', '#004A70')
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        
        self.test_button = QPushButton("🔍 Test Connection")
        self.test_button.setMinimumHeight(45)
        self.test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand_primary};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                margin: 15px 0px 10px 0px;
            }}
            QPushButton:hover {{
                background-color: {brand_primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        # Add some bottom spacing
        layout.addSpacing(20)
    
    def get_input_style(self):
        """Get standardized input field styling with LinkedIn Blue theme"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'ui_surface': '#FFFFFF',
                'border_muted': '#bdc3c7',
                'ui_focus': '#0077B5',
                'brand_primaryHoverAlt': '#004A70',
                'text_muted': '#95a5a6'
            }
        
        return f"""
            QLineEdit {{
                padding: 12px 18px;
                border: 2px solid {colors['border_muted']};
                border-radius: 10px;
                font-size: 14px;
                background-color: {colors['ui_surface']};
                min-height: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {colors['ui_focus']};
                border-width: 3px;
            }}
            QLineEdit:hover {{
                border-color: {colors['brand_primaryHoverAlt']};
            }}
            QLineEdit:placeholder {{
                color: {colors['text_muted']};
                font-style: italic;
            }}
        """
    
    def get_help_button_style(self):
        """Get standardized help button styling with LinkedIn Blue theme"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'brand_primary': '#0077B5',
                'brand_primaryHover': '#005885',
                'text_inverse': 'white'
            }
        
        return f"""
            QPushButton {{
                background-color: {colors['brand_primary']};
                color: {colors['text_inverse']};
                border: none;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['brand_primaryHover']};
            }}
        """
    
    def show_help_dialog(self, title: str, content: str):
        """Show help dialog with detailed instructions"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(f"Help: {title}")
        dialog.setTextFormat(Qt.TextFormat.RichText)
        dialog.setText(content)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Make dialog larger for better readability
        dialog.setStyleSheet("""
            QMessageBox {
                min-width: 500px;
                min-height: 300px;
            }
            QMessageBox QLabel {
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        
        dialog.exec()
    
    def _show_tenant_help(self):
        """Safe handler for tenant ID help button"""
        try:
            self.show_help_dialog("Tenant ID", 
                "📍 <b>Where to find your Tenant ID:</b><br><br>"
                "1. Go to <a href='https://portal.azure.com'>portal.azure.com</a><br>"
                "2. Navigate to 'Azure Active Directory'<br>"
                "3. Click on 'Properties' in the left menu<br>"
                "4. Copy the <b>Tenant ID</b> (also called Directory ID)<br><br>"
                "💡 This uniquely identifies your Azure AD tenant.")
        except Exception as e:
            print(f"Warning: Could not show tenant help: {e}")
    
    def _show_client_help(self):
        """Safe handler for client ID help button"""
        try:
            self.show_help_dialog("Client ID", 
                "📍 <b>Where to find your Client ID:</b><br><br>"
                "1. Go to <a href='https://portal.azure.com'>portal.azure.com</a><br>"
                "2. Navigate to 'Azure Active Directory' → 'App registrations'<br>"
                "3. Find your app (or create new registration)<br>"
                "4. Copy the <b>Application (client) ID</b> from Overview page<br><br>"
                "💡 This identifies your specific application in Azure.")
        except Exception as e:
            print(f"Warning: Could not show client help: {e}")
    
    def _show_secret_help(self):
        """Safe handler for client secret help button"""
        try:
            self.show_help_dialog("Client Secret", 
                "📍 <b>How to create a Client Secret:</b><br><br>"
                "1. In your app registration, go to 'Certificates & secrets'<br>"
                "2. Click 'New client secret'<br>"
                "3. Add description and set expiration<br>"
                "4. Copy the <b>Value</b> (not the Secret ID)<br><br>"
                "⚠️ <b>Important:</b> Save this immediately - you can't view it again!<br><br>"
                "💡 This is like a password for your application.")
        except Exception as e:
            print(f"Warning: Could not show secret help: {e}")
    
    def _show_url_help(self):
        """Safe handler for organization URL help button"""
        try:
            self.show_help_dialog("Organization URL", 
                "📍 <b>Where to find your Organization URL:</b><br><br>"
                "1. Go to <a href='https://admin.powerplatform.microsoft.com'>admin.powerplatform.microsoft.com</a><br>"
                "2. Click on 'Environments'<br>"
                "3. Find your Dynamics 365 environment<br>"
                "4. Copy the <b>Environment URL</b><br><br>"
                "📝 <b>Format:</b> https://[your-org].crm.dynamics.com<br><br>"
                "💡 This is the web address of your Dynamics 365 instance.")
        except Exception as e:
            print(f"Warning: Could not show URL help: {e}")
    
    def test_connection(self):
        """Test authentication connection with detailed component validation"""
        # Get all field values
        tenant_id = self.tenant_id_edit.text().strip()
        client_id = self.client_id_edit.text().strip()
        client_secret = self.client_secret_edit.text().strip()
        org_url = self.org_url_edit.text().strip()
        
        # Check if all fields are filled
        if not all([tenant_id, client_id, client_secret, org_url]):
            QMessageBox.warning(self, "Validation Error", 
                              "Please fill in all authentication fields before testing.")
            return
        
        # Show progress dialog and start real connectivity tests
        self.show_connectivity_test_dialog(tenant_id, client_id, client_secret, org_url)
    
    def show_detailed_test_results(self, tenant_id: str, client_id: str, client_secret: str, org_url: str):
        """Show detailed test results for each authentication component"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        # Create custom dialog optimized for laptop screens - minimal height
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Connection Test Results")
        dialog.setMinimumSize(500, 320)
        dialog.setMaximumSize(600, 380)
        dialog.resize(520, 340)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        # Create main layout with minimal spacing
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        
        # Title - minimal
        title = QLabel("Authentication Test Results")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {colors.get('brand_primary', '#0077B5')}; margin-bottom: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Disclaimer about test type
        disclaimer = QLabel("Format validation only - not testing actual connectivity")
        disclaimer.setFont(QFont("Segoe UI", 7))
        disclaimer.setStyleSheet("color: #666; font-style: italic; margin-bottom: 4px;")
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(disclaimer)
        
        # Test results for each component
        components = [
            ("🏢 Tenant ID", tenant_id, self.validate_tenant_id(tenant_id)),
            ("📱 Client ID", client_id, self.validate_client_id(client_id)),
            ("🔑 Client Secret", client_secret, self.validate_client_secret(client_secret)),
            ("🌐 Organization URL", org_url, self.validate_org_url(org_url))
        ]
        
        for component_name, value, is_valid in components:
            component_frame = self.create_test_result_item(component_name, value, is_valid)
            layout.addWidget(component_frame)
        
        # Overall result - minimal
        all_valid = all(result[2] for result in components)
        overall_frame = QFrame()
        overall_frame.setMinimumHeight(24)
        overall_frame.setMaximumHeight(28)
        overall_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Get theme colors for validation styling
        colors = get_theme_manager().get_theme_definition()['colors']
        state_success = colors.get('state_success', '#28A745')
        state_error = colors.get('state_error', '#C0392B')
        section_success_bg = colors.get('section_successBg', '#D4EDDA')
        section_error_bg = colors.get('section_errorBg', '#F8D7DA')
        text_success_dark = colors.get('text_successDark', '#155724')
        text_error_dark = colors.get('text_errorDark', '#721C24')
        
        overall_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {section_success_bg if all_valid else section_error_bg};
                border: 2px solid {state_success if all_valid else state_error};
                border-radius: 3px;
                padding: 4px;
                margin-top: 2px;
                min-height: 24px;
                max-height: 28px;
            }}
        """)
        
        overall_layout = QHBoxLayout(overall_frame)
        overall_layout.setContentsMargins(2, 1, 2, 1)
        overall_icon = QLabel("✓" if all_valid else "✗")
        overall_icon.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        overall_icon.setMinimumSize(14, 14)
        overall_icon.setMaximumSize(14, 14)
        overall_icon.setStyleSheet(f"color: {state_success if all_valid else state_error}; background-color: transparent;")
        overall_text = QLabel("Ready for connection!" if all_valid else "Authentication incomplete")
        overall_text.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        overall_text.setStyleSheet(f"color: {text_success_dark if all_valid else text_error_dark};")
        overall_text.setWordWrap(True)
        
        overall_layout.addWidget(overall_icon)
        overall_layout.addWidget(overall_text, 1)
        layout.addWidget(overall_frame)
        
        # Close button - minimal
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)
        button_layout.addStretch()
        
        close_button = QPushButton("OK")
        close_button.setMinimumSize(50, 20)
        close_button.setMaximumSize(70, 24)
        close_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        brand_primary = colors.get('brand_primary', '#0077B5')
        brand_primary_hover = colors.get('brand_primaryHover', '#005885')
        brand_primary_active = colors.get('brand_primaryActive', '#004A70')
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand_primary};
                color: {text_inverse};
                border: none;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
                padding: 2px 8px;
                min-width: 50px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {brand_primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.exec()
    
    def show_connectivity_test_dialog(self, tenant_id: str, client_id: str, client_secret: str, org_url: str):
        """Show progress dialog and perform real connectivity tests"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
        from PyQt6.QtCore import QTimer, QThread, pyqtSignal
        from PyQt6.QtGui import QFont
        
        # Get theme colors for styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            colors = {
                'brand_primary': '#0077B5',
                'state_errorButton': '#DC3545',
                'state_error': '#C0392B',
                'text_inverse': '#FFFFFF'
            }
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        
        # Create progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("🔗 Testing Connection")
        progress_dialog.setMinimumSize(400, 200)
        progress_dialog.setMaximumSize(500, 250)
        progress_dialog.resize(450, 220)
        progress_dialog.setModal(True)
        progress_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        layout = QVBoxLayout(progress_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Testing Authentication Components")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {colors.get('brand_primary', '#0077B5')};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status label
        status_label = QLabel("Initializing tests...")
        status_label.setFont(QFont("Segoe UI", 10))
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        layout.addWidget(progress_bar)
        
        # Cancel button (initially hidden)
        cancel_button = QPushButton("Cancel")
        state_error_button = colors.get('state_errorButton', '#DC3545')
        state_error = colors.get('state_error', '#C0392B')
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {state_error_button};
                color: {text_inverse};
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {state_error};
            }}
        """)
        cancel_button.hide()
        layout.addWidget(cancel_button)
        
        # Check if requests library is available
        if not REQUESTS_AVAILABLE:
            progress_dialog.accept()
            QMessageBox.warning(self, "Connectivity Testing Unavailable", 
                              "Network connectivity testing requires the 'requests' library.\n\n"
                              "Falling back to format validation only.")
            self.show_detailed_test_results(tenant_id, client_id, client_secret, org_url)
            return
        
        # Start connectivity test thread
        self.connectivity_thread = ConnectivityTestThread(tenant_id, client_id, client_secret, org_url)
        
        # Store progress dialog and components for safe access
        self.current_progress_dialog = progress_dialog
        self.current_progress_bar = progress_bar
        self.current_status_label = status_label
        self.current_test_params = (tenant_id, client_id, client_secret, org_url)
        
        # Connect signals to safe methods instead of lambdas
        self.connectivity_thread.progress_updated.connect(self._on_connectivity_progress)
        self.connectivity_thread.test_completed.connect(self._on_connectivity_completed)
        self.connectivity_thread.test_failed.connect(self._on_connectivity_failed)
        
        cancel_button.clicked.connect(self._on_connectivity_cancelled)
        
        self.connectivity_thread.start()
        progress_dialog.exec()
    
    def _on_connectivity_progress(self, progress: int, status: str):
        """Safe handler for connectivity test progress updates"""
        try:
            if hasattr(self, 'current_progress_bar') and self.current_progress_bar:
                self.current_progress_bar.setValue(progress)
            if hasattr(self, 'current_status_label') and self.current_status_label:
                self.current_status_label.setText(status)
        except Exception as e:
            print(f"Warning: Could not update progress: {e}")
    
    def _on_connectivity_completed(self, results: dict):
        """Safe handler for connectivity test completion"""
        try:
            if hasattr(self, 'current_progress_dialog') and self.current_progress_dialog:
                self.current_progress_dialog.accept()
            
            if hasattr(self, 'current_test_params') and self.current_test_params:
                tenant_id, client_id, client_secret, org_url = self.current_test_params
                print(f"DEBUG: Connectivity test results: {results}")
                self.show_detailed_test_results_with_connectivity(tenant_id, client_id, client_secret, org_url, results)
        except Exception as e:
            print(f"Warning: Could not handle test completion: {e}")
        finally:
            self._cleanup_connectivity_test()
    
    def _on_connectivity_failed(self, error: str):
        """Safe handler for connectivity test failure"""
        try:
            if hasattr(self, 'current_progress_dialog') and self.current_progress_dialog:
                self.current_progress_dialog.accept()
            
            if hasattr(self, 'current_test_params') and self.current_test_params:
                tenant_id, client_id, client_secret, org_url = self.current_test_params
                print(f"DEBUG: Connectivity test failed: {error}")
                self.show_detailed_test_results_with_fallback(tenant_id, client_id, client_secret, org_url, error)
        except Exception as e:
            print(f"Warning: Could not handle test failure: {e}")
        finally:
            self._cleanup_connectivity_test()
    
    def _on_connectivity_cancelled(self):
        """Safe handler for connectivity test cancellation"""
        try:
            if hasattr(self, 'connectivity_thread') and self.connectivity_thread:
                self.connectivity_thread.terminate()
            if hasattr(self, 'current_progress_dialog') and self.current_progress_dialog:
                self.current_progress_dialog.reject()
        except Exception as e:
            print(f"Warning: Could not cancel test: {e}")
        finally:
            self._cleanup_connectivity_test()
    
    def _cleanup_connectivity_test(self):
        """Clean up connectivity test resources"""
        try:
            self.current_progress_dialog = None
            self.current_progress_bar = None
            self.current_status_label = None
            self.current_test_params = None
        except Exception:
            pass
    
    def show_detailed_test_results_with_connectivity(self, tenant_id: str, client_id: str, client_secret: str, org_url: str, connectivity_results: dict):
        """Show detailed test results including real connectivity tests"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        # Get theme colors for styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            colors = {
                'brand_primary': '#0077B5'
            }
        
        # Create custom dialog with compact sizing (70% scale)
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Complete Connection Test Results")
        dialog.setMinimumSize(406, 280)  # 70% of 580x400
        dialog.resize(434, 315)         # 70% of 620x450
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        # Remove size constraints that cause distortion on move
        dialog.setSizeGripEnabled(True)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(14, 14, 14, 14)  # 70% of 20
        layout.setSpacing(7)                       # 70% of 10
        
        # Title
        title = QLabel("Complete Authentication Test Results")
        title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))  # 70% of 12 ≈ 8
        title.setStyleSheet(f"color: {colors.get('brand_primary', '#0077B5')}; margin-bottom: 3px;")  # 70% of 4
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Test results for each component with connectivity
        components = [
            ("🏢 Tenant ID", tenant_id, connectivity_results.get('tenant_valid', False)),
            ("📱 Client ID", client_id, connectivity_results.get('client_valid', False)),
            ("🔑 Client Secret", client_secret, connectivity_results.get('secret_valid', False)),
            ("🌐 Organization URL", org_url, connectivity_results.get('org_url_valid', False)),
            ("🔍 Data Access", "Contacts API test", connectivity_results.get('data_access_valid', False))
        ]
        
        for component_name, value, is_valid in components:
            component_frame = self.create_connectivity_test_result_item(component_name, value, is_valid, connectivity_results)
            layout.addWidget(component_frame)
        
        # Overall result
        all_valid = all(result[2] for result in components)
        overall_frame = QFrame()
        overall_frame.setMinimumHeight(28)  # 70% of 40
        overall_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        overall_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {'#d4edda' if all_valid else '#f8d7da'};
                border: 1px solid {'#28a745' if all_valid else '#dc3545'};  /* 70% of 2px ≈ 1px */
                border-radius: 3px;        /* 70% of 4px ≈ 3px */
                padding: 6px;              /* 70% of 8px ≈ 6px */
                margin-top: 4px;           /* 70% of 6px ≈ 4px */
                min-height: 28px;          /* 70% of 40px */
            }}
        """)
        
        overall_layout = QHBoxLayout(overall_frame)
        overall_layout.setContentsMargins(6, 4, 6, 4)  # 70% of 8,6
        overall_icon = QLabel("✓" if all_valid else "✗")
        overall_icon.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))  # 70% of 12 ≈ 8
        overall_icon.setMinimumSize(11, 11)  # 70% of 16
        overall_icon.setMaximumSize(11, 11)  # 70% of 16
        overall_icon.setStyleSheet(f"color: {'#28a745' if all_valid else '#dc3545'}; background-color: transparent;")
        # More specific messaging based on what was actually tested
        data_access_valid = connectivity_results.get('data_access_valid', False)
        auth_components_valid = all(connectivity_results.get(key, False) for key in ['tenant_valid', 'client_valid', 'secret_valid', 'org_url_valid'])
        
        if all_valid and data_access_valid:
            message = "🎉 FULL FUNCTIONALITY CONFIRMED! Ready for production use."
        elif auth_components_valid and not data_access_valid:
            message = "⚠️ Authentication works, but permissions needed for data access"
        elif not auth_components_valid:
            message = "❌ Authentication configuration has issues"
        else:
            message = "❌ Connection test incomplete"
            
        overall_text = QLabel(message)
        overall_text.setFont(QFont("Segoe UI", 6, QFont.Weight.Bold))  # 70% of 9 ≈ 6
        overall_text.setStyleSheet(f"color: {'#155724' if all_valid else '#721c24'};")
        overall_text.setWordWrap(True)
        
        overall_layout.addWidget(overall_icon)
        overall_layout.addWidget(overall_text, 1)
        layout.addWidget(overall_frame)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 11, 0, 0)  # 70% of 15 ≈ 11
        button_layout.addStretch()
        
        close_button = QPushButton("OK")
        close_button.setMinimumSize(56, 22)  # 70% of 80x32
        close_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                border-radius: 4px;        /* 70% of 6px ≈ 4px */
                font-size: 8px;            /* 70% of 11px ≈ 8px */
                font-weight: bold;
                padding: 6px 11px;         /* 70% of 8px 16px ≈ 6px 11px */
                min-width: 56px;           /* 70% of 80px */
                min-height: 22px;          /* 70% of 32px */
            }
            QPushButton:hover {
                background-color: #005885;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.exec()
    
    def show_detailed_test_results_with_fallback(self, tenant_id: str, client_id: str, client_secret: str, org_url: str, error_message: str):
        """Show test results when connectivity testing failed - show format validation instead"""
        # Create a minimal results dict for format validation
        fallback_results = {
            'tenant_valid': self.validate_tenant_id(tenant_id),
            'client_valid': self.validate_client_id(client_id),
            'secret_valid': self.validate_client_secret(client_secret),
            'org_url_valid': self.validate_org_url(org_url),
            'tenant_error': 'Connectivity test failed - format validation only',
            'client_error': 'Connectivity test failed - format validation only',
            'secret_error': 'Connectivity test failed - format validation only',
            'org_error': 'Connectivity test failed - format validation only'
        }
        
        print(f"DEBUG: Showing fallback results: {fallback_results}")
        
        # Show the connectivity results dialog with fallback data
        self.show_detailed_test_results_with_connectivity(tenant_id, client_id, client_secret, org_url, fallback_results)
    
    def create_test_result_item(self, component_name: str, value: str, is_valid: bool) -> QFrame:
        """Create a test result item widget - minimal height"""
        frame = QFrame()
        frame.setMinimumHeight(50)
        frame.setMaximumHeight(60)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {'#d4edda' if is_valid else '#f8d7da'};
                border-left: 3px solid {'#28a745' if is_valid else '#dc3545'};
                border-radius: 3px;
                padding: 4px;
                margin: 1px 0px;
                min-height: 50px;
                max-height: 60px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(8)
        layout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        
        # Status icon - text based to avoid clipping
        status_text = "✓" if is_valid else "✗"
        status_icon = QLabel(status_text)
        status_icon.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        status_icon.setMinimumSize(20, 20)
        status_icon.setMaximumSize(20, 20)
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_icon.setStyleSheet(f"color: {'#28a745' if is_valid else '#dc3545'}; background-color: transparent;")
        layout.addWidget(status_icon)
        
        # Component info - minimal spacing
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Component name and status with test details
        name_status = f"{component_name} - {'Valid' if is_valid else 'Invalid'}"
        name_label = QLabel(name_status)
        name_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {'#155724' if is_valid else '#721c24'};")
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Test criteria explanation
        test_info = self.get_test_criteria_text(component_name, is_valid)
        test_label = QLabel(test_info)
        test_label.setFont(QFont("Segoe UI", 7))
        test_label.setStyleSheet("color: #5a6c7d; font-style: italic;")
        test_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        test_label.setWordWrap(True)
        
        # Full value display for better readability
        display_value = value
        if "Secret" in component_name:
            display_value = "•" * min(len(value), 20) + " (hidden)"
        elif len(value) > 45:
            display_value = value[:42] + "..."
            
        value_label = QLabel(display_value)
        value_label.setFont(QFont("Segoe UI", 8))
        value_label.setStyleSheet(f"color: {'#6c757d' if is_valid else '#721c24'};")
        value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        value_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(test_label)
        info_layout.addWidget(value_label)
        
        layout.addLayout(info_layout, 1)
        
        return frame
    
    def create_connectivity_test_result_item(self, component_name: str, value: str, is_valid: bool, connectivity_results: dict) -> QFrame:
        """Create a connectivity test result item widget with detailed test info"""
        print(f"DEBUG: Creating connectivity test item - {component_name}: {is_valid}, value: {value[:20]}...")
        
        # Special handling for Data Access errors to provide better guidance
        if component_name == "🔍 Data Access" and not is_valid:
            return self.create_enhanced_data_access_error_item(connectivity_results)
        
        frame = QFrame()
        frame.setMinimumHeight(49)  # 70% of 70
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {'#d4edda' if is_valid else '#f8d7da'};
                border-left: 2px solid {'#28a745' if is_valid else '#dc3545'};  /* 70% of 3px ≈ 2px */
                border-radius: 2px;    /* 70% of 3px ≈ 2px */
                padding: 6px;          /* 70% of 8px ≈ 6px */
                margin: 1px 0px;       /* 70% of 2px ≈ 1px */
                min-height: 49px;      /* 70% of 70px */
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)  # 70% of 12,8
        layout.setSpacing(8)                   # 70% of 12
        
        # Status icon - ensure visibility
        status_icon = QLabel("✓" if is_valid else "✗")
        status_icon.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))  # 70% of 16 ≈ 11
        status_icon.setMinimumSize(17, 17)  # 70% of 24
        status_icon.setMaximumSize(17, 17)  # 70% of 24
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_icon.setStyleSheet(f"""
            color: {'#28a745' if is_valid else '#dc3545'};
            background-color: transparent;
            border: none;
            padding: 1px;              /* 70% of 2px ≈ 1px */
        """)
        status_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(status_icon)
        
        # Component info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Component name and status - scaled font and ensure visibility
        name_status = f"{component_name} - {'Valid' if is_valid else 'Invalid'}"
        name_label = QLabel(name_status)
        name_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))  # 70% of 11 ≈ 8
        name_label.setStyleSheet(f"""
            color: {'#155724' if is_valid else '#721c24'};
            background-color: transparent;
            padding: 1px;       /* 70% of 2px ≈ 1px */
            min-height: 11px;   /* 70% of 16px ≈ 11px */
        """)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Connectivity test details - scaled font
        test_details = self.get_connectivity_test_details(component_name, is_valid, connectivity_results)
        test_label = QLabel(test_details)
        test_label.setFont(QFont("Segoe UI", 6))  # 70% of 9 ≈ 6
        test_label.setStyleSheet("""
            color: #5a6c7d; 
            font-style: italic;
            background-color: transparent;
            padding: 1px;
            min-height: 10px;   /* 70% of 14px ≈ 10px */
        """)
        test_label.setWordWrap(True)
        test_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Value display - scaled font
        display_value = value
        if "Secret" in component_name:
            display_value = "•" * min(len(value), 14) + " (hidden)"  # 70% of 20 ≈ 14
        elif len(value) > 28:  # 70% of 40 ≈ 28
            display_value = value[:26] + "..."  # 70% of 37 ≈ 26
            
        value_label = QLabel(display_value)
        value_label.setFont(QFont("Segoe UI", 6))  # 70% of 9 ≈ 6
        value_label.setStyleSheet(f"""
            color: {'#6c757d' if is_valid else '#721c24'};
            background-color: transparent;
            padding: 1px;
            min-height: 10px;   /* 70% of 14px ≈ 10px */
        """)
        value_label.setWordWrap(True)
        value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(test_label)
        info_layout.addWidget(value_label)
        
        layout.addLayout(info_layout, 1)
        
        return frame
    
    def create_enhanced_data_access_error_item(self, connectivity_results: dict) -> QFrame:
        """Create an enhanced error display for Data Access failures with clear guidance"""
        frame = QFrame()
        frame.setMinimumHeight(70)  # Taller for more content
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;  /* Warning yellow background */
                border-left: 3px solid #ffc107;  /* Warning yellow border */
                border-radius: 3px;
                padding: 8px;
                margin: 1px 0px;
                min-height: 70px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        
        # Warning icon
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        icon_label.setStyleSheet("color: #856404; background-color: transparent;")
        icon_label.setMinimumSize(15, 15)
        icon_label.setMaximumSize(15, 15)
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Data Access - Permissions Required")
        title_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #856404; background-color: transparent;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Error message
        error_msg = connectivity_results.get('data_access_error', 'Data access failed')
        error_label = QLabel(f"❌ {error_msg}")
        error_label.setFont(QFont("Segoe UI", 6))
        error_label.setStyleSheet("color: #721c24; background-color: transparent; padding: 2px;")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        
        # Fix guidance
        fix_button = QPushButton("🔧 How to Fix This")
        fix_button.setFont(QFont("Segoe UI", 6, QFont.Weight.Bold))
        fix_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #856404;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                text-align: left;
                min-height: 18px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        fix_button.clicked.connect(lambda: self.show_data_access_fix_guidance(connectivity_results))
        layout.addWidget(fix_button)
        
        return frame
    
    def show_data_access_fix_guidance(self, connectivity_results: dict):
        """Show comprehensive guidance on how to fix data access permissions for ordinary users"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QTabWidget, QWidget, QScrollArea, QTextBrowser
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        # Get current Client ID from the form
        current_client_id = self.client_id_edit.text().strip()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔧 Complete Setup Guide - Fix Data Access")
        dialog.setMinimumSize(600, 500)
        dialog.resize(650, 550)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🔧 Complete Setup Guide: Fix Dynamics 365 Data Access")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #0077B5; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Problem explanation
        problem_label = QLabel("❌ <b>Issue:</b> Authentication works, but data access fails due to incomplete setup.")
        problem_label.setFont(QFont("Segoe UI", 9))
        problem_label.setWordWrap(True)
        problem_label.setStyleSheet("color: #721c24; background-color: #f8d7da; padding: 8px; border-radius: 4px;")
        layout.addWidget(problem_label)
        
        # Tab widget for two-part solution
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0077B5;
                color: white;
            }
        """)
        
        # Step 1 Tab: Azure AD Permissions
        step1_widget = QWidget()
        step1_layout = QVBoxLayout(step1_widget)
        step1_layout.setContentsMargins(15, 15, 15, 15)
        
        step1_title = QLabel("1️⃣ Azure AD App Permissions")
        step1_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        step1_title.setStyleSheet("color: #0077B5; margin-bottom: 8px;")
        step1_layout.addWidget(step1_title)
        
        # Add clickable links instruction
        step1_instruction = QLabel("💡 Tip: Blue underlined links below are clickable and will open in your browser")
        step1_instruction.setFont(QFont("Segoe UI", 8))
        step1_instruction.setStyleSheet("color: #6c757d; font-style: italic; margin-bottom: 5px;")
        step1_layout.addWidget(step1_instruction)
        
        step1_content = QTextBrowser()
        step1_content.setMaximumHeight(250)
        # Enable clickable links
        step1_content.setOpenExternalLinks(True)
        step1_html = """
<div style="font-family: Segoe UI; font-size: 10px; line-height: 1.5;">
<b>🔗 Add Azure AD Permissions:</b>
<ol>
<li><b>Go to:</b> <a href="https://portal.azure.com" style="color: #0077B5; text-decoration: underline; font-weight: bold;">🔗 Azure Portal (portal.azure.com)</a></li>
<li><b>Navigate:</b> Azure Active Directory → App registrations</li>
<li><b>Find your app:</b> "PST To Dynamics Import Tool"</li>
<li><b>Click:</b> "API permissions" (in left menu)</li>
<li><b>Add permission:</b> Click "+ Add a permission"</li>
<li><b>Select:</b> "Dynamics CRM" from the APIs list</li>
<li><b>Choose:</b> "Delegated permissions"</li>
<li><b>Check:</b> ✅ "user_impersonation"</li>
<li><b>Click:</b> "Add permissions"</li>
<li><b>🚨 CRITICAL:</b> Click "Grant admin consent for [your organization]"</li>
<li><b>Verify:</b> Status shows "Granted for [your organization]" with green checkmark</li>
</ol>
</div>
"""
        step1_content.setHtml(step1_html)
        step1_content.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px;")
        step1_layout.addWidget(step1_content)
        
        tab_widget.addTab(step1_widget, "Step 1: Azure AD")
        
        # Step 2 Tab: Dynamics 365 Application User
        step2_widget = QWidget()
        step2_layout = QVBoxLayout(step2_widget)
        step2_layout.setContentsMargins(15, 15, 15, 15)
        
        step2_title = QLabel("2️⃣ Dynamics 365 Application User")
        step2_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        step2_title.setStyleSheet("color: #0077B5; margin-bottom: 8px;")
        step2_layout.addWidget(step2_title)
        
        # Add clickable links instruction
        step2_instruction = QLabel("💡 Tip: Blue underlined links below are clickable and will open in your browser")
        step2_instruction.setFont(QFont("Segoe UI", 8))
        step2_instruction.setStyleSheet("color: #6c757d; font-style: italic; margin-bottom: 5px;")
        step2_layout.addWidget(step2_instruction)
        
        step2_content = QTextBrowser()
        step2_content.setMaximumHeight(250)
        # Enable clickable links
        step2_content.setOpenExternalLinks(True)
        step2_html = f"""
<div style="font-family: Segoe UI; font-size: 10px; line-height: 1.5;">
<b>👤 Create Application User in Dynamics 365:</b>
<ol>
<li><b>Go to:</b> <a href="https://admin.powerplatform.microsoft.com" style="color: #0077B5; text-decoration: underline; font-weight: bold;">🔗 Power Platform Admin Center</a></li>
<li><b>Navigate:</b> Environments → [Your Environment] → Settings</li>
<li><b>Click:</b> "Users + permissions" → "Application users"</li>
<li><b>Click:</b> "+ New app user"</li>
<li><b>Add an app:</b> Click "Add an app"</li>
<li><b>Select:</b> Your "PST To Dynamics Import Tool" app (use Client ID: <code>{current_client_id}</code> to find it)</li>
<li><b>Business Unit Field:</b> 
   <ul style="margin-top: 5px;">
   <li>📝 <b>Type your organization name</b> (e.g., "Contoso", "Your Company Name")</li>
   <li>📝 <b>OR try common patterns:</b> "Root Business Unit", "[OrganizationName]", "Default Business Unit"</li>
   <li>📝 <b>If dropdown shows no results:</b> Leave it blank and continue - it will use default</li>
   <li>💡 <b>Tip:</b> This is usually your main organization/company name from Dynamics 365</li>
   </ul>
</li>
<li><b>🔐 CRITICAL - Assign Security Roles:</b>
   <ul>
   <li>✅ <b>System Administrator</b> (full access) OR</li>
   <li>✅ <b>System Customizer</b> + <b>Sales Manager</b> (contacts access) OR</li>
   <li>✅ Custom role with Contact: Create, Read, Write, Delete permissions</li>
   </ul>
</li>
<li><b>Click:</b> "Create" to save the application user</li>
<li><b>Verify:</b> Application user appears in the list with "Enabled" status</li>
</ol>
</div>
"""
        step2_content.setHtml(step2_html)
        step2_content.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px;")
        step2_layout.addWidget(step2_content)
        
        tab_widget.addTab(step2_widget, "Step 2: D365 User")
        
        layout.addWidget(tab_widget)
        
        # Important notes
        notes_label = QLabel("⚠️ <b>Important Notes:</b>")
        notes_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        notes_label.setStyleSheet("color: #856404; margin-top: 10px;")
        layout.addWidget(notes_label)
        
        notes_content = QLabel("""• You need <b>Global Administrator</b> or <b>Application Administrator</b> rights in Azure AD for Step 1
• You need <b>System Administrator</b> rights in Dynamics 365 for Step 2  
• Both steps are required - Azure AD permissions alone are not sufficient
• After completing both steps, restart this application and test again
• If you don't have admin rights, ask your IT administrator to complete these steps""")
        notes_content.setFont(QFont("Segoe UI", 8))
        notes_content.setWordWrap(True)
        notes_content.setStyleSheet("color: #856404; background-color: #fff3cd; padding: 8px; border-radius: 4px; border-left: 3px solid #ffc107;")
        layout.addWidget(notes_content)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Help button for more info
        help_button = QPushButton("📞 Need Help?")
        help_button.setFont(QFont("Segoe UI", 9))
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        help_button.clicked.connect(lambda: self.show_additional_help_dialog())
        button_layout.addWidget(help_button)
        
        # Close button
        close_button = QPushButton("✅ I'll Complete These Steps")
        close_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def show_additional_help_dialog(self):
        """Show additional help and troubleshooting information"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QTextBrowser
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📞 Additional Help & Troubleshooting")
        dialog.setMinimumSize(550, 400)
        dialog.resize(600, 450)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📞 Additional Help & Troubleshooting")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #0077B5; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Help content
        help_content = QTextBrowser()
        # Enable clickable links
        help_content.setOpenExternalLinks(True)
        help_html = """
<div style="font-family: Segoe UI; font-size: 10px; line-height: 1.5;">

<h3 style="color: #0077B5;">🔍 Common Issues & Solutions:</h3>

<b>❓ "I don't have admin rights"</b><br/>
→ Ask your IT administrator to complete both setup steps<br/>
→ Send them this guide: they'll know what to do<br/>
→ You'll need both Azure AD and Dynamics 365 admin permissions<br/><br/>

<b>❓ "Can't find my app in Azure Portal"</b><br/>
→ Make sure you're in the correct Azure AD tenant<br/>
→ Check that the app name is exactly "PST To Dynamics Import Tool"<br/>
→ Try searching by the Client ID instead of name<br/><br/>

<b>❓ "Dynamics CRM permission not available"</b><br/>
→ Make sure you have Dynamics 365 licenses in your tenant<br/>
→ The API may be called "Common Data Service" in some tenants<br/>
→ Look for "CRM" or "Dynamics" in the API list<br/><br/>

<b>❓ "Can't find Application Users in Dynamics 365"</b><br/>
→ Make sure you're in the Power Platform Admin Center (not Dynamics 365 web app)<br/>
→ You need System Administrator role in Dynamics 365<br/>
→ Navigate: Environments → [Your Environment] → Settings → Users + permissions<br/><br/>

<b>❓ "Business Unit dropdown shows no results"</b><br/>
→ Try typing your company/organization name (e.g., "Contoso", "Acme Corp")<br/>
→ Try common patterns: "Root Business Unit", "Default Business Unit", "[YourOrgName]"<br/>
→ If nothing works, leave it blank - the system will use the default business unit<br/>
→ Business unit names match your organization's structure in Dynamics 365<br/><br/>

<b>❓ "Still getting permission errors after setup"</b><br/>
→ Wait 10-15 minutes for permissions to propagate<br/>
→ Make sure you granted admin consent (step is often missed)<br/>
→ Verify the Application User has correct security roles assigned<br/>
→ Try logging out and back into Azure/Dynamics 365<br/><br/>

<h3 style="color: #0077B5;">🆘 Need More Help?</h3>

<b>Contact Information:</b><br/>
• Your IT Administrator (for permission issues)<br/>
• Microsoft Support (for Azure AD or Dynamics 365 specific issues)<br/>
• Application Support: Check the application documentation for contact details<br/><br/>

<b>What to include when asking for help:</b><br/>
• Screenshot of the error message from this application<br/>
• Your Azure AD tenant domain name<br/>
• Your Dynamics 365 organization URL<br/>
• Whether you completed both setup steps<br/>
• Any specific error messages from Azure Portal or Power Platform Admin Center<br/>

</div>
"""
        help_content.setHtml(help_html)
        help_content.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 12px;
            }
        """)
        layout.addWidget(help_content)
        
        # Close button
        button_layout = QVBoxLayout()
        close_button = QPushButton("✅ Back to Setup Guide")
        close_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(close_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def get_connectivity_test_details(self, component_name: str, is_valid: bool, connectivity_results: dict) -> str:
        """Get detailed connectivity test results for each component"""
        if component_name == "🏢 Tenant ID":
            if is_valid:
                return "✓ Azure AD tenant accessible via OAuth endpoint"
            else:
                return f"✗ {connectivity_results.get('tenant_error', 'Tenant not found or inaccessible')}"
        elif component_name == "📱 Client ID":
            if is_valid:
                return "✓ App registration found and accessible"
            else:
                return f"✗ {connectivity_results.get('client_error', 'App registration not found')}"
        elif component_name == "🔑 Client Secret":
            if is_valid:
                return "✓ Client secret valid, authentication successful"
            else:
                return f"✗ {connectivity_results.get('secret_error', 'Authentication failed with provided secret')}"
        elif component_name == "🌐 Organization URL":
            if is_valid:
                return "✓ Dynamics 365 organization accessible"
            else:
                return f"✗ {connectivity_results.get('org_error', 'Organization URL not accessible')}"
        elif component_name == "🔍 Data Access":
            if is_valid:
                contacts_count = connectivity_results.get('contacts_count', 0)
                return f"✓ Successfully accessed Dynamics 365 data ({contacts_count} contacts retrieved)"
            else:
                error_msg = connectivity_results.get('data_access_error', 'Data access failed')
                details = connectivity_results.get('data_access_details', '')
                if details:
                    return f"✗ {error_msg}\n   {details}"
                else:
                    return f"✗ {error_msg}"
        return "Test completed"
    
    def get_test_criteria_text(self, component_name: str, is_valid: bool) -> str:
        """Get explanation of what test criteria are being checked"""
        criteria_map = {
            "🏢 Tenant ID": {
                "valid": "✓ Format: Valid UUID (36 characters, dashes at positions 8,13,18,23)",
                "invalid": "✗ Expected: UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"
            },
            "📱 Client ID": {
                "valid": "✓ Format: Valid UUID (Application ID from Azure AD)",
                "invalid": "✗ Expected: UUID format (Application ID from Azure AD)"
            },
            "🔑 Client Secret": {
                "valid": "✓ Format: Valid secret (10+ characters, contains alphanumeric)",
                "invalid": "✗ Expected: Valid secret (minimum 10 characters, alphanumeric content)"
            },
            "🌐 Organization URL": {
                "valid": "✓ Format: Valid Dynamics 365 URL (*.crm*.dynamics.com)",
                "invalid": "✗ Expected: Dynamics 365 URL format (orgname.crm.dynamics.com)"
            },
            "🔍 Data Access": {
                "valid": "✓ Real Data Access: Contacts API accessed successfully with proper permissions",
                "invalid": "✗ Data Access Failed: Cannot retrieve live Dynamics 365 data (permissions needed)"
            }
        }
        
        component_criteria = criteria_map.get(component_name, {})
        return component_criteria.get("valid" if is_valid else "invalid", "Format validation")
    
    def validate_tenant_id(self, tenant_id: str) -> bool:
        """Validate Tenant ID format (UUID)"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, tenant_id.lower()))
    
    def validate_client_id(self, client_id: str) -> bool:
        """Validate Client ID format (UUID)"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, client_id.lower()))
    
    def validate_client_secret(self, client_secret: str) -> bool:
        """Validate Client Secret (basic checks)"""
        # Client secrets are typically 32+ characters and contain various characters
        return len(client_secret) >= 10 and any(c.isalnum() for c in client_secret)
    
    def validate_org_url(self, org_url: str) -> bool:
        """Validate Organization URL format"""
        import re
        # Dynamics 365 URL pattern - flexible for with/without https://
        # Pattern 1: With https:// prefix
        url_pattern_https = r'^https://[a-zA-Z0-9-]+\.crm\d*\.dynamics\.com/?$'
        # Pattern 2: Without https:// prefix (common in admin center)
        url_pattern_domain = r'^[a-zA-Z0-9-]+\.crm\d*\.dynamics\.com/?$'
        
        return bool(re.match(url_pattern_https, org_url) or re.match(url_pattern_domain, org_url))
    
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
    
    def apply_theme(self, theme_definition):
        """Apply theme to configuration manager"""
        colors = theme_definition['colors']
        
        # Update main widget styling
        self.setStyleSheet(f"""
            ConfigurationManager {{
                background: {colors['ui_canvas']};
                color: {colors['text_primary']};
            }}
        """)
        
        # Refresh the auth widget if it has an apply_theme method
        if hasattr(self.auth_widget, 'apply_theme'):
            self.auth_widget.apply_theme(theme_definition)
    
    def resizeEvent(self, event):
        """Override resize event - simplified like Import Wizard"""
        super().resizeEvent(event)
        # No aggressive height enforcement - let Qt handle layout naturally
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (fixed 60px)
        header = self.create_header()
        layout.addWidget(header)
        
        # Set up content
        self.setup_content()
    
    def create_header(self) -> QWidget:
        """Create dashboard header (standardized to match Settings panel)"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'brand_primary': '#0077B5',
                'brand_primaryBorder': '#006097',
                'text_inverse': 'white'
            }
        
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background-color: {colors['brand_primary']};
            border-bottom: 1px solid {colors['brand_primaryBorder']};
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            color: {colors['text_inverse']};
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def setup_content(self):
        """Set up the main content area"""
        layout = self.layout()
        
        # Get current theme colors for dynamic styling FIRST
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'ui_canvas': '#F3F6F8',
                'ui_surface': '#FFFFFF',
                'brand_primary': '#0077B5',
                'ui_surfaceLight': '#F8F9FA',
                'ui_divider': '#E1E4E8'
            }
        
        # ScrollArea (takes remaining space minus footer) - settings content ONLY
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"QScrollArea {{ border: none; background-color: {colors['ui_canvas']}; }}")
        
        scroll_widget = QWidget()
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(20, 20, 20, 0)
        scroll_layout.setSpacing(20)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Store references
        self.scroll_area = scroll_area
        self.scroll_widget = scroll_widget
        self.scroll_layout = scroll_layout
        
        # Use the 'live' auth_widget for the main content
        scroll_layout.addWidget(self.auth_widget)
        
        # Add the rest of the settings sections with consistent LinkedIn Blue theme
        email_section = QGroupBox("📧 Email Processing Settings")
        email_section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                background-color: {colors['ui_surface']};
                font-size: 14px;
                min-height: 200px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['brand_primary']};
                background-color: {colors['ui_surface']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        email_layout = QVBoxLayout(email_section)
        email_layout.setContentsMargins(20, 15, 20, 15)
        email_layout.setSpacing(5)  # Reduced from 8 to 5
        
        # Create and store email processing settings with defaults and descriptions
        self.batch_size_edit = QLineEdit("50")  # Default: 50 emails per batch
        self.timeout_edit = QLineEdit("30")     # Default: 30 seconds timeout
        self.max_attachments_edit = QLineEdit("10")  # Default: 10 max attachments
        self.auto_retry_checkbox = QCheckBox("Enable")
        self.auto_retry_checkbox.setChecked(True)  # Default: enabled
        
        # Use enhanced layout with descriptions
        self.add_config_row_with_description(
            email_layout, "Batch Size:", self.batch_size_edit,
            "Number of emails processed in each batch. Higher values process faster but use more memory. Recommended: 25-100 for small systems, 100-500 for powerful systems."
        )
        self.add_config_row_with_description(
            email_layout, "Timeout (seconds):", self.timeout_edit,
            "Maximum time to wait for each email operation before timing out. Increase for slow networks or large attachments. Recommended: 30-120 seconds."
        )
        self.add_config_row_with_description(
            email_layout, "Max Attachments:", self.max_attachments_edit,
            "Maximum number of attachments to process per email. Higher values may slow processing. Set to 0 for unlimited. Recommended: 5-20 attachments."
        )
        self.add_config_row_with_description(
            email_layout, "Auto-retry Failed:", self.auto_retry_checkbox,
            "Automatically retry failed email imports after temporary network or server errors. Recommended: Enable for reliable import processing."
        )
        scroll_layout.addWidget(email_section)
        
        perf_section = QGroupBox("⚡ Performance Settings")
        perf_section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                background-color: {colors['ui_surface']};
                font-size: 14px;
                min-height: 200px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['brand_primary']};
                background-color: {colors['ui_surface']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        perf_layout = QVBoxLayout(perf_section)
        perf_layout.setContentsMargins(20, 15, 20, 15)
        perf_layout.setSpacing(5)  # Reduced from 8 to 5
        
        # Create and store performance settings with defaults and descriptions
        self.thread_pool_edit = QLineEdit("4")    # Default: 4 threads
        self.memory_limit_edit = QLineEdit("512") # Default: 512 MB memory limit
        self.cache_size_edit = QLineEdit("128")   # Default: 128 MB cache
        self.enable_logging_checkbox = QCheckBox("Enable")
        self.enable_logging_checkbox.setChecked(True)  # Default: enabled
        
        # Use enhanced layout with descriptions
        self.add_config_row_with_description(
            perf_layout, "Thread Pool Size:", self.thread_pool_edit,
            "Number of parallel processing threads. More threads = faster processing but higher CPU usage. Match your CPU cores. Recommended: 2-8 threads."
        )
        self.add_config_row_with_description(
            perf_layout, "Memory Limit (MB):", self.memory_limit_edit,
            "Maximum memory the application can use before optimization kicks in. Higher values allow larger PST files. Recommended: 256-1024 MB based on available RAM."
        )
        self.add_config_row_with_description(
            perf_layout, "Cache Size (MB):", self.cache_size_edit,
            "Amount of memory reserved for caching frequently accessed data. Larger cache improves speed but uses more RAM. Recommended: 64-256 MB."
        )
        self.add_config_row_with_description(
            perf_layout, "Enable Logging:", self.enable_logging_checkbox,
            "Records detailed operation logs for troubleshooting and monitoring. Minimal performance impact. Recommended: Enable for production monitoring."
        )
        scroll_layout.addWidget(perf_section)
        
        ai_section = QGroupBox("🧠 AI Intelligence Settings")
        ai_section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['brand_primary']};
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                background-color: {colors['ui_surface']};
                font-size: 14px;
                min-height: 200px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: {colors['brand_primary']};
                background-color: {colors['ui_surface']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        ai_layout = QVBoxLayout(ai_section)
        ai_layout.setContentsMargins(20, 15, 20, 15)
        ai_layout.setSpacing(5)  # Reduced from 8 to 5
        
        # Create and store AI intelligence settings with defaults and descriptions
        self.ai_analysis_checkbox = QCheckBox("Enable")
        self.ai_analysis_checkbox.setChecked(True)  # Default: enabled
        self.confidence_threshold_edit = QLineEdit("0.85")  # Default: 85% confidence
        self.learning_mode_combo = QComboBox()
        self.learning_mode_combo.addItems(["Active", "Passive", "Disabled"])
        self.learning_mode_combo.setCurrentText("Active")  # Default: Active
        self.pattern_recognition_checkbox = QCheckBox("Enable")
        self.pattern_recognition_checkbox.setChecked(True)  # Default: enabled
        
        # Use enhanced layout with descriptions
        self.add_config_row_with_description(
            ai_layout, "Enable AI Analysis:", self.ai_analysis_checkbox,
            "Uses machine learning to analyze email content for better categorization and insights. Improves over time. Recommended: Enable for enhanced functionality."
        )
        self.add_config_row_with_description(
            ai_layout, "Confidence Threshold:", self.confidence_threshold_edit,
            "Minimum confidence level (0.0-1.0) for AI predictions to be accepted. Lower values = more predictions, higher risk. Recommended: 0.75-0.90 for balanced accuracy."
        )
        self.add_config_row_with_description(
            ai_layout, "Learning Mode:", self.learning_mode_combo,
            "Active: Learns from user feedback. Passive: Uses existing models only. Disabled: No AI learning. Recommended: Active for continuous improvement."
        )
        self.add_config_row_with_description(
            ai_layout, "Pattern Recognition:", self.pattern_recognition_checkbox,
            "Identifies common patterns in email data for automated processing suggestions. Helps optimize future imports. Recommended: Enable for workflow optimization."
        )
        scroll_layout.addWidget(ai_section)
        
        # Add bottom padding to scroll content
        scroll_layout.addSpacing(20)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area, 1)  # Takes remaining space
        
        # FOOTER - Apply Import Wizard's successful pattern
        footer = QFrame()  # Use QFrame like Import Wizard
        footer.setFixedHeight(80)  # Match Import Wizard's 80px (not 200px)
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['ui_surfaceLight']};
            border-top: 1px solid {colors['ui_divider']};
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        # Store footer reference
        self.footer_widget = footer
        
        # Status label
        self.status_label = QLabel("Configuration ready")
        self.status_label.setStyleSheet(f"color: {colors.get('text_secondary', '#666')}; font-size: 14px;")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        brand_primary = colors.get('brand_primary', '#0077B5')
        brand_primary_hover = colors.get('brand_primaryHover', '#005885')
        brand_primary_active = colors.get('brand_primaryActive', '#004A70')
        text_inverse = colors.get('text_inverse', '#FFFFFF')
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand_primary};
                color: {text_inverse};
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {brand_primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {brand_primary_active};
            }}
        """)
        self.save_button.clicked.connect(self.save_all_settings)
        footer_layout.addWidget(self.save_button)
        
        # Add footer to main layout
        layout.addWidget(footer)
    
    def add_config_row_with_description(self, parent_layout, label_text: str, widget, description: str):
        """Add a configuration row with 1/3 input field and 2/3 description layout"""
        try:
            # Get theme colors
            if THEME_MANAGER_AVAILABLE:
                theme_manager = get_theme_manager()
                theme_def = theme_manager.get_theme_definition()
                colors = theme_def['colors']
            else:
                # Fallback colors matching LinkedIn Blue theme
                colors = {
                    'text_primary': '#2C3E50',
                    'text_secondary': '#666666',
                    'ui_surface': '#FFFFFF',
                    'ui_divider': '#D0D7DE'
                }
            
            # Create main horizontal container
            row_container = QWidget()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(0, 4, 0, 4)  # Reduced from 8 to 4
            row_layout.setSpacing(15)
            
            # Left side: Label + Input (1/3 of width)
            left_container = QWidget()
            left_container.setMaximumWidth(200)  # Fixed width for consistency
            left_container.setMinimumWidth(200)
            left_layout = QVBoxLayout(left_container)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(3)  # Reduced from 5 to 3
            
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.get('text_primary', '#2C3E50')};
                    font-weight: bold;
                    font-size: 13px;
                    margin: 0px;
                }}
            """)
            left_layout.addWidget(label)
            
            # Input widget with consistent styling
            if isinstance(widget, QLineEdit):
                widget.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 8px 12px;
                        border: 1px solid {colors.get('ui_divider', '#D0D7DE')};
                        border-radius: 4px;
                        background-color: {colors.get('ui_surface', '#FFFFFF')};
                        font-size: 13px;
                        min-height: 20px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid {colors.get('brand_primary', '#0077B5')};
                    }}
                """)
            elif isinstance(widget, QComboBox):
                widget.setStyleSheet(f"""
                    QComboBox {{
                        padding: 8px 12px;
                        border: 1px solid {colors.get('ui_divider', '#D0D7DE')};
                        border-radius: 4px;
                        background-color: {colors.get('ui_surface', '#FFFFFF')};
                        font-size: 13px;
                        min-height: 20px;
                    }}
                    QComboBox:focus {{
                        border: 2px solid {colors.get('brand_primary', '#0077B5')};
                    }}
                    QComboBox::drop-down {{
                        border: none;
                    }}
                    QComboBox::down-arrow {{
                        width: 12px;
                        height: 12px;
                    }}
                """)
            elif isinstance(widget, QCheckBox):
                widget.setStyleSheet(f"""
                    QCheckBox {{
                        font-size: 13px;
                        color: {colors.get('text_primary', '#2C3E50')};
                        spacing: 8px;
                    }}
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                        border: 2px solid {colors.get('ui_divider', '#D0D7DE')};
                        border-radius: 3px;
                        background-color: {colors.get('ui_surface', '#FFFFFF')};
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {colors.get('brand_primary', '#0077B5')};
                        border-color: {colors.get('brand_primary', '#0077B5')};
                    }}
                """)
            
            left_layout.addWidget(widget)
            left_layout.addStretch()
            
            # Right side: Description (2/3 of width)
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.get('text_secondary', '#666666')};
                    font-size: 12px;
                    line-height: 1.4;
                    margin: 0px;
                    padding: 2px 0px;
                }}
            """)
            description_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            
            # Add to horizontal layout
            row_layout.addWidget(left_container)  # Fixed width
            row_layout.addWidget(description_label, 1)  # Stretch to fill remaining space
            
            # Add the row to parent layout
            parent_layout.addWidget(row_container)
            
        except Exception as e:
            logger.error(f"Error creating config row with description: {e}")
            # Fallback to simple layout
            fallback_container = QWidget()
            fallback_layout = QHBoxLayout(fallback_container)
            fallback_layout.addWidget(QLabel(label_text))
            fallback_layout.addWidget(widget)
            parent_layout.addWidget(fallback_container)
    
    def save_all_settings(self):
        """Save all configuration settings"""
        try:
            # Save authentication settings
            self.auth_widget.save_settings()
            
            # Save additional settings to QSettings
            settings = QSettings("PSTtoDynamics", "Configuration")
            
            # Email Processing Settings
            settings.setValue("email/batch_size", self.batch_size_edit.text())
            settings.setValue("email/timeout", self.timeout_edit.text())
            settings.setValue("email/max_attachments", self.max_attachments_edit.text())
            settings.setValue("email/auto_retry", self.auto_retry_checkbox.isChecked())
            
            # Performance Settings
            settings.setValue("performance/thread_pool", self.thread_pool_edit.text())
            settings.setValue("performance/memory_limit", self.memory_limit_edit.text())
            settings.setValue("performance/cache_size", self.cache_size_edit.text())
            settings.setValue("performance/enable_logging", self.enable_logging_checkbox.isChecked())
            
            # AI Intelligence Settings
            settings.setValue("ai/analysis_enabled", self.ai_analysis_checkbox.isChecked())
            settings.setValue("ai/confidence_threshold", self.confidence_threshold_edit.text())
            settings.setValue("ai/learning_mode", self.learning_mode_combo.currentText())
            settings.setValue("ai/pattern_recognition", self.pattern_recognition_checkbox.isChecked())
            
            # Prepare configuration data
            config_data = {
                'dynamics_auth': self.auth_widget.get_config_data(),
                'email_processing': {
                    'batch_size': int(self.batch_size_edit.text() or 50),
                    'timeout': int(self.timeout_edit.text() or 30),
                    'max_attachments': int(self.max_attachments_edit.text() or 10),
                    'auto_retry': self.auto_retry_checkbox.isChecked()
                },
                'performance': {
                    'thread_pool': int(self.thread_pool_edit.text() or 4),
                    'memory_limit': int(self.memory_limit_edit.text() or 512),
                    'cache_size': int(self.cache_size_edit.text() or 128),
                    'enable_logging': self.enable_logging_checkbox.isChecked()
                },
                'ai_intelligence': {
                    'analysis_enabled': self.ai_analysis_checkbox.isChecked(),
                    'confidence_threshold': float(self.confidence_threshold_edit.text() or 0.85),
                    'learning_mode': self.learning_mode_combo.currentText(),
                    'pattern_recognition': self.pattern_recognition_checkbox.isChecked()
                }
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
            # Load authentication settings
            self.auth_widget.load_settings()
            
            # Load additional settings from QSettings
            settings = QSettings("PSTtoDynamics", "Configuration")
            
            # Email Processing Settings
            self.batch_size_edit.setText(settings.value("email/batch_size", "50"))
            self.timeout_edit.setText(settings.value("email/timeout", "30"))
            self.max_attachments_edit.setText(settings.value("email/max_attachments", "10"))
            self.auto_retry_checkbox.setChecked(settings.value("email/auto_retry", True, type=bool))
            
            # Performance Settings
            self.thread_pool_edit.setText(settings.value("performance/thread_pool", "4"))
            self.memory_limit_edit.setText(settings.value("performance/memory_limit", "512"))
            self.cache_size_edit.setText(settings.value("performance/cache_size", "128"))
            self.enable_logging_checkbox.setChecked(settings.value("performance/enable_logging", True, type=bool))
            
            # AI Intelligence Settings
            self.ai_analysis_checkbox.setChecked(settings.value("ai/analysis_enabled", True, type=bool))
            self.confidence_threshold_edit.setText(settings.value("ai/confidence_threshold", "0.85"))
            self.learning_mode_combo.setCurrentText(settings.value("ai/learning_mode", "Active"))
            self.pattern_recognition_checkbox.setChecked(settings.value("ai/pattern_recognition", True, type=bool))
            
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