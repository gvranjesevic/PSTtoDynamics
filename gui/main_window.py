"""
PST-to-Dynamics 365 Main GUI Window
===================================

Phase 5.1 Foundation: Main Application Window
Professional desktop interface for email import system with AI intelligence.
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
    QDialog, QDialogButtonBox, QLineEdit, QToolButton, QGroupBox, QFormLayout,
    QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QRect
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction

# Initialize logger after importing logging
logger = logging.getLogger(__name__)

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
    logger.warning(f"⚠️ Backend modules not available: {e}")

# Import application icon
try:
    from gui.resources.app_icon import get_app_icon, get_app_pixmap
    ICON_AVAILABLE = True
except ImportError:
    ICON_AVAILABLE = False
    logger.warning("⚠️ Application icon not available")

# Import thread manager
try:
    from thread_manager import ThreadManager
    THREAD_MANAGER_AVAILABLE = True
except ImportError:
    THREAD_MANAGER_AVAILABLE = False
    logger.warning("⚠️ Thread manager not available")

# Import theme manager
try:
    from gui.themes.theme_manager import ThemeManager, ThemeType, get_theme_manager
    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False
    logger.warning("⚠️ Theme manager not available")

# Import Windows overlay manager
try:
    from gui.windows_overlay_manager import create_overlay_manager
    OVERLAY_MANAGER_AVAILABLE = True
except ImportError:
    OVERLAY_MANAGER_AVAILABLE = False
    logger.warning("⚠️ Windows overlay manager not available")

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
    
    def apply_theme(self, theme_definition):
        """Apply theme to navigation sidebar"""
        colors = theme_definition['colors']
        
        # Apply theme to sidebar container
        self.setStyleSheet(f"""
            NavigationSidebar {{
                background: {colors['ui_surface']};
                border-right: 1px solid {colors['ui_border']};
                border-radius: 8px;
            }}
        """)
        
        # Re-setup UI to apply new theme colors
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the navigation sidebar interface"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'ui_surface': '#FFFFFF',
                'ui_border': '#D0D7DE',
                'text_primary': '#2C3E50',
                'ui_surfaceHover': '#ECF0F1',
                'ui_surfaceHoverAlt': '#D5DBDB',
                'brand_primary': '#0077B5',
                'text_inverse': '#FFFFFF',
                'brand_primaryHover': '#005885',
                'brand_primaryActive': '#004A70'
            }
        
        self.setFixedWidth(200)  # Reduced from 220 to 200 for more compact design
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            NavigationSidebar {{
                background: {colors['ui_surface']};
                border-right: 1px solid {colors['ui_border']};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 15, 10, 10)  # Slightly more top margin for balance
        
        # Clear existing layout if re-applying theme
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
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
            btn = self.create_nav_button(nav_id, icon, title, description, colors)
            self.nav_buttons[nav_id] = btn
            layout.addWidget(btn)
        
        # Spacer to push content to top
        layout.addStretch()
        
        # Set initial selection
        self.select_nav_item("dashboard")
        
    def create_nav_button(self, nav_id: str, icon: str, title: str, description: str, colors: dict) -> QPushButton:
        """Create a professional navigation button"""
        btn = QPushButton()
        btn.setFixedHeight(50)  # Reduced from 60 to 50 for more compact design
        btn.setToolTip(description)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Button text with icon
        btn.setText(f"{icon}  {title}")
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        
        # Style the button with dynamic colors
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 8px 12px;
                border: none;
                border-radius: 6px;
                background-color: transparent;
                color: {colors['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {colors['ui_surfaceHover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['ui_surfaceHoverAlt']};
            }}
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
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'text_primary': '#2C3E50',
                'ui_surfaceHover': '#ECF0F1',
                'ui_surfaceHoverAlt': '#D5DBDB',
                'brand_primary': '#0077B5',
                'text_inverse': '#FFFFFF',
                'brand_primaryHover': '#005885',
                'brand_primaryActive': '#004A70'
            }
        
        # Reset all buttons
        for btn in self.nav_buttons.values():
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: transparent;
                    color: {colors['text_primary']};
                }}
                QPushButton:hover {{
                    background-color: {colors['ui_surfaceHover']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['ui_surfaceHoverAlt']};
                }}
            """)
        
        # Highlight selected button
        if nav_id in self.nav_buttons:
            self.nav_buttons[nav_id].setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: {colors['brand_primary']};
                    color: {colors['text_inverse']};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['brand_primaryHover']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['brand_primaryActive']};
                }}
            """)


class ContentArea(QWidget):
    """Main content area that displays different modules"""
    
    def __init__(self):
        super().__init__()
        self.active_widgets = []
        self.setup_ui()
    
    def apply_theme(self, theme_definition):
        """Apply theme to content area"""
        colors = theme_definition['colors']
        
        # Update content area styling
        self.setStyleSheet(f"""
            ContentArea {{
                background: {colors['ui_canvas']};
                color: {colors['text_primary']};
            }}
        """)
    
    def setup_ui(self):
        """Setup the content area interface"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'text_primary': '#2C3E50',
                'text_tertiary': '#7F8C8D'
            }
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove excessive margins
        # Removed any initial spacing to avoid top gap
        
        # Welcome message
        welcome_label = QLabel("Welcome to PST to Dynamics 365")
        welcome_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        welcome_label.setStyleSheet(f"color: {colors['text_primary']}; margin-bottom: 10px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Select a module from the sidebar to get started")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet(f"color: {colors['text_tertiary']}; margin-bottom: 30px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(welcome_label)
        self.layout.addWidget(subtitle_label)
        self.layout.addStretch()
    
    def clear_layout(self):
        """Remove all items (including spacers/stretches) from the layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
    
    def show_module(self, module_id: str):
        """Display the specified module"""
        # Clear current content
        self.cleanup_active_widgets()
        
        # Clear layout completely (widgets + spacers)
        self.clear_layout()
        
        # Show appropriate module
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
        else:
            # Default welcome screen
            self.setup_ui()
    
    def show_dashboard(self):
        """Show the main dashboard"""
        # Dashboard header (standardized to match Settings panel)
        header = self.create_dashboard_header()
        self.layout.addWidget(header)
        
        # Set up dashboard content
        self.setup_dashboard_content()
    
    def create_dashboard_header(self) -> QWidget:
        """Create dashboard header (standardized to match Settings panel)"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'brand_primary': '#0077B5',
                'brand_primaryBorder': '#006097',
                'text_inverse': '#FFFFFF'
            }
        
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background-color: {colors['brand_primary']};
            border-bottom: 1px solid {colors['brand_primaryBorder']};
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Dashboard")
        title.setStyleSheet(f"""
            color: {colors['text_inverse']};
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def setup_dashboard_content(self):
        """Set up dashboard content"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'brand_primary': '#0077B5'
            }
        
        # Status cards with proper margins
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(20, 0, 20, 0)
        status_layout.setSpacing(15)
        
        # System status card
        system_card = self.create_status_card("System Status", "✅ Online", colors['brand_primary'])
        status_layout.addWidget(system_card)
        
        # Database status card
        db_card = self.create_status_card("Database", "✅ Connected", colors['brand_primary'])
        status_layout.addWidget(db_card)
        
        # Last sync card
        sync_card = self.create_status_card("Last Sync", "🔄 Never", colors['brand_primary'])
        status_layout.addWidget(sync_card)
        
        self.layout.addWidget(status_widget)
        self.layout.addStretch()
    
    def create_status_card(self, title: str, status: str, color: str) -> QFrame:
        """Create a status card widget"""
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            # Fallback colors if theme manager not available
            colors = {
                'ui_surface': '#FFFFFF'
            }
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['ui_surface']};
                border: 2px solid {color} !important;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color};")
        
        status_label = QLabel(status)
        status_label.setFont(QFont("Segoe UI", 14))
        status_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(status_label)
        
        return card
    
    def show_import_placeholder(self):
        """Show import wizard placeholder"""
        try:
            from gui.widgets.import_wizard import ImportWizard
            
            # Create and add import wizard directly
            wizard = ImportWizard()
            wizard.wizard_completed.connect(self.on_import_completed)
            wizard.wizard_cancelled.connect(self.on_import_cancelled)
            self.active_widgets.append(wizard)
            self.layout.addWidget(wizard)
            
        except ImportError:
            # Fallback placeholder
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'text_tertiary': '#7f8c8d'}
            
            placeholder = QLabel("📧 Import Wizard\n\nComing Soon...")
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']};")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder)
            self.layout.addStretch()
    
    def on_import_completed(self, success: bool, data: dict):
        """Handle import completion"""
        if success:
            QMessageBox.information(self, "Import Complete", 
                                  f"Successfully imported {data.get('count', 0)} emails!")
        else:
            QMessageBox.warning(self, "Import Failed", 
                              f"Import failed: {data.get('error', 'Unknown error')}")
    
    def on_import_cancelled(self):
        """Handle import cancellation"""
        QMessageBox.information(self, "Import Cancelled", "Import operation was cancelled.")
    
    def cleanup_active_widgets(self):
        """Clean up active widgets to prevent memory leaks"""
        for widget in self.active_widgets:
            try:
                # Stop any running threads or timers
                if hasattr(widget, 'stop'):
                    widget.stop()
                if hasattr(widget, 'close'):
                    widget.close()
                if hasattr(widget, 'deleteLater'):
                    widget.deleteLater()
            except Exception as e:
                logger.warning(f"Error cleaning up widget: {e}")
        
        self.active_widgets.clear()
    
    def show_analytics_placeholder(self):
        """Show analytics dashboard placeholder"""
        try:
            from gui.widgets.analytics_dashboard import AnalyticsDashboard
            
            # Create and add analytics dashboard directly
            dashboard = AnalyticsDashboard()
            self.active_widgets.append(dashboard)
            self.layout.addWidget(dashboard)
            
        except ImportError:
            # Fallback placeholder
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'text_tertiary': '#7f8c8d'}
            
            placeholder = QLabel("📈 Analytics Dashboard\n\nComing Soon...")
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']};")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder)
            self.layout.addStretch()
    
    def show_ai_placeholder(self):
        """Show AI intelligence dashboard placeholder"""
        try:
            from gui.widgets.ai_intelligence_dashboard import AIIntelligenceDashboard
            
            # Create and add AI dashboard directly
            dashboard = AIIntelligenceDashboard()
            self.active_widgets.append(dashboard)
            self.layout.addWidget(dashboard)
            
        except ImportError:
            # Fallback placeholder
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'text_tertiary': '#7f8c8d'}
            
            placeholder = QLabel("🧠 AI Intelligence Dashboard\n\nComing Soon...")
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']};")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder)
            self.layout.addStretch()
    
    def show_contacts_placeholder(self):
        """Show contacts management placeholder"""
        try:
            from gui.widgets.contact_management_dashboard import ContactManagementDashboard
            
            # Create and add contact dashboard directly
            dashboard = ContactManagementDashboard()
            self.active_widgets.append(dashboard)
            self.layout.addWidget(dashboard)
            
        except ImportError:
            # Fallback placeholder
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'text_tertiary': '#7f8c8d'}
            
            placeholder = QLabel("👥 Contact Management\n\nComing Soon...")
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']};")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder)
            self.layout.addStretch()
    
    def show_settings_placeholder(self):
        """Embed Configuration Manager directly in the content area with a fixed external footer."""
        try:
            # Import Configuration Manager
            from gui.widgets.configuration_manager import ConfigurationManager
            
            # ----- Create container for embedded settings -----
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            
            # ----- Create ConfigurationManager -----
            config_manager = ConfigurationManager()
            config_manager.configuration_changed.connect(self.on_configuration_changed)
            
            # Detach the internal footer so we can manage it externally
            if hasattr(config_manager, "footer_widget"):
                footer = config_manager.footer_widget
                # Remove from internal layout & re-parent to container
                if hasattr(config_manager, "layout") and config_manager.layout() is not None:
                    config_manager.layout().removeWidget(footer)
                footer.setParent(container)
                footer.setFixedHeight(80)  # Match Import Wizard's 80px
                footer.setMinimumHeight(80)
                footer.setMaximumHeight(80)
                # Ensure the footer's size policy is fixed vertically
                footer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            else:
                footer = None  # Fallback (should not happen)
            
            # Ensure the scroll area inside ConfigurationManager expands
            config_manager.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # ----- Wrap ConfigurationManager in a scroll area -----
            from PyQt6.QtWidgets import QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            scroll_area.setWidget(config_manager)
            
            # Add scroll area then footer
            container_layout.addWidget(scroll_area, 1)  # stretch=1
            if footer:
                container_layout.addWidget(footer, 0)  # stretch=0 (fixed)
            
            # Ensure scroll area stretches properly
            container_layout.setStretchFactor(scroll_area, 1)
            
            # Keep footer on top of Z-order during resize events
            if footer:
                def raise_footer():
                    footer.raise_()
                container.resizeEvent = lambda event, orig=container.resizeEvent: (orig(event) if orig else None, raise_footer())
                raise_footer()
            
            # ----- Add container to content layout -----
            self.layout.addWidget(container)
            self.active_widgets.append(container)
            self.active_widgets.append(config_manager)
            if footer:
                self.active_widgets.append(footer)
            
            # Force immediate layout update
            self.layout.update()
            self.layout.activate()
            
        except Exception as e:
            from PyQt6.QtWidgets import QLabel
            import traceback
            traceback.print_exc()
            placeholder = QLabel(f"⚙️ Settings could not be loaded.\n\nError: {e}")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'state_error': '#e74c3c'}
            placeholder.setStyleSheet(f"color: {colors['state_error']}; font-size: 14px;")
            self.layout.addWidget(placeholder)
            self.layout.addStretch()
    
    def show_settings_info_message(self):
        """Show an informational message about settings access"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.setSpacing(20)
        
        # Settings icon and title
        title = QLabel("⚙️ System Settings")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            colors = {'brand_primary': '#0077B5'}
        title.setStyleSheet(f"color: {colors['brand_primary']}; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Settings can be accessed through:\n\n"
            "• Tools → Settings (menu bar)\n"
            "• Ctrl+, (keyboard shortcut)\n"
            "• Click the Settings button in the sidebar"
        )
        instructions.setFont(QFont("Segoe UI", 14))
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            colors = {'text_primary': '#2c3e50'}
        instructions.setStyleSheet(f"color: {colors['text_primary']}; line-height: 1.6;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(instructions)
        
        # Features list
        features = QLabel(
            "Configure:\n"
            "✓ Dynamics 365 Authentication\n"
            "✓ Email Processing Settings\n"
            "✓ Performance Options\n"
            "✓ AI Intelligence Settings"
        )
        features.setFont(QFont("Segoe UI", 12))
        features.setStyleSheet("color: #666; margin-top: 20px;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(features)
        
        self.layout.addWidget(info_widget)
    
    def force_footer_positioning(self, container, config_manager):
        """Legacy method - no longer needed with separate window approach"""
        pass
    
    def on_configuration_changed(self, config_data: dict):
        """Handle configuration changes"""
        logger.info(f"Configuration updated: {config_data}")
        QMessageBox.information(self, "Configuration Updated", 
                              "Configuration has been saved successfully.")
    
    def show_sync_monitoring_dashboard(self):
        """Show the sync monitoring dashboard"""
        try:
            # Create dashboard without sync engine for now (will be connected later)
            dashboard = SyncMonitoringDashboard()
            self.active_widgets.append(dashboard)
            self.layout.addWidget(dashboard)
            
        except ImportError:
            # Fallback placeholder
            # Get current theme colors for dynamic styling
            if THEME_MANAGER_AVAILABLE:
                colors = get_theme_manager().get_theme_definition()['colors']
            else:
                colors = {'text_tertiary': '#7f8c8d'}
            
            placeholder = QLabel("🔄 Sync Monitor Dashboard\n\nComing Soon...")
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']};")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder)
            self.layout.addStretch()


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
                # Check system health
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Get current theme colors for dynamic styling
                if THEME_MANAGER_AVAILABLE:
                    colors = get_theme_manager().get_theme_definition()['colors']
                else:
                    colors = {'state_error': '#e74c3c', 'state_success': '#27ae60'}
                
                if cpu_percent > 80 or memory_percent > 80:
                    self.status_updated.emit("System Load High", colors['state_error'])
                else:
                    self.status_updated.emit("System Ready", colors['state_success'])
                
                self.msleep(5000)  # Check every 5 seconds
                
            except Exception as e:
                logger.warning(f"Status monitor error: {e}")
                # Get current theme colors for dynamic styling
                if THEME_MANAGER_AVAILABLE:
                    colors = get_theme_manager().get_theme_definition()['colors']
                else:
                    colors = {'state_warning': '#f39c12'}
                self.status_updated.emit("Monitor Error", colors['state_warning'])
                self.msleep(10000)  # Wait longer on error
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.status_monitor = None
        self.overlay_manager = None
        
        # Initialize theme manager and set LinkedIn Blue theme
        try:
            from gui.themes.theme_manager import ThemeManager, ThemeType
            self.theme_manager = ThemeManager()
            self.theme_manager.set_theme(ThemeType.LINKEDIN_BLUE)
            logger.info("✅ LinkedIn Blue theme applied")
        except ImportError:
            logger.warning("⚠️ Theme manager not available")
        
        self.setup_ui()
        
        # Initialize Windows overlay manager after UI setup
        if OVERLAY_MANAGER_AVAILABLE:
            self.overlay_manager = create_overlay_manager(self)
            if self.overlay_manager:
                logger.info("✅ Windows overlay manager initialized - Voice Access conflicts will be handled")
                # Connect window state changes to handle maximize behavior
                self.connect_window_state_events()
            else:
                logger.warning("⚠️ Could not initialize overlay manager")
        
        self.show_welcome_if_first_run()
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("PST-to-Dynamics 365 - AI-Powered Email Import")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Handle Windows overlays (Voice Access, etc.)
        self.handle_windows_overlays()
        
        # Set application icon if available
        if ICON_AVAILABLE:
            self.setWindowIcon(get_app_icon())
        
        # Create central widget and main layout
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout (sidebar + content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create and setup main components
        self.navigation_sidebar = NavigationSidebar()
        self.content_area = ContentArea()
        self.content_area.setContentsMargins(0, 0, 0, 0)
        if hasattr(self.content_area, 'layout'):
            layout = self.content_area.layout
            if layout is not None:
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
        
        # Add components to layout
        main_layout.addWidget(self.navigation_sidebar)
        main_layout.addWidget(self.content_area, 1)
        
        # Connect navigation signals
        self.navigation_sidebar.navigate_to.connect(self.on_navigate)
        
        # Setup additional UI components
        self.setup_menu_bar()
        # self.setup_toolbar()  # Commented out - redundant with left panel and menus
        self.setup_status_bar()
        
        # Apply current theme
        if hasattr(self, 'theme_manager'):
            self.apply_current_theme()
    
    def handle_windows_overlays(self):
        """Handle Windows system overlays like Voice Access"""
        try:
            # Move window below potential overlay area
            screen = self.screen().availableGeometry()
            
            # Calculate safe positioning (accounting for 60px overlay at top)
            safe_top = max(100, 60)  # At least 60px from top for Voice Access
            safe_left = 50
            safe_width = min(1400, screen.width() - 100)
            safe_height = min(900, screen.height() - safe_top - 50)
            
            # Set window geometry with safe positioning
            self.setGeometry(safe_left, safe_top, safe_width, safe_height)
            
            # Set window flags to handle overlays better
            from PyQt6.QtCore import Qt
            flags = self.windowFlags()
            
            # Ensure window stays in front when focused
            flags |= Qt.WindowType.WindowStaysOnTopHint
            
            # But allow normal window behavior
            flags &= ~Qt.WindowType.WindowStaysOnTopHint  # Remove always on top
            
            logger.info("✅ Window positioning adjusted for Windows overlays")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not adjust window for overlays: {e}")

    def apply_current_theme(self):
        """Apply the current theme to the main window"""
        try:
            if THEME_MANAGER_AVAILABLE:
                theme_def = get_theme_manager().get_theme_definition()
                if theme_def:
                    colors = theme_def.get('colors', {})
                    # Apply comprehensive LinkedIn Blue theme styling
                    self.setStyleSheet(f"""
                        QMainWindow {{
                            background-color: {colors.get('ui_canvas', '#F3F6F8')};
                            color: {colors.get('text_primary', '#2C3E50')};
                            font-family: 'Segoe UI', Arial, sans-serif;
                            font-size: 14px;
                        }}
                        
                        /* Menu Bar Styling */
                        QMenuBar {{
                            background-color: {colors.get('ui_surface', '#FFFFFF')};
                            color: {colors.get('text_primary', '#2C3E50')};
                            border-bottom: 1px solid {colors.get('ui_border', '#D0D7DE')};
                            padding: 4px 8px;
                            font-weight: 500;
                        }}
                        
                        QMenuBar::item {{
                            background-color: transparent;
                            color: {colors.get('text_primary', '#2C3E50')};
                            padding: 8px 12px;
                            border-radius: 4px;
                            margin: 2px;
                        }}
                        
                        QMenuBar::item:selected {{
                            background-color: {colors.get('brand_primary', '#0077B5')};
                            color: {colors.get('text_inverse', '#FFFFFF')};
                        }}
                        
                        QMenuBar::item:pressed {{
                            background-color: {colors.get('brand_primaryHover', '#005885')};
                            color: {colors.get('text_inverse', '#FFFFFF')};
                        }}
                        
                        /* Menu Dropdown Styling */
                        QMenu {{
                            background-color: {colors.get('ui_surface', '#FFFFFF')};
                            color: {colors.get('text_primary', '#2C3E50')};
                            border: 1px solid {colors.get('ui_border', '#D0D7DE')};
                            border-radius: 6px;
                            padding: 4px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        }}
                        
                        QMenu::item {{
                            background-color: transparent;
                            color: {colors.get('text_primary', '#2C3E50')};
                            padding: 8px 16px;
                            border-radius: 4px;
                            margin: 1px;
                        }}
                        
                        QMenu::item:selected {{
                            background-color: {colors.get('brand_primary', '#0077B5')};
                            color: {colors.get('text_inverse', '#FFFFFF')};
                        }}
                        
                        QMenu::separator {{
                            height: 1px;
                            background-color: {colors.get('ui_border', '#D0D7DE')};
                            margin: 4px 8px;
                        }}
                        
                        /* Status Bar Styling */
                        QStatusBar {{
                            background-color: {colors.get('ui_surface', '#FFFFFF')};
                            color: {colors.get('text_secondary', '#666666')};
                            border-top: 1px solid {colors.get('ui_border', '#D0D7DE')};
                            padding: 4px 8px;
                        }}
                    """)
                    
                    # Apply theme to child widgets
                    if hasattr(self.navigation_sidebar, 'apply_theme'):
                        self.navigation_sidebar.apply_theme(theme_def)
                    if hasattr(self.content_area, 'apply_theme'):
                        self.content_area.apply_theme(theme_def)
                    
                    logger.info(f"Applied theme: {theme_def.get('name', 'LinkedIn Blue')}")
                else:
                    logger.warning("⚠️ Could not get theme definition")
            else:
                # Fallback styling if no theme manager
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: #F3F6F8;
                        color: #2C3E50;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 14px;
                    }
                    
                    /* Menu Bar Styling */
                    QMenuBar {
                        background-color: #FFFFFF;
                        color: #2C3E50;
                        border-bottom: 1px solid #D0D7DE;
                        padding: 4px 8px;
                        font-weight: 500;
                    }
                    
                    QMenuBar::item {
                        background-color: transparent;
                        color: #2C3E50;
                        padding: 8px 12px;
                        border-radius: 4px;
                        margin: 2px;
                    }
                    
                    QMenuBar::item:selected {
                        background-color: #0077B5;
                        color: #FFFFFF;
                    }
                    
                    QMenuBar::item:pressed {
                        background-color: #005885;
                        color: #FFFFFF;
                    }
                    
                    /* Menu Dropdown Styling */
                    QMenu {
                        background-color: #FFFFFF;
                        color: #2C3E50;
                        border: 1px solid #D0D7DE;
                        border-radius: 6px;
                        padding: 4px;
                    }
                    
                    QMenu::item {
                        background-color: transparent;
                        color: #2C3E50;
                        padding: 8px 16px;
                        border-radius: 4px;
                        margin: 1px;
                    }
                    
                    QMenu::item:selected {
                        background-color: #0077B5;
                        color: #FFFFFF;
                    }
                    
                    QMenu::separator {
                        height: 1px;
                        background-color: #D0D7DE;
                        margin: 4px 8px;
                    }
                """)
                logger.info("Applied fallback LinkedIn Blue styling")
        except Exception as e:
            logger.error(f"❌ Error applying theme: {e}")

    def on_theme_changed(self, theme_name: str):
        """Handle theme change events"""
        try:
            self.apply_current_theme()
            logger.info(f"Theme changed to: {theme_name}")
        except Exception as e:
            logger.error(f"❌ Error handling theme change: {e}")

    def connect_window_state_events(self):
        """Connect window state change events for overlay management"""
        try:
            # We'll handle window state changes in the changeEvent method
            logger.info("✅ Window state event handling connected")
        except Exception as e:
            logger.error(f"❌ Error connecting window state events: {e}")

    def changeEvent(self, event):
        """Handle window state changes (minimize, maximize, restore)"""
        try:
            super().changeEvent(event)
            
            # Handle window state changes for overlay management
            if hasattr(self, 'overlay_manager') and self.overlay_manager:
                if event.type() == event.Type.WindowStateChange:
                    current_state = self.windowState()
                    
                    # Check if maximized
                    if current_state & Qt.WindowState.WindowMaximized:
                        logger.info("🔧 Window maximized - eliminating Voice Access gap")
                        # Pause overlay monitoring to prevent repositioning
                        if hasattr(self.overlay_manager, 'pause_monitoring'):
                            self.overlay_manager.pause_monitoring()
                        # Use a timer to ensure the maximize operation completes first
                        QTimer.singleShot(100, self.handle_maximized_state)
                    
                    # Check if restored to normal (not maximized, not minimized)
                    elif current_state == Qt.WindowState.WindowNoState:
                        logger.info("🔧 Window restored - resuming normal overlay management")
                        # Resume overlay monitoring for normal windows
                        if hasattr(self.overlay_manager, 'resume_monitoring'):
                            self.overlay_manager.resume_monitoring()
                        # Resume normal overlay management with a slight delay
                        QTimer.singleShot(100, self.overlay_manager.check_overlay_conflicts)
                    
                    # Log other state changes for debugging
                    elif current_state & Qt.WindowState.WindowMinimized:
                        logger.debug("🔧 Window minimized")
                        
        except Exception as e:
            logger.error(f"❌ Error handling window state change: {e}")
            import traceback
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")

    def showMaximized(self):
        """Override showMaximized to eliminate Voice Access gap"""
        try:
            # Call the parent showMaximized first
            super().showMaximized()
            
            # Then immediately adjust to eliminate Voice Access gap
            QTimer.singleShot(50, self.eliminate_voice_access_gap)
            
        except Exception as e:
            logger.error(f"❌ Error in showMaximized override: {e}")
            super().showMaximized()  # Fallback

    def eliminate_voice_access_gap(self):
        """Eliminate the Voice Access gap for maximized windows with widget protection"""
        try:
            if self.isMaximized():
                screen = self.screen()
                if screen:
                    # Get the full screen geometry (not just available)
                    full_screen = screen.geometry()
                    available_rect = screen.availableGeometry()
                    
                    # Create maximized rectangle that goes to the very top
                    maximized_rect = QRect(
                        available_rect.left(),    # Respect left boundary
                        0,                        # Start from absolute top (y=0)
                        available_rect.width(),   # Use available width
                        available_rect.bottom()   # Use available bottom
                    )
                    
                    # Set the geometry to eliminate the gap
                    self.setGeometry(maximized_rect)
                    logger.info(f"✅ Voice Access gap eliminated - window geometry: {maximized_rect}")
                    
                    # CRITICAL: Protect embedded ConfigurationManager after geometry change
                    QTimer.singleShot(50, self.protect_embedded_widgets)
                    
        except Exception as e:
            logger.error(f"❌ Error eliminating Voice Access gap: {e}")
    
    def protect_embedded_widgets(self):
        """Protect embedded widgets from geometry manipulation effects"""
        try:
            # Access active_widgets from content_area, not MainWindow
            if hasattr(self, 'content_area') and hasattr(self.content_area, 'active_widgets'):
                # Find and protect any embedded ConfigurationManager widgets
                for widget in self.content_area.active_widgets:
                    # Check if widget is a ConfigurationManager or contains one
                    if hasattr(widget, 'footer_widget'):
                        # Direct ConfigurationManager
                        self.force_footer_positioning(self.content_area, widget)
                    elif hasattr(widget, 'findChild'):
                        # Search for ConfigurationManager in container
                        from gui.widgets.configuration_manager import ConfigurationManager
                        config_manager = widget.findChild(ConfigurationManager)
                        if config_manager:
                            self.force_footer_positioning(widget, config_manager)
                
                logger.debug("🛡️ Embedded widget protection completed")
            else:
                logger.debug("No content area or active widgets found")
        except Exception as e:
            logger.warning(f"Embedded widget protection error: {e}")

    def handle_maximized_state(self):
        """Handle maximized state to eliminate Voice Access gap"""
        try:
            if self.isMaximized() and hasattr(self, 'overlay_manager'):
                self.eliminate_voice_access_gap()
                    
        except Exception as e:
            logger.error(f"❌ Error handling maximized state: {e}")

    def showEvent(self, event):
        """Handle window show event to ensure proper positioning"""
        super().showEvent(event)
        
        # Only reposition if window is not maximized
        if not self.isMaximized():
            # Ensure window is not obscured by Windows overlays
            try:
                screen_rect = self.screen().availableGeometry()
                window_rect = self.geometry()
                
                # Check if window is too close to top (Voice Access area)
                if window_rect.top() < 60:
                    # Move window down to avoid overlay
                    self.move(window_rect.left(), 80)
                    logger.info("🔧 Window repositioned to avoid Windows overlay")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not check window positioning: {e}")
        else:
            logger.debug("🔒 Skipping showEvent repositioning - window is maximized")
    
    def setup_menu_bar(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Import", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.on_navigate("import"))
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.on_navigate("dashboard"))
        view_menu.addAction(dashboard_action)
        
        analytics_action = QAction("&Analytics", self)
        analytics_action.triggered.connect(lambda: self.on_navigate("analytics"))
        view_menu.addAction(analytics_action)
        
        contacts_action = QAction("&Contacts", self)
        contacts_action.triggered.connect(lambda: self.on_navigate("contacts"))
        view_menu.addAction(contacts_action)
        
        sync_monitor_action = QAction("&Sync Monitor", self)
        sync_monitor_action.triggered.connect(lambda: self.on_navigate("sync_monitor"))
        view_menu.addAction(sync_monitor_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.on_navigate("settings"))
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        welcome_action = QAction("&Welcome", self)
        welcome_action.triggered.connect(self.show_welcome_dialog)
        help_menu.addAction(welcome_action)
        
        manual_action = QAction("&User Manual", self)
        manual_action.triggered.connect(self.show_user_manual)
        help_menu.addAction(manual_action)
        
        faq_action = QAction("&FAQ", self)
        faq_action.triggered.connect(self.show_faq_dialog)
        help_menu.addAction(faq_action)
        
        feedback_action = QAction("Send &Feedback", self)
        feedback_action.triggered.connect(self.show_feedback_dialog)
        help_menu.addAction(feedback_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # def setup_toolbar(self):
    #     """Setup the application toolbar - COMMENTED OUT: Redundant with left panel and menus"""
    #     toolbar = self.addToolBar("Main")
    #     toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    #     
    #     # Quick action buttons
    #     if ICONS_AVAILABLE:
    #         try:
    #             import_action = QAction(qta.icon('fa5s.file-import'), "Import", self)
    #             dashboard_action = QAction(qta.icon('fa5s.tachometer-alt'), "Dashboard", self)
    #             settings_action = QAction(qta.icon('fa5s.cog'), "Settings", self)
    #         except:
    #             # Fallback to text-only
    #             import_action = QAction("📧 Import", self)
    #             dashboard_action = QAction("📊 Dashboard", self)
    #             settings_action = QAction("⚙️ Settings", self)
    #     else:
    #         import_action = QAction("📧 Import", self)
    #         dashboard_action = QAction("📊 Dashboard", self)
    #         settings_action = QAction("⚙️ Settings", self)
    #     
    #     import_action.triggered.connect(lambda: self.on_navigate("import"))
    #     dashboard_action.triggered.connect(lambda: self.on_navigate("dashboard"))
    #     settings_action.triggered.connect(lambda: self.on_navigate("settings"))
    #     
    #     toolbar.addAction(import_action)
    #     toolbar.addAction(dashboard_action)
    #     toolbar.addSeparator()
    #     toolbar.addAction(settings_action)
    
    def setup_status_bar(self):
        """Setup the application status bar"""
        self.status_bar = self.statusBar()
        
        # Status message
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Version info
        version_label = QLabel("v1.0.0")
        # Get current theme colors for dynamic styling
        if THEME_MANAGER_AVAILABLE:
            colors = get_theme_manager().get_theme_definition()['colors']
        else:
            colors = {'text_secondary': '#6c757d'}
        version_label.setStyleSheet(f"color: {colors['text_secondary']}; font-size: 10px;")
        self.status_bar.addPermanentWidget(version_label)
    
    def start_monitoring(self):
        """Start background system monitoring"""
        self.status_monitor = SystemStatusMonitor()
        self.status_monitor.status_updated.connect(self.update_status)
        self.status_monitor.start()
    
    def update_status(self, message: str, color: str):
        """Update status bar"""
        self.status_message.setText(message)
        self.status_message.setStyleSheet(f"color: {color};")
    
    def on_navigate(self, module_id: str):
        """Handle navigation to different modules"""
        self.content_area.show_module(module_id)
        self.navigation_sidebar.select_nav_item(module_id)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>PST to Dynamics 365</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Company:</b> Dynamique Solutions</p>
        <br>
        <p>A professional desktop application for importing, synchronizing, and managing 
        contacts and emails between PST files and Microsoft Dynamics 365.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>Advanced sync engine with conflict resolution</li>
        <li>AI-powered analytics and insights</li>
        <li>Professional monitoring dashboard</li>
        <li>Comprehensive contact management</li>
        </ul>
        <br>
        <p><i>Built with PyQt6 and modern design principles.</i></p>
        """
        
        QMessageBox.about(self, "About PST to Dynamics 365", about_text)
    
    def show_welcome_if_first_run(self):
        """Show welcome dialog on first run"""
        try:
            # Check if this is first run
            settings_file = os.path.join(os.path.expanduser("~"), ".pst_dynamics_settings.json")
            if not os.path.exists(settings_file):
                # First run - show welcome dialog
                QTimer.singleShot(1000, self.show_welcome_dialog)  # Delay to ensure window is shown
                
                # Create settings file to mark as not first run
                try:
                    with open(settings_file, 'w') as f:
                        json.dump({"first_run": False, "version": "1.0.0"}, f)
                except Exception as e:
                    logger.warning(f"Could not create settings file: {e}")
        except Exception as e:
            logger.warning(f"Error checking first run: {e}")
    
    def show_welcome_dialog(self):
        """Show welcome dialog"""
        try:
            welcome_dialog = WelcomeDialog(self)
            welcome_dialog.exec()
        except Exception as e:
            logger.warning(f"Could not show welcome dialog: {e}")
    
    def show_user_manual(self):
        """Show user manual"""
        try:
            # Try to open user manual file or URL
            manual_text = """
            <h2>PST to Dynamics 365 User Manual</h2>
            <h3>Getting Started</h3>
            <p>1. Configure your Dynamics 365 connection in Settings</p>
            <p>2. Select your PST file using the Import Wizard</p>
            <p>3. Review and start the import process</p>
            <p>4. Monitor progress in the Sync Monitor</p>
            
            <h3>Configuration</h3>
            <p>Use environment variables or the Settings panel to configure:</p>
            <ul>
            <li>DYNAMICS_USERNAME - Your Dynamics 365 username</li>
            <li>DYNAMICS_PASSWORD - Your password (use keyring for security)</li>
            <li>DYNAMICS_TENANT_DOMAIN - Your organization domain</li>
            <li>DYNAMICS_CLIENT_ID - Application client ID</li>
            </ul>
            
            <h3>Support</h3>
            <p>For additional help, use the Send Feedback option in the Help menu.</p>
            """
            
            dialog = QDialog(self)
            dialog.setWindowTitle("User Manual")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setHtml(manual_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing user manual: {e}")
            QMessageBox.information(self, "User Manual", 
                                  "User manual is not available. Please check the documentation folder.")
    
    def show_faq_dialog(self):
        """Show FAQ dialog"""
        faq_text = """
        <h2>Frequently Asked Questions</h2>
        
        <h3>Q: How do I configure my Dynamics 365 connection?</h3>
        <p>A: Go to Settings and enter your Dynamics 365 credentials, or use environment variables for security.</p>
        
        <h3>Q: What PST file formats are supported?</h3>
        <p>A: The application supports standard Outlook PST files (.pst) created by Microsoft Outlook.</p>
        
        <h3>Q: How do I handle import conflicts?</h3>
        <p>A: Use the Sync Monitor to view and resolve conflicts using various resolution strategies.</p>
        
        <h3>Q: Can I import large PST files?</h3>
        <p>A: Yes, the application supports batch processing and memory optimization for large files.</p>
        
        <h3>Q: How do I get support?</h3>
        <p>A: Use the Send Feedback option in the Help menu to report issues or request assistance.</p>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Frequently Asked Questions")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setHtml(faq_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def show_feedback_dialog(self):
        """Show feedback dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Send Feedback")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel("Please describe your feedback, bug report, or feature request:")
        layout.addWidget(instructions)
        
        # Feedback text area
        feedback_edit = QTextEdit()
        feedback_edit.setPlaceholderText("Enter your feedback here...")
        layout.addWidget(feedback_edit)
        
        # Email field
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email (optional):"))
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("your.email@example.com")
        email_layout.addWidget(email_edit)
        layout.addLayout(email_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(lambda: self.submit_feedback(feedback_edit.toPlainText(), email_edit.text(), dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def submit_feedback(self, feedback, email, dlg):
        # Placeholder: In production, send to server or save locally
        logger.info(f"Feedback submitted: {feedback[:100]}... (Email: {email})")
        QMessageBox.information(self, "Feedback Sent", 
                              "Thank you for your feedback! We'll review it and get back to you if needed.")
        dlg.accept()
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop monitoring thread
        if self.status_monitor:
            self.status_monitor.stop()
        
        # Clean up overlay manager
        if self.overlay_manager:
            self.overlay_manager.cleanup()
            logger.info("✅ Overlay manager cleanup completed")
        
        # Clean up active widgets
        self.content_area.cleanup_active_widgets()
        
        # Clean up all registered threads
        if THREAD_MANAGER_AVAILABLE:
            try:
                if hasattr(self, 'thread_manager') and self.thread_manager:
                    self.thread_manager.cleanup_all_threads(timeout=5.0)
                else:
                    thread_manager = ThreadManager()
                    thread_manager.cleanup_all_threads(timeout=5.0)
                logger.info("✅ All threads cleaned up successfully")
            except Exception as e:
                logger.warning(f"⚠️ Thread cleanup warning: {e}")
        
        event.accept()


class PSTDynamicsApp(QApplication):
    """Main application class"""
    
    def __init__(self):
        super().__init__(sys.argv)
        self.setup_app()
    
    def setup_app(self):
        """Setup application properties"""
        self.setApplicationName("PST to Dynamics 365")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Dynamique Solutions")
        self.setOrganizationDomain("dynamique.com")
    
    def run(self):
        """Run the application"""
        try:
            # Create and show main window
            window = MainWindow()
            window.show()
            
            # Start event loop
            return self.exec()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            QMessageBox.critical(None, "Application Error", 
                               f"A critical error occurred:\n{str(e)}")
            return 1


def main():
    """Main entry point"""
    try:
        # Suppress Qt CSS warnings before anything else
        import os
        os.environ['QT_LOGGING_RULES'] = 'qt.qpa.stylesheet.parser.warning=false;qt.qpa.window.warning=false;qt.qpa.gl.warning=false;qt.qpa.xcb.warning=false'
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create and run application
        app = PSTDynamicsApp()
        return app.run()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 