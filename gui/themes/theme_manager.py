"""
Phase 5.7 Theme Management System
=================================

Advanced theme engine supporting multiple themes with real-time switching,
system integration, and enterprise customization capabilities.

Features:
- Light/Dark theme with system detection
- Corporate branding theme
- High contrast accessibility theme
- Real-time theme switching without restart
- Custom theme creation and persistence
- Component-wide styling propagation

Author: AI Assistant
Phase: 5.7
"""

import sys
import logging
import os

logger = logging.getLogger(__name__)
from typing import Dict, Any, Optional, Callable
from enum import Enum
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QPalette, QColor
from gui.themes.linkedin_blue_theme import LinkedInBlueTheme  # NEW IMPORT for LinkedIn Blue spec application

class ThemeType(Enum):
    """Available theme types"""
    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    HIGH_CONTRAST = "high_contrast"
    LINKEDIN_BLUE = "linkedin_blue"
    CUSTOM = "custom"

class ThemeManager(QObject):
    """
    Central theme management system for the entire application.
    Handles theme switching, persistence, and propagation to all components.
    """
    
    # Signals
    theme_changed = pyqtSignal(str)  # Emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Dynamique", "PSTtoDynamics365")
        self.current_theme = ThemeType.LINKEDIN_BLUE
        self.registered_widgets = []
        self.theme_definitions = {}
        
        # Initialize theme definitions
        self._load_theme_definitions()
        
        # Set up system theme detection
        self._setup_system_detection()
        
        # Load saved theme preference
        self._load_saved_theme()
    
    def _load_theme_definitions(self):
        """Load all available theme definitions"""
        
        # Light Theme Definition
        self.theme_definitions[ThemeType.LIGHT] = {
            'name': 'Light Theme',
            'description': 'Clean light theme with professional appearance',
            'colors': {
                'primary': '#1e40af',
                'secondary': '#3b82f6', 
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'neutral': '#6b7280',
                'background': '#ffffff',
                'surface': '#f8fafc',
                'text_primary': '#1e293b',
                'text_secondary': '#64748b',
                'border': '#e2e8f0',
                'shadow': 'rgba(0, 0, 0, 0.1)'
            },
            'fonts': {
                'primary': 'Segoe UI',
                'code': 'JetBrains Mono',
                'size_base': 14,
                'size_small': 12,
                'size_large': 16,
                'size_title': 24
            },
            'spacing': {
                'xs': 4,
                'sm': 8,
                'md': 16,
                'lg': 24,
                'xl': 32,
                'xxl': 48
            }
        }
        
        # Dark Theme Definition
        self.theme_definitions[ThemeType.DARK] = {
            'name': 'Dark Theme',
            'description': 'Modern dark theme for reduced eye strain',
            'colors': {
                'primary': '#3b82f6',
                'secondary': '#60a5fa',
                'success': '#34d399',
                'warning': '#fbbf24',
                'error': '#f87171',
                'neutral': '#9ca3af',
                'background': '#1e293b',
                'surface': '#334155',
                'text_primary': '#f1f5f9',
                'text_secondary': '#cbd5e1',
                'border': '#475569',
                'shadow': 'rgba(0, 0, 0, 0.3)'
            },
            'fonts': self.theme_definitions[ThemeType.LIGHT]['fonts'],
            'spacing': self.theme_definitions[ThemeType.LIGHT]['spacing']
        }
        
        # Corporate Theme Definition
        self.theme_definitions[ThemeType.CORPORATE] = {
            'name': 'Corporate Theme',
            'description': 'Professional corporate branding theme',
            'colors': {
                'primary': '#1e40af',
                'secondary': '#2563eb',
                'success': '#059669',
                'warning': '#d97706',
                'error': '#dc2626',
                'neutral': '#6b7280',
                'background': '#ffffff',
                'surface': '#f9fafb',
                'text_primary': '#111827',
                'text_secondary': '#6b7280',
                'border': '#d1d5db',
                'shadow': 'rgba(0, 0, 0, 0.12)'
            },
            'fonts': self.theme_definitions[ThemeType.LIGHT]['fonts'],
            'spacing': self.theme_definitions[ThemeType.LIGHT]['spacing']
        }
        
        # High Contrast Theme Definition (Accessibility)
        self.theme_definitions[ThemeType.HIGH_CONTRAST] = {
            'name': 'High Contrast',
            'description': 'High contrast theme for accessibility',
            'colors': {
                'primary': '#0000ff',
                'secondary': '#4169e1',
                'success': '#008000',
                'warning': '#ff8c00',
                'error': '#ff0000',
                'neutral': '#000000',
                'background': '#ffffff',
                'surface': '#f0f0f0',
                'text_primary': '#000000',
                'text_secondary': '#333333',
                'border': '#000000',
                'shadow': 'rgba(0, 0, 0, 0.8)'
            },
            'fonts': {
                'primary': 'Segoe UI',
                'code': 'JetBrains Mono',
                'size_base': 16,  # Larger for accessibility
                'size_small': 14,
                'size_large': 18,
                'size_title': 28
            },
            'spacing': {
                'xs': 6,   # Larger spacing for accessibility
                'sm': 12,
                'md': 20,
                'lg': 28,
                'xl': 36,
                'xxl': 52
            }
        }
        
        # LinkedIn Blue Theme Definition
        self.theme_definitions[ThemeType.LINKEDIN_BLUE] = {
            'name': 'LinkedIn Blue',
            'description': 'Professional LinkedIn-inspired blue theme with modern aesthetics',
            'colors': {
                # Brand Colors
                'brand_primary': '#0077B5',
                'brand_primaryHover': '#005885',
                'brand_primaryActive': '#004A70',
                'brand_secondary': '#005885',
                'brand_accent': '#00A0DC',
                'brand_primaryBorder': '#006097',
                'brand_primaryHoverAlt': '#004471',
                'brand_darkHover': '#004471',
                
                # UI Surface Colors
                'ui_surface': '#FFFFFF',
                'ui_surfaceAlt': '#F9FAFB',
                'ui_canvas': '#F3F6F8',
                'ui_surfaceLight': '#F8F9FA',
                'ui_surfaceHover': '#ECF0F1',
                'ui_surfaceHoverLight': '#E9ECEF',
                'ui_surfaceHoverAlt': '#E8F4FD',
                'ui_disabled': '#CCCCCC',
                'ui_disabledDark': '#95A5A6',
                'ui_buttonDark': '#6C757D',
                'ui_buttonDarker': '#5A6268',
                'ui_shadow': 'rgba(0,119,181,0.15)',
                'ui_focus': '#0077B5',
                
                # Border Colors
                'ui_border': '#D0D7DE',
                'ui_divider': '#DEE2E6',
                'ui_gridline': '#F0F0F0',
                'border_light': '#E8EBED',
                'border_muted': '#BDC3C7',
                'border_gridlineAlt': '#E1E4E8',
                
                # Text Colors
                'text_primary': '#2C3E50',
                'text_secondary': '#666666',
                'text_tertiary': '#7F8C8D',
                'text_inverse': '#FFFFFF',
                'text_muted': '#999999',
                'text_dim': '#6C757D',
                'text_dark': '#495057',
                'text_neutral': '#495057',
                'text_black': '#000000',
                'text_link': '#0077B5',
                'text_darkBackground': '#2C3E50',
                'text_lightOnDark': '#ECF0F1',
                
                # State Colors
                'state_success': '#28A745',
                'state_successHover': '#229954',
                'state_successButton': '#27AE60',
                'state_successDeep': '#196F3D',
                'state_warning': '#F59E0B',
                'state_error': '#C0392B',
                'state_errorButton': '#E74C3C',
                'state_errorAlt': '#EF4444',
                'state_info': '#3B82F6',
                'state_successAlt': '#10B981',
                'legacy_success': '#2ECC71',
                
                # Section Colors
                'section_infoBorder': '#17A2B8',
                'section_infoBg': '#E7F8FF',
                'text_infoDark': '#0C5460',
                'section_successBg': '#D4EDDA',
                'section_successBgAlt': '#E8F8F5',
                'text_successDark': '#155724',
                'section_warningBorder': '#E67E22',
                'section_warningBg': '#FEF9E7',
                'text_warningDark': '#D68910',
                'section_errorBorder': '#DC3545',
                'section_errorBg': '#F8D7DA',
                'text_errorDark': '#721C24',
                'section_aiBorder': '#8E44AD',
                'section_aiBg': '#FAF9FF',
                'text_aiPurple': '#6C3483',
                
                # Legacy compatibility
                'primary': '#0077B5',
                'secondary': '#005885',
                'accent': '#00A0DC',
                'success': '#057642',
                'warning': '#F5C75D',
                'error': '#CC1016',
                'neutral': '#666666',
                'background': '#F3F6F8',
                'surface': '#FFFFFF',
                'surface_secondary': '#F9FAFB',
                'border': '#D0D7DE',
                'shadow': 'rgba(0, 119, 181, 0.15)',
                'hover': '#004471',
                'active': '#003A5C',
                'focus': '#0077B5',
                'disabled': '#CCCCCC'
            },
            'fonts': {
                'primary': 'Segoe UI',
                'secondary': 'Arial',
                'code': 'Consolas',
                'size_base': 14,
                'size_small': 12,
                'size_large': 16,
                'size_title': 20,
                'size_heading': 18,
                'weight_normal': 400,
                'weight_medium': 500,
                'weight_bold': 600
            },
            'spacing': {
                'xs': 4,
                'sm': 8,
                'md': 16,
                'lg': 24,
                'xl': 32,
                'xxl': 48
            },
            'borders': {
                'radius_small': 4,
                'radius_medium': 8,
                'radius_large': 12,
                'width_thin': 1,
                'width_medium': 2,
                'width_thick': 3
            }
        }
    
    def _setup_system_detection(self):
        """Set up automatic system theme detection (Windows 10/11)"""
        try:
            # Check if system supports dark mode detection
            if sys.platform == "win32":
                import winreg
                try:
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    
                    # If system preference is to use dark theme
                    if value == 0:
                        self.system_theme = ThemeType.DARK
                    else:
                        self.system_theme = ThemeType.LIGHT
                        
                except (OSError, FileNotFoundError):
                    self.system_theme = ThemeType.LIGHT
            else:
                self.system_theme = ThemeType.LIGHT
                
        except Exception:
            self.system_theme = ThemeType.LIGHT
    
    def _load_saved_theme(self):
        """Load previously saved theme preference"""
        saved_theme = self.settings.value("theme/current", ThemeType.LINKEDIN_BLUE.value)
        
        # Validate saved theme
        try:
            theme_type = ThemeType(saved_theme)
            self.current_theme = theme_type
        except ValueError:
            self.current_theme = ThemeType.LINKEDIN_BLUE
    
    def get_available_themes(self) -> Dict[ThemeType, Dict]:
        """Get all available themes with their metadata"""
        return {
            theme_type: {
                'name': definition['name'],
                'description': definition['description']
            }
            for theme_type, definition in self.theme_definitions.items()
        }
    
    def get_current_theme(self) -> ThemeType:
        """Get the currently active theme"""
        return self.current_theme
    
    def get_theme_definition(self, theme_type: ThemeType = None) -> Dict:
        """Get complete theme definition for a specific theme"""
        if theme_type is None:
            theme_type = self.current_theme
        
        return self.theme_definitions.get(theme_type, self.theme_definitions[ThemeType.LIGHT])
    
    def set_theme(self, theme_type: ThemeType, save_preference: bool = True):
        """
        Set the active theme and apply it to all registered components
        
        Args:
            theme_type: The theme to activate
            save_preference: Whether to save this as the user's preference
        """
        if theme_type not in self.theme_definitions:
            logger.debug("Warning: Theme {theme_type} not found, using Light theme")
            theme_type = ThemeType.LIGHT
        
        # Update current theme
        old_theme = self.current_theme
        self.current_theme = theme_type
        
        # Save preference if requested
        if save_preference:
            self.settings.setValue("theme/current", theme_type.value)
        
        # Apply theme to application
        self._apply_theme_to_application()
        
        # Notify all registered widgets
        self._notify_widgets_theme_changed()
        
        # Emit signal
        self.theme_changed.emit(theme_type.value)
        
        logger.info(f"✅ Theme changed from {old_theme.value} to {theme_type.value}")
    
    def _apply_theme_to_application(self):
        """Apply current theme to the entire QApplication"""
        app = QApplication.instance()
        if not app:
            return
        
        theme_def = self.get_theme_definition()
        colors = theme_def['colors']
        
        # Create and apply palette
        palette = QPalette()
        
        # Set palette colors based on theme
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['surface']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['border']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['surface']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['surface']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['error']))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['background']))
        
        app.setPalette(palette)
        
        # Apply global stylesheet for LinkedIn Blue theme (2025 spec)
        if self.current_theme == ThemeType.LINKEDIN_BLUE:
            try:
                app.setStyleSheet(LinkedInBlueTheme.get_stylesheet())
            except Exception as e:
                logger.warning(f"Failed to apply LinkedIn Blue global stylesheet: {e}")
    
    def _notify_widgets_theme_changed(self):
        """Notify all registered widgets that the theme has changed"""
        theme_def = self.get_theme_definition()
        
        # Clean up dead widget references
        self.registered_widgets = [ref for ref in self.registered_widgets if ref() is not None]
        
        # Notify all live widgets
        for widget_ref in self.registered_widgets:
            widget = widget_ref()
            if widget and hasattr(widget, 'apply_theme'):
                try:
                    widget.apply_theme(theme_def)
                except Exception as e:
                    logger.debug("Warning: Failed to apply theme to widget {widget}: {e}")
    
    def register_widget(self, widget: QWidget):
        """
        Register a widget to receive theme change notifications
        
        Args:
            widget: Widget that should receive theme updates
                   Must implement apply_theme(theme_definition) method
        """
        import weakref
        
        # Add weak reference to avoid memory leaks
        widget_ref = weakref.ref(widget)
        self.registered_widgets.append(widget_ref)
        
        # Apply current theme immediately
        if hasattr(widget, 'apply_theme'):
            theme_def = self.get_theme_definition()
            widget.apply_theme(theme_def)
    
    def unregister_widget(self, widget: QWidget):
        """Unregister a widget from theme notifications"""
        import weakref
        
        # Remove widget reference
        widget_ref = weakref.ref(widget)
        if widget_ref in self.registered_widgets:
            self.registered_widgets.remove(widget_ref)
    
    def get_stylesheet_for_widget(self, widget_class: str) -> str:
        """
        Generate CSS stylesheet for a specific widget class based on current theme
        
        Args:
            widget_class: Widget class name (e.g., 'QPushButton', 'QLabel')
        
        Returns:
            CSS stylesheet string
        """
        theme_def = self.get_theme_definition()
        colors = theme_def['colors']
        fonts = theme_def['fonts']
        spacing = theme_def['spacing']
        
        stylesheets = {
            'QPushButton': f"""
                QPushButton {{
                    background: {colors['primary']};
                    color: {colors['background']};
                    border: none;
                    padding: {spacing['sm']}px {spacing['md']}px;
                    border-radius: 8px;
                    font-family: "{fonts['primary']}";
                    font-size: {fonts['size_base']}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {colors['secondary']};
                }}
                QPushButton:pressed {{
                    background: {colors['neutral']};
                }}
                QPushButton:disabled {{
                    background: {colors['border']};
                    color: {colors['text_secondary']};
                }}
            """,
            
            'QLabel': f"""
                QLabel {{
                    color: {colors['text_primary']};
                    font-family: "{fonts['primary']}";
                    font-size: {fonts['size_base']}px;
                }}
                QLabel[class="title"] {{
                    font-size: {fonts['size_title']}px;
                    font-weight: bold;
                    color: {colors['text_primary']};
                }}
                QLabel[class="subtitle"] {{
                    font-size: {fonts['size_large']}px;
                    color: {colors['text_secondary']};
                }}
            """,
            
            'QLineEdit': f"""
                QLineEdit {{
                    padding: {spacing['sm']}px {spacing['md']}px;
                    border: 2px solid {colors['border']};
                    border-radius: 8px;
                    font-family: "{fonts['primary']}";
                    font-size: {fonts['size_base']}px;
                    background: {colors['background']};
                    color: {colors['text_primary']};
                }}
                QLineEdit:focus {{
                    border-color: {colors['primary']};
                }}
            """,
            
            'QTableWidget': f"""
                QTableWidget {{
                    background: {colors['background']};
                    color: {colors['text_primary']};
                    gridline-color: {colors['border']};
                    font-family: "{fonts['primary']}";
                    font-size: {fonts['size_base']}px;
                }}
                QTableWidget::item {{
                    padding: {spacing['sm']}px;
                }}
                QTableWidget::item:selected {{
                    background: {colors['primary']};
                    color: {colors['background']};
                }}
                QHeaderView::section {{
                    background: {colors['surface']};
                    color: {colors['text_primary']};
                    padding: {spacing['md']}px;
                    border: 1px solid {colors['border']};
                    font-weight: bold;
                }}
            """,
            
            'QTabWidget': f"""
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
                    background: {colors['background']};
                    color: {colors['text_primary']};
                    border: 2px solid {colors['border']};
                    border-bottom: none;
                }}
            """
        }
        
        return stylesheets.get(widget_class, "")
    
    def create_custom_theme(self, name: str, colors: Dict[str, str], 
                          fonts: Dict = None, spacing: Dict = None) -> bool:
        """
        Create a custom theme definition
        
        Args:
            name: Theme name
            colors: Color definitions dictionary
            fonts: Font definitions (optional)
            spacing: Spacing definitions (optional)
        
        Returns:
            True if theme was created successfully
        """
        try:
            # Validate required color keys
            required_colors = ['primary', 'secondary', 'background', 'text_primary']
            for key in required_colors:
                if key not in colors:
                    logger.debug("Error: Missing required color '{key}' in custom theme")
                    return False
            
            # Use defaults for missing optional definitions
            if fonts is None:
                fonts = self.theme_definitions[ThemeType.LIGHT]['fonts']
            if spacing is None:
                spacing = self.theme_definitions[ThemeType.LIGHT]['spacing']
            
            # Create custom theme definition
            custom_theme = {
                'name': name,
                'description': f'Custom theme: {name}',
                'colors': colors,
                'fonts': fonts,
                'spacing': spacing
            }
            
            # Store custom theme
            self.theme_definitions[ThemeType.CUSTOM] = custom_theme
            
            # Save to settings
            self.settings.setValue("theme/custom", custom_theme)
            
            logger.info("✅ Custom theme '{name}' created successfully")
            return True
            
        except Exception as e:
            logger.error("❌ Error creating custom theme: {e}")
            return False
    
    def auto_detect_and_apply_system_theme(self):
        """Automatically detect and apply system theme preference"""
        self._setup_system_detection()
        
        if hasattr(self, 'system_theme'):
            self.set_theme(self.system_theme, save_preference=False)
            logger.info("✅ Applied system theme: {self.system_theme.value}")

# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

def apply_theme_to_widget(widget: QWidget, widget_class: str = None):
    """
    Convenience function to apply current theme to a widget
    
    Args:
        widget: Widget to style
        widget_class: Widget class override (auto-detected if None)
    """
    if widget_class is None:
        widget_class = widget.__class__.__name__
    
    theme_manager = get_theme_manager()
    stylesheet = theme_manager.get_stylesheet_for_widget(widget_class)
    
    if stylesheet:
        widget.setStyleSheet(stylesheet)

# Example usage and testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox
    
    class ThemeTestWindow(QMainWindow):
        """Test window for theme system"""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🎨 Theme System Test - Phase 5.7")
            self.setGeometry(100, 100, 800, 600)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Get theme manager
            self.theme_manager = get_theme_manager()
            
            # Theme selector
            self.theme_selector = QComboBox()
            themes = self.theme_manager.get_available_themes()
            for theme_type, theme_info in themes.items():
                self.theme_selector.addItem(theme_info['name'], theme_type)
            
            self.theme_selector.currentIndexChanged.connect(self.on_theme_changed)
            layout.addWidget(self.theme_selector)
            
            # Test buttons
            for i in range(5):
                btn = QPushButton(f"Test Button {i+1}")
                apply_theme_to_widget(btn, 'QPushButton')
                layout.addWidget(btn)
            
            # Register with theme manager
            self.theme_manager.register_widget(self)
            
            # Apply initial theme
            self.apply_theme(self.theme_manager.get_theme_definition())
        
        def apply_theme(self, theme_definition):
            """Apply theme to this widget"""
            colors = theme_definition['colors']
            self.setStyleSheet(f"""
                QMainWindow {{
                    background: {colors['background']};
                    color: {colors['text_primary']};
                }}
            """)
        
        def on_theme_changed(self):
            """Handle theme selection change"""
            theme_type = self.theme_selector.currentData()
            if theme_type:
                self.theme_manager.set_theme(theme_type)
    
    # Run test
    app = QApplication(sys.argv)
    window = ThemeTestWindow()
    window.show()
    
    logger.debug("🎨 Phase 5.7 Theme System Test")
    logger.debug("=" * 40)
    logger.info("✅ Theme Manager initialized")
    logger.info("✅ Multiple themes available")
    logger.info("✅ Real-time theme switching")
    logger.info("✅ Widget registration system")
    logger.info("✅ System theme detection")
    
    sys.exit(app.exec())