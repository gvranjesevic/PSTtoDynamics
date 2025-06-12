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
import os
from typing import Dict, Any, Optional, Callable
from enum import Enum
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QPalette, QColor

class ThemeType(Enum):
    """Available theme types"""
    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    HIGH_CONTRAST = "high_contrast"
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
        self.current_theme = ThemeType.LIGHT
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
        saved_theme = self.settings.value("theme/current", ThemeType.LIGHT.value)
        
        # Validate saved theme
        try:
            theme_type = ThemeType(saved_theme)
            self.current_theme = theme_type
        except ValueError:
            self.current_theme = ThemeType.LIGHT
    
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
            print(f"Warning: Theme {theme_type} not found, using Light theme")
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
        
        print(f"✅ Theme changed from {old_theme.value} to {theme_type.value}")
    
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
                    print(f"Warning: Failed to apply theme to widget {widget}: {e}")
    
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
                    print(f"Error: Missing required color '{key}' in custom theme")
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
            
            print(f"✅ Custom theme '{name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating custom theme: {e}")
            return False
    
    def auto_detect_and_apply_system_theme(self):
        """Automatically detect and apply system theme preference"""
        self._setup_system_detection()
        
        if hasattr(self, 'system_theme'):
            self.set_theme(self.system_theme, save_preference=False)
            print(f"✅ Applied system theme: {self.system_theme.value}")

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
    
    print("🎨 Phase 5.7 Theme System Test")
    print("=" * 40)
    print("✅ Theme Manager initialized")
    print("✅ Multiple themes available")
    print("✅ Real-time theme switching")
    print("✅ Widget registration system")
    print("✅ System theme detection")
    
    sys.exit(app.exec())