"""
LinkedIn Blue Theme Definition
=============================

Professional LinkedIn-inspired blue theme with modern aesthetics.
This theme uses LinkedIn's signature blue (#0077B5) as the primary color
with carefully selected complementary colors for a professional look.
"""

from enum import Enum

class LinkedInBlueTheme:
    """LinkedIn Blue theme definition with all styling properties"""
    
    # Core LinkedIn Blue Colors
    COLORS = {
        'primary': '#0077B5',        # LinkedIn signature blue
        'secondary': '#005885',      # Darker LinkedIn blue
        'accent': '#00A0DC',         # Lighter LinkedIn blue
        'success': '#057642',        # LinkedIn green
        'warning': '#F5C75D',        # LinkedIn gold
        'error': '#CC1016',          # LinkedIn red
        'neutral': '#666666',        # LinkedIn gray
        'background': '#F3F6F8',     # LinkedIn light background
        'surface': '#FFFFFF',        # Pure white surfaces
        'surface_secondary': '#F9FAFB', # Slightly off-white
        'text_primary': '#000000',   # LinkedIn black text
        'text_secondary': '#666666', # LinkedIn gray text
        'text_muted': '#999999',     # Muted text
        'border': '#D0D7DE',         # LinkedIn border gray
        'border_light': '#E8EBED',   # Lighter border
        'shadow': 'rgba(0, 119, 181, 0.15)', # LinkedIn blue shadow
        'hover': '#004471',          # Darker blue for hover states
        'active': '#003A5C',         # Even darker for active states
        'focus': '#0077B5',          # LinkedIn blue for focus
        'disabled': '#CCCCCC'        # Disabled state
    }
    
    # Typography
    FONTS = {
        'primary': 'Segoe UI',       # Professional font
        'secondary': 'Arial',        # Fallback
        'code': 'Consolas',          # Code font
        'size_base': 14,
        'size_small': 12,
        'size_large': 16,
        'size_title': 20,
        'size_heading': 18,
        'weight_normal': 400,
        'weight_medium': 500,
        'weight_bold': 600
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48
    }
    
    # Borders and Radius
    BORDERS = {
        'radius_small': 4,
        'radius_medium': 8,
        'radius_large': 12,
        'width_thin': 1,
        'width_medium': 2,
        'width_thick': 3
    }
    
    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate complete CSS stylesheet for LinkedIn Blue theme"""
        return f"""
        /* LinkedIn Blue Theme Stylesheet */
        
        /* Main Application Window */
        QMainWindow {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
            font-family: '{cls.FONTS['primary']}';
            font-size: {cls.FONTS['size_base']}px;
        }}
        
        /* Navigation Sidebar */
        QFrame[objectName="NavigationSidebar"] {{
            background-color: {cls.COLORS['surface']};
            border-right: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_medium']}px;
        }}
        
        /* Navigation Buttons */
        QPushButton[objectName="nav_button"] {{
            background-color: transparent;
            color: {cls.COLORS['text_primary']};
            border: none;
            padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
            text-align: left;
            border-radius: {cls.BORDERS['radius_small']}px;
            font-weight: {cls.FONTS['weight_medium']};
        }}
        
        QPushButton[objectName="nav_button"]:hover {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        QPushButton[objectName="nav_button"]:pressed {{
            background-color: {cls.COLORS['active']};
        }}
        
        /* Primary Buttons */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
            border: none;
            padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
            border-radius: {cls.BORDERS['radius_small']}px;
            font-weight: {cls.FONTS['weight_medium']};
            font-size: {cls.FONTS['size_base']}px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['active']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['disabled']};
            color: {cls.COLORS['text_muted']};
        }}
        
        /* Secondary Buttons */
        QPushButton[class="secondary"] {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['primary']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['primary']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_small']}px;
            padding: {cls.SPACING['sm']}px;
            font-size: {cls.FONTS['size_base']}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.COLORS['focus']};
            outline: none;
        }}
        
        /* Labels */
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-size: {cls.FONTS['size_base']}px;
        }}
        
        QLabel[class="title"] {{
            font-size: {cls.FONTS['size_title']}px;
            font-weight: {cls.FONTS['weight_bold']};
            color: {cls.COLORS['primary']};
        }}
        
        QLabel[class="heading"] {{
            font-size: {cls.FONTS['size_heading']}px;
            font-weight: {cls.FONTS['weight_medium']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QLabel[class="secondary"] {{
            color: {cls.COLORS['text_secondary']};
        }}
        
        QLabel[class="muted"] {{
            color: {cls.COLORS['text_muted']};
        }}
        
        /* Tables */
        QTableWidget, QTableView {{
            background-color: {cls.COLORS['surface']};
            alternate-background-color: {cls.COLORS['surface_secondary']};
            gridline-color: {cls.COLORS['border_light']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_small']}px;
        }}
        
        QTableWidget::item, QTableView::item {{
            padding: {cls.SPACING['sm']}px;
            border-bottom: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border_light']};
        }}
        
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['surface_secondary']};
            color: {cls.COLORS['text_primary']};
            padding: {cls.SPACING['sm']}px;
            border: none;
            border-bottom: {cls.BORDERS['width_medium']}px solid {cls.COLORS['primary']};
            font-weight: {cls.FONTS['weight_medium']};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            background-color: {cls.COLORS['surface_secondary']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_small']}px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: {cls.BORDERS['radius_small']}px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_secondary']};
            border-top: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border-bottom: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
        }}
        
        QMenuBar::item {{
            padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        /* Tool Bar */
        QToolBar {{
            background-color: {cls.COLORS['surface']};
            border: none;
            spacing: {cls.SPACING['sm']}px;
        }}
        
        QToolButton {{
            background-color: transparent;
            color: {cls.COLORS['text_primary']};
            border: none;
            padding: {cls.SPACING['sm']}px;
            border-radius: {cls.BORDERS['radius_small']}px;
        }}
        
        QToolButton:hover {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['surface_secondary']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['neutral']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['primary']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['surface_secondary']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['neutral']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['primary']};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_small']}px;
            padding: {cls.SPACING['sm']}px;
        }}
        
        QComboBox:focus {{
            border-color: {cls.COLORS['focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['text_secondary']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            background-color: {cls.COLORS['surface']};
            border: {cls.BORDERS['width_thin']}px solid {cls.COLORS['border']};
            border-radius: {cls.BORDERS['radius_small']}px;
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['surface_secondary']};
            color: {cls.COLORS['text_secondary']};
            padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
            border-top-left-radius: {cls.BORDERS['radius_small']}px;
            border-top-right-radius: {cls.BORDERS['radius_small']}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['surface']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {cls.COLORS['hover']};
            color: {cls.COLORS['surface']};
        }}
        """
    
    @classmethod
    def get_theme_definition(cls) -> dict:
        """Get complete theme definition dictionary"""
        return {
            'name': 'LinkedIn Blue',
            'description': 'Professional LinkedIn-inspired blue theme with modern aesthetics',
            'colors': cls.COLORS,
            'fonts': cls.FONTS,
            'spacing': cls.SPACING,
            'borders': cls.BORDERS
        } 