"""
PST-to-Dynamics 365 Main GUI Window
===================================

logger = logging.getLogger(__name__)

Phase 5.1 Foundation: Main Application Window
Professional desktop interface for email import sys
 import loggingtem with AI intelligence.
"""

import sys


import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QToolBar, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QProgressBar, QSizePolicy, QTextEdit,
    QDialog, QDialogButtonBox, QLineEdit, QToolButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction

# Import qtawesome for professional icons
try:
    import qtawesome as qta
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False
    logger.warning("⚠️ QtAwesome not available - using default icons")

# Import existing backend modules (Phase 1-4 remain unchanged)
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    import config
    from email_importer import EmailImporter
    try:
        from phase4_integration import Phase4IntelligentSystem
        PHASE4_AVAILABLE = True
    except ImportError:
        PHASE4_AVAILABLE = False
        logger.warning("⚠️ Phase 4 AI not available in GUI mode")
    
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    logger.warning("⚠️ Backend modules not available: {e}")

# Import application icon
try:
    from gui.resources.app_icon import get_app_icon, get_app_pixmap
    ICON_AVAILABLE = True
except ImportError:
    ICON_AVAILABLE = False
    logger.warning("⚠️ Application icon not available")

# Add import for the sync monitoring dashboard
from gui.widgets.sync_monitoring_dashboard import SyncMonitoringDashboard
from sync.sync_engine import SyncEngine
from gui.widgets.welcome_dialog import WelcomeDialog


class NavigationSidebar(QFrame):
    """Professional navigation sidebar with module selection"""
    
    # Signal emitted when navigation item is clicked
    navigate_to = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the navigation sidebar interface"""
        self.setFixedWidth(220)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Application title/logo area
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        app_title = QLabel("PST to Dynamics 365")
        app_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #2c3e50; margin: 10px 0px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        app_subtitle = QLabel("AI-Powered Email Import")
        app_subtitle.setFont(QFont("Segoe UI", 9))
        app_subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        layout.addWidget(title_frame)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "Dashboard", "System overview and status"),
            ("import", "📧", "Import Wizard", "Guided email import process"),
            ("analytics", "📈", "Analytics", "Import analytics and reports"),
            ("ai", "🧠", "AI Intelligence", "Machine learning insights"),
            ("contacts", "👥", "Contacts", "Contact management"),
            ("sync_monitor", "🔄", "Sync Monitor", "Monitor sync operations"),
            ("settings", "⚙️", "Settings", "System configuration")
        ]
        
        for nav_id, icon, title, description in nav_items:
            btn = self.create_nav_button(nav_id, icon, title, description)
            self.nav_buttons[nav_id] = btn
            layout.addWidget(btn)
        
        # Spacer to push content to top
        layout.addStretch()
        
        # Status indicator at bottom
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        self.status_label = QLabel("System Ready")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setStyleSheet("color: #27ae60; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_frame)
        
        # Set initial selection
        self.select_nav_item("dashboard")
        
    def create_nav_button(self, nav_id: str, icon: str, title: str, description: str) -> QPushButton:
        """Create a professional navigation button"""
        btn = QPushButton()
        btn.setFixedHeight(60)
        btn.setToolTip(description)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Button text with icon
        btn.setText(f"{icon}  {title}")
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        
        # Style the button
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
            QPushButton:pressed {
                background-color: #d5dbdb;
            }
        """)
        
        # Connect click event
        btn.clicked.connect(lambda: self.on_nav_click(nav_id))
        
        return btn
    
    def on_nav_click(self, nav_id: str):
        """Handle navigation button click"""
        self.select_nav_item(nav_id)
        self.navigate_to.emit(nav_id)
    
    def select_nav_item(self, nav_id: str):
        """Visually select a navigation item"""
        # Reset all buttons
        for btn in self.nav_buttons.values():
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 8px;
                    background-color: transparent;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #ecf0f1;
                }
                QPushButton:pressed {
                    background-color: #d5dbdb;
                }
            """)
        
        # Highlight selected button
        if nav_id in self.nav_buttons:
            self.nav_buttons[nav_id].setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 8px;
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
    
    def update_status(self, status: str, color: str = "#27ae60"):
        """Update the status indicator"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; padding: 5px;")


class ContentArea(QWidget):
    """Main content area that displays different modules"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_module = None
        
    def setup_ui(self):
        """Setup the content area"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Content header
        self.header_label = QLabel("Welcome to PST-to-Dynamics 365")
        self.header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        self.subtitle_label = QLabel("AI-powered email import system")
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        
        layout.addWidget(self.header_label)
        layout.addWidget(self.subtitle_label)
        
        # Content body (placeholder for now)
        self.content_body = QLabel("Select a module from the sidebar to get started.")
        self.content_body.setFont(QFont("Segoe UI", 11))
        self.content_body.setStyleSheet("color: #34495e; padding: 20px;")
        self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.content_body)
        layout.addStretch()
        
    def show_module(self, module_id: str):
        """Display a specific module"""
        # Clean up any active widgets first
        self.cleanup_active_widgets()
        
        self.current_module = module_id
        
        module_info = {
            "dashboard": ("System Dashboard", "Overview and system status"),
            "import": ("Import Wizard", "Guided email import process"),
            "analytics": ("Analytics Dashboard", "Import analytics and reports"),
            "ai": ("AI Intelligence", "Machine learning insights and optimization"),
            "contacts": ("Contact Management", "Manage Dynamics 365 contacts"),
            "sync_monitor": ("Sync Monitoring", "Monitor sync operations and resolve conflicts"),
            "settings": ("System Settings", "Configure application settings")
        }
        
        if module_id in module_info:
            title, description = module_info[module_id]
            self.header_label.setText(title)
            self.subtitle_label.setText(description)
            
            # Module-specific content (placeholder for Phase 5.2+)
            if module_id == "dashboard":
                self.show_dashboard()
            elif module_id == "import":
                self.show_import_placeholder()
            elif module_id == "analytics":
                self.show_analytics_placeholder()
            elif module_id == "ai":
                self.show_ai_placeholder()
            elif module_id == "contacts":
                self.show_contacts_placeholder()
            elif module_id == "sync_monitor":
                self.show_sync_monitoring_dashboard()
            elif module_id == "settings":
                self.show_settings_placeholder()
    
    def show_dashboard(self):
        """Show the dashboard module (Phase 5.1 basic version)"""
        import sys
        import logging
        dashboard_info = f"""
        <div style="font-family: Segoe UI; color: #2c3e50;">
        <h3>System Status</h3>
        <p><b>✅ Phase 1-4 Backend:</b> {"Available" if BACKEND_AVAILABLE else "Not Available"}</p>
        <p><b>🧠 AI Intelligence:</b> {"Available" if PHASE4_AVAILABLE else "Not Available"}</p>
        <p><b>🎨 GUI Framework:</b> PyQt6 Loaded</p>
        
        <h3>Quick Actions</h3>
        <p>• Use the Import Wizard to start importing emails</p>
        <p>• View Analytics for import insights</p>
        <p>• Access AI Intelligence for smart recommendations</p>
        <p>• Manage Contacts in Dynamics 365</p>
        
        <h3>Phase 5.1 Foundation Complete</h3>
        <p>✅ Main window framework</p>
        <p>✅ Navigation sidebar</p>
        <p>✅ Status monitoring</p>
        <p>✅ Menu system</p>
        </div>
        """
        
        self.content_body.setText(dashboard_info)
        self.content_body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    def show_import_placeholder(self):
        """Show the Import Wizard (Phase 5.2)"""
        # Clear existing content
        if hasattr(self, 'import_wizard'):
            return  # Already showing
        
        # Hide the header and subtitle to free up space
        self.header_label.hide()
        self.subtitle_label.hide()
        
        # Import the wizard
        try:
            from gui.widgets.import_wizard import ImportWizard
            
            # Replace content body with import wizard
            self.content_body.hide()
            
            # Create and add import wizard
            self.import_wizard = ImportWizard()
            self.import_wizard.wizard_completed.connect(self.on_import_completed)
            self.import_wizard.wizard_cancelled.connect(self.on_import_cancelled)
            
            # Add to layout
            layout = self.layout()
            layout.insertWidget(2, self.import_wizard)  # Insert after subtitle
            
        except ImportError as e:
            self.content_body.setText(f"❌ Import Wizard not available: {e}\n\nFeatures:\n• Step-by-step import process\n• Real-time progress tracking\n• AI optimization recommendations\n• Error handling and recovery")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def on_import_completed(self, success: bool, data: dict):
        """Handle import wizard completion"""
        if success:
            message = f"✅ Import completed successfully!\n\nFile: {data.get('file_name', 'Unknown')}\nStatus: {data.get('final_status', 'Completed')}"
        else:
            message = f"❌ Import was not completed.\n\nStatus: {data.get('final_status', 'Failed')}"
        
        # Clean up any active widgets
        self.cleanup_active_widgets()
        
        # Show result and return to dashboard
        self.content_body.setText(message)
        self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_body.show()
    
    def on_import_cancelled(self):
        """Handle import wizard cancellation"""
        # Clean up any active widgets
        self.cleanup_active_widgets()
        
        self.content_body.setText("📧 Import cancelled by user.\n\nYou can start a new import anytime using the Import Wizard.")
        self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_body.show()
    
    def cleanup_active_widgets(self):
        """Clean up any active widgets (wizard, config manager, etc.)"""
        # Show header and subtitle again
        self.header_label.show()
        self.subtitle_label.show()
        
        # Show content body again
        self.content_body.show()
        
        # Remove import wizard
        if hasattr(self, 'import_wizard'):
            self.import_wizard.hide()
            self.layout().removeWidget(self.import_wizard)
            self.import_wizard.deleteLater()
            del self.import_wizard
        
        # Remove configuration manager
        if hasattr(self, 'config_manager'):
            self.config_manager.hide()
            self.layout().removeWidget(self.config_manager)
            self.config_manager.deleteLater()
            del self.config_manager
        
        # Remove analytics dashboard
        if hasattr(self, 'analytics_dashboard'):
            self.analytics_dashboard.hide()
            self.layout().removeWidget(self.analytics_dashboard)
            self.analytics_dashboard.deleteLater()
            del self.analytics_dashboard
        
        # Remove AI intelligence dashboard
        if hasattr(self, 'ai_dashboard'):
            self.ai_dashboard.hide()
            self.layout().removeWidget(self.ai_dashboard)
            self.ai_dashboard.deleteLater()
            del self.ai_dashboard
        
        # Remove contact management dashboard
        if hasattr(self, 'contact_dashboard'):
            self.contact_dashboard.hide()
            self.layout().removeWidget(self.contact_dashboard)
            self.contact_dashboard.deleteLater()
            del self.contact_dashboard
        
        # Remove sync monitoring dashboard
        if hasattr(self, 'sync_monitoring_dashboard'):
            self.sync_monitoring_dashboard.hide()
            self.layout().removeWidget(self.sync_monitoring_dashboard)
            self.sync_monitoring_dashboard.deleteLater()
            del self.sync_monitoring_dashboard
    
    def show_analytics_placeholder(self):
        """Show Analytics Dashboard (Phase 5.4)"""
        try:
            from gui.widgets.analytics_dashboard import AnalyticsDashboard
            
            # Clean up any existing widgets
            self.cleanup_active_widgets()
            
            # Hide the header and subtitle to free up space
            self.header_label.hide()
            self.subtitle_label.hide()
            
            # Create and show analytics dashboard
            self.analytics_dashboard = AnalyticsDashboard()
            
            # Replace content with analytics dashboard
            self.content_body.hide()
            
            # Add to layout
            layout = self.layout()
            layout.insertWidget(2, self.analytics_dashboard)  # Insert after subtitle
            
            logger.info("📈 Phase 5.4 Analytics Dashboard loaded successfully")
            
        except ImportError as e:
            logger.warning("⚠️ Analytics Dashboard not available: {e}")
            self.content_body.setText("📈 Analytics Dashboard\n\nError loading dashboard module.\nPlease check installation.")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            logger.error("❌ Error loading Analytics Dashboard: {e}")
            self.content_body.setText(f"📈 Analytics Dashboard\n\nError: {str(e)}")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def show_ai_placeholder(self):
        """Show AI Intelligence Dashboard (Phase 5.5)"""
        try:
            from gui.widgets.ai_intelligence_dashboard import AIIntelligenceDashboard
            
            # Clean up any existing widgets
            self.cleanup_active_widgets()
            
            # Hide the header and subtitle to free up space
            self.header_label.hide()
            self.subtitle_label.hide()
            
            # Create and show AI intelligence dashboard
            self.ai_dashboard = AIIntelligenceDashboard()
            
            # Replace content with AI dashboard
            self.content_body.hide()
            
            # Add to layout
            layout = self.layout()
            layout.insertWidget(2, self.ai_dashboard)  # Insert after subtitle
            
            logger.debug("🤖 Phase 5.5 AI Intelligence Dashboard loaded successfully")
            
        except ImportError as e:
            logger.warning("⚠️ AI Intelligence Dashboard not available: {e}")
            self.content_body.setText("🤖 AI Intelligence Dashboard\n\nError loading AI dashboard module.\nPlease check Phase 4 components installation.")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            logger.error("❌ Error loading AI Intelligence Dashboard: {e}")
            self.content_body.setText(f"🤖 AI Intelligence Dashboard\n\nError: {str(e)}")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def show_contacts_placeholder(self):
        """Show Contact Management Dashboard (Phase 5.6)"""
        try:
            from gui.widgets.contact_management_dashboard import ContactManagementDashboard
            
            # Clean up any existing widgets
            self.cleanup_active_widgets()
            
            # Hide the header and subtitle to free up space
            self.header_label.hide()
            self.subtitle_label.hide()
            
            # Create and show contact management dashboard
            self.contact_dashboard = ContactManagementDashboard()
            
            # Replace content with contact dashboard
            self.content_body.hide()
            
            # Add to layout
            layout = self.layout()
            layout.insertWidget(2, self.contact_dashboard)  # Insert after subtitle
            
            logger.info("👥 Phase 5.6 Contact Management Dashboard loaded successfully")
            
        except ImportError as e:
            logger.warning("⚠️ Contact Management Dashboard not available: {e}")
            self.content_body.setText("👥 Contact Management Dashboard\n\nError loading contact dashboard module.\nPlease check contact management components installation.")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            logger.error("❌ Error loading Contact Management Dashboard: {e}")
            self.content_body.setText(f"👥 Contact Management Dashboard\n\nError: {str(e)}")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def show_settings_placeholder(self):
        """Show the Configuration Manager (Phase 5.3)"""
        # Clear existing content
        if hasattr(self, 'config_manager'):
            return  # Already showing
        
        # Hide the header and subtitle to free up space
        self.header_label.hide()
        self.subtitle_label.hide()
        
        # Import the configuration manager
        try:
            from gui.widgets.configuration_manager import ConfigurationManager
            
            # Replace content body with configuration manager
            self.content_body.hide()
            
            # Create and add configuration manager
            self.config_manager = ConfigurationManager()
            self.config_manager.configuration_changed.connect(self.on_configuration_changed)
            
            # Add to layout
            layout = self.layout()
            layout.insertWidget(2, self.config_manager)  # Insert after subtitle
            
        except ImportError as e:
            self.content_body.setText(f"❌ Configuration Manager not available: {e}\n\nFeatures:\n• Visual configuration editor\n• Authentication setup\n• Import behavior settings\n• Phase 2-4 advanced options")
            self.content_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def on_configuration_changed(self, config_data: dict):
        """Handle configuration changes"""
        logger.debug("Configuration updated:")
        for section, data in config_data.items():
            logger.debug("  {section}: {data}")
        
        # Update status to indicate configuration was saved
        self.update_status("Configuration updated successfully", "#27ae60")

    def show_sync_monitoring_dashboard(self):
        self.cleanup_active_widgets()
        self.header_label.hide()
        self.subtitle_label.hide()
        self.content_body.hide()
        self.sync_engine = SyncEngine()
        self.sync_monitoring_dashboard = SyncMonitoringDashboard(self.sync_engine)
        # Add inline help button
        help_btn = QToolButton()
        help_btn.setText("?")
        help_btn.setToolTip("Learn more about sync monitoring and conflict resolution.")
        help_btn.clicked.connect(lambda: QMessageBox.information(self, "Sync Monitor Help", "The Sync Monitoring Dashboard provides real-time sync metrics, conflict resolution, and logs. Use the tabs to view metrics, resolve conflicts, and review logs."))
        layout = self.layout()
        layout.insertWidget(2, help_btn)
        layout.insertWidget(3, self.sync_monitoring_dashboard)


class SystemStatusMonitor(QThread):
    """Background thread to monitor system status"""
    
    status_updated = pyqtSignal(str, str)  # message, color
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        """Monitor system status in background"""
        while self.running:
            try:
                # Check backend availability
                if BACKEND_AVAILABLE:
                    self.status_updated.emit("System Ready", "#27ae60")
                else:
                    self.status_updated.emit("Backend Unavailable", "#e74c3c")
                
                # Sleep for 5 seconds before next check
                self.msleep(5000)
                
            except Exception as e:
                self.status_updated.emit("Status Error", "#e74c3c")
                self.msleep(10000)  # Wait longer if error
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    """Main application window for PST-to-Dynamics 365 GUI"""
    
    def __init__(self):
        super().__init__()
        self.status_monitor = None
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.start_monitoring()
        self.show_welcome_if_first_run()
        
    def setup_ui(self):
        """Setup the main window interface"""
        self.setWindowTitle("PST to Dynamics 365 - AI Email Import System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon
        try:
            from gui.resources.app_icon import get_app_icon
            self.setWindowIcon(get_app_icon(32))
        except ImportError:
            pass  # Fallback to default icon
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Navigation sidebar
        self.sidebar = NavigationSidebar()
        self.sidebar.navigate_to.connect(self.on_navigate)
        
        # Main content area
        self.content_area = ContentArea()
        
        # Add to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_area)
        
        # Set splitter proportions (sidebar: content = 1:4)
        splitter.setSizes([220, 980])
        splitter.setCollapsible(0, False)  # Don't allow sidebar to collapse
        
        layout.addWidget(splitter)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            
            /* Menu Bar Styling */
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 4px 8px;
                font-family: "Segoe UI";
                font-size: 14px;
                color: #2c3e50;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #e9ecef;
            }
            QMenuBar::item:pressed {
                background-color: #3498db;
                color: white;
            }
            
            /* Menu Dropdown Styling */
            QMenu {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 6px 0px;
                font-family: "Segoe UI";
                font-size: 14px;
                color: #2c3e50;
            }
            QMenu::item {
                padding: 8px 20px;
                margin: 1px;
                color: #2c3e50;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ecf0f1;
                margin: 4px 10px;
            }
            
            /* Toolbar Styling */
            QToolBar {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 6px;
                spacing: 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
                font-family: "Segoe UI";
                font-size: 13px;
                color: #2c3e50;
            }
            QToolBar QToolButton:hover {
                background-color: #e9ecef;
            }
            QToolBar QToolButton:pressed {
                background-color: #3498db;
                color: white;
            }
            
            /* Splitter Styling */
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 1px;
            }
            QSplitter::handle:hover {
                background-color: #95a5a6;
            }
        """)
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_import_action = QAction("&New Import...", self)
        new_import_action.setShortcut("Ctrl+N")
        new_import_action.setStatusTip("Start a new email import")
        new_import_action.triggered.connect(lambda: self.on_navigate("import"))
        file_menu.addAction(new_import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.triggered.connect(lambda: self.on_navigate("dashboard"))
        view_menu.addAction(dashboard_action)
        
        analytics_action = QAction("&Analytics", self)
        analytics_action.setShortcut("Ctrl+2")
        analytics_action.triggered.connect(lambda: self.on_navigate("analytics"))
        view_menu.addAction(analytics_action)
        
        ai_action = QAction("&AI Intelligence", self)
        ai_action.setShortcut("Ctrl+3")
        ai_action.triggered.connect(lambda: self.on_navigate("ai"))
        view_menu.addAction(ai_action)
        
        sync_monitor_action = QAction("&Sync Monitor", self)
        sync_monitor_action.setShortcut("Ctrl+4")
        sync_monitor_action.triggered.connect(lambda: self.on_navigate("sync_monitor"))
        view_menu.addAction(sync_monitor_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.on_navigate("settings"))
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        help_menu.addSeparator()
        welcome_action = QAction("Show Welcome Screen", self)
        welcome_action.triggered.connect(self.show_welcome_dialog)
        help_menu.addAction(welcome_action)
        manual_action = QAction("User Manual", self)
        manual_action.triggered.connect(self.show_user_manual)
        help_menu.addAction(manual_action)
        faq_action = QAction("FAQ", self)
        faq_action.triggered.connect(self.show_faq_dialog)
        help_menu.addAction(faq_action)
        feedback_action = QAction("Send Feedback", self)
        feedback_action.triggered.connect(self.show_feedback_dialog)
        help_menu.addAction(feedback_action)
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        
        # Quick action buttons with text labels
        import_action = QAction("📧 Import", self)
        import_action.setStatusTip("Start email import")
        import_action.triggered.connect(lambda: self.on_navigate("import"))
        toolbar.addAction(import_action)
        
        analytics_action = QAction("📈 Analytics", self)
        analytics_action.setStatusTip("View analytics")
        analytics_action.triggered.connect(lambda: self.on_navigate("analytics"))
        toolbar.addAction(analytics_action)
        
        ai_action = QAction("🧠 AI", self)
        ai_action.setStatusTip("AI Intelligence")
        ai_action.triggered.connect(lambda: self.on_navigate("ai"))
        toolbar.addAction(ai_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setStatusTip("Application settings")
        settings_action.triggered.connect(lambda: self.on_navigate("settings"))
        toolbar.addAction(settings_action)
        
        # Add stretch to push items to the left
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = self.statusBar()
        
        # Main status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Add spacer
        self.status_bar.addPermanentWidget(QLabel(""), 1)
        
        # Backend status
        self.backend_status = QLabel("Backend: Checking...")
        self.status_bar.addPermanentWidget(self.backend_status)
        
        # Phase indicator
        phase_label = QLabel("Phase 5.1 Foundation")
        phase_label.setStyleSheet("font-weight: bold; color: #3498db; padding: 0 10px;")
        self.status_bar.addPermanentWidget(phase_label)
    
    def start_monitoring(self):
        """Start system status monitoring"""
        self.status_monitor = SystemStatusMonitor()
        self.status_monitor.status_updated.connect(self.update_status)
        self.status_monitor.start()
    
    def update_status(self, message: str, color: str):
        """Update the status display"""
        self.sidebar.update_status(message, color)
        self.backend_status.setText(f"Backend: {message}")
        self.backend_status.setStyleSheet(f"color: {color};")
    
    def on_navigate(self, module_id: str):
        """Handle navigation to different modules"""
        self.content_area.show_module(module_id)
        self.status_label.setText(f"Viewing {module_id.title()}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h3>PST to Dynamics 365</h3>
        <p><b>Version:</b> 1.0.0 (Production Release)</p>
        <p><b>Company:</b> Dynamique Solutions</p>
        <p><b>AI-Powered Email Import System</b></p>
        <br>
        <p>A comprehensive solution for importing emails from PST files 
        into Microsoft Dynamics 365 with advanced AI intelligence.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>Bidirectional sync and conflict resolution</li>
        <li>Professional desktop GUI</li>
        <li>AI-powered pattern recognition</li>
        <li>Smart import optimization</li>
        <li>Predictive analytics</li>
        <li>Enterprise-grade interface</li>
        </ul>
        <br>
        <p><b>Developer:</b> gvranjesevic@dynamique.com</p>
        """
        QMessageBox.about(self, "About PST to Dynamics 365", about_text)
    
    def show_welcome_if_first_run(self):
        config_path = os.path.join(os.path.expanduser('~'), '.psttodyn_config.json')
        first_run = True
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    cfg = json.load(f)
                    first_run = cfg.get('first_run', True)
            except Exception:
                first_run = True
        if first_run:
            dlg = WelcomeDialog(self)
            dlg.exec()
            # Mark as not first run
            try:
                with open(config_path, 'w') as f:
                    json.dump({'first_run': False}, f)
            except Exception:
                pass

    def show_welcome_dialog(self):
        dlg = WelcomeDialog(self)
        dlg.exec()
    
    def show_user_manual(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("User Manual")
        dlg.setMinimumSize(700, 600)
        layout = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)
        try:
            with open("USER_MANUAL.md", "r", encoding="utf-8") as f:
                text.setPlainText(f.read())
        except Exception as e:
            text.setPlainText(f"Could not load user manual: {e}")
        layout.addWidget(text)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()

    def show_faq_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Frequently Asked Questions (FAQ)")
        dlg.setMinimumSize(500, 400)
        layout = QVBoxLayout(dlg)
        faq_text = QTextEdit()
        faq_text.setReadOnly(True)
        faq_text.setPlainText("""
Q: How do I import emails from a PST file?
A: Use the Import Wizard from the navigation sidebar.

Q: How do I resolve sync conflicts?
A: Go to the Sync Monitor and use the Conflict Resolution tab.

Q: Where can I find logs and metrics?
A: The Sync Monitoring Dashboard provides real-time logs and metrics.

Q: How do I get help?
A: Use this Help menu or contact support.
        """)
        layout.addWidget(faq_text)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()

    def show_feedback_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Send Feedback")
        dlg.setMinimumSize(400, 300)
        layout = QVBoxLayout(dlg)
        label = QLabel("We value your feedback! Please enter your comments below:")
        layout.addWidget(label)
        feedback_edit = QTextEdit()
        layout.addWidget(feedback_edit)
        email_label = QLabel("Your email (optional):")
        layout.addWidget(email_label)
        email_edit = QLineEdit()
        layout.addWidget(email_edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(lambda: self.submit_feedback(feedback_edit.toPlainText(), email_edit.text(), dlg))
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        dlg.exec()

    def submit_feedback(self, feedback, email, dlg):
        # Placeholder: In production, send to server or save locally
        logger.debug("Feedback received: {feedback}\nFrom: {email}")
        QMessageBox.information(self, "Thank you!", "Your feedback has been received.")
        dlg.accept()

    def closeEvent(self, event):
        """Handle application close"""
        if self.status_monitor:
            self.status_monitor.stop()
        event.accept()


class PSTDynamicsApp(QApplication):
    """Main application class"""
    
    def __init__(self):
        super().__init__(sys.argv)
        self.setup_app()
        self.main_window = None
        
    def setup_app(self):
        """Setup application properties"""
        self.setApplicationName("PST to Dynamics 365")
        self.setApplicationVersion("Phase 5.1")
        self.setOrganizationName("Dynamique Solutions")
        self.setOrganizationDomain("dynamique.com")
    
    def run(self):
        """Run the application"""
        self.main_window = MainWindow()
        self.main_window.show()
        
        logger.info("🚀 PST-to-Dynamics 365 GUI Application Started")
        logger.info("📊 Phase 5.1 Foundation - Main Window Framework")
        logger.info("✅ All systems ready for testing and review")
        
        return self.exec()


def main():
    """Main entry point"""
    logger.debug("=" * 60)
    logger.debug("🎯 PST-to-Dynamics 365 Phase 5.1 Foundation")
    logger.debug("🖥️ Professional Desktop GUI Application")
    logger.debug("=" * 60)
    
    try:
        app = PSTDynamicsApp()
        return app.run()
    except Exception as e:
        logger.error("❌ Application startup error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 