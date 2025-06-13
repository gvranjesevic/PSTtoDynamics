"""
Application Icon Resources
=========================

Contains embedded SVG icon data for the PST to Dynamics 365 application.
"""

import base64
from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QPixmap, QIcon, QPainter

try:
    from PyQt6.QtSvgWidgets import QSvgWidget
    from PyQt6.QtSvg import QSvgRenderer
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

# Application icon as SVG data
APP_ICON_SVG = """
<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4a90e2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#357abd;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#50c878;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3da05e;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="64" cy="64" r="60" fill="url(#grad1)" stroke="#2c5aa0" stroke-width="2"/>
  
  <!-- PST file icon (left side) -->
  <rect x="20" y="35" width="25" height="30" rx="2" fill="#ffffff" opacity="0.9"/>
  <rect x="22" y="37" width="21" height="2" fill="#4a90e2"/>
  <rect x="22" y="41" width="18" height="1" fill="#666"/>
  <rect x="22" y="44" width="16" height="1" fill="#666"/>
  <rect x="22" y="47" width="19" height="1" fill="#666"/>
  <rect x="22" y="50" width="15" height="1" fill="#666"/>
  <rect x="22" y="53" width="17" height="1" fill="#666"/>
  <rect x="22" y="56" width="14" height="1" fill="#666"/>
  <rect x="22" y="59" width="16" height="1" fill="#666"/>
  
  <!-- Arrow (center) -->
  <path d="M 50 60 L 60 55 L 60 58 L 70 58 L 70 62 L 60 62 L 60 65 Z" fill="#ffffff"/>
  
  <!-- Dynamics 365 logo (right side) -->
  <circle cx="85" cy="50" r="18" fill="url(#grad2)"/>
  <text x="85" y="46" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" font-weight="bold" fill="#ffffff">D365</text>
  <rect x="76" y="52" width="18" height="1" fill="#ffffff" opacity="0.8"/>
  <rect x="78" y="55" width="14" height="1" fill="#ffffff" opacity="0.6"/>
  <rect x="80" y="58" width="10" height="1" fill="#ffffff" opacity="0.4"/>
  
  <!-- Sync arrows at bottom -->
  <path d="M 35 85 Q 45 80 55 85" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.8"/>
  <path d="M 55 85 L 52 82 M 55 85 L 52 88" stroke="#ffffff" stroke-width="2" opacity="0.8"/>
  
  <path d="M 73 85 Q 83 80 93 85" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.8"/>
  <path d="M 73 85 L 76 82 M 73 85 L 76 88" stroke="#ffffff" stroke-width="2" opacity="0.8"/>
  
  <!-- Title text -->
  <text x="64" y="110" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#ffffff">PST to D365</text>
</svg>
"""

def create_simple_icon(size: int = 32) -> QIcon:
    """
    Create a simple icon using basic shapes if SVG is not available.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw background circle
    painter.setBrush(Qt.GlobalColor.blue)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size-4, size-4)
    
    # Draw arrow
    painter.setBrush(Qt.GlobalColor.white)
    arrow_size = size // 4
    center = size // 2
    painter.drawRect(center - arrow_size//2, center - 1, arrow_size, 2)
    painter.drawRect(center + arrow_size//2 - 2, center - arrow_size//4, 2, arrow_size//2)
    
    painter.end()
    return QIcon(pixmap)

def get_app_icon(size: int = 32) -> QIcon:
    """
    Get the application icon as a QIcon object.
    
    Args:
        size: Icon size in pixels (default: 32)
        
    Returns:
        QIcon object containing the application icon
    """
    if not SVG_AVAILABLE:
        return create_simple_icon(size)
    
    try:
        # Create SVG renderer
        svg_bytes = QByteArray(APP_ICON_SVG.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Render SVG to pixmap
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    except Exception:
        return create_simple_icon(size)

def get_app_pixmap(size: int = 128) -> QPixmap:
    """
    Get the application icon as a QPixmap object.
    
    Args:
        size: Icon size in pixels (default: 128)
        
    Returns:
        QPixmap object containing the application icon
    """
    if not SVG_AVAILABLE:
        return create_simple_icon(size).pixmap(size, size)
    
    try:
        # Create SVG renderer
        svg_bytes = QByteArray(APP_ICON_SVG.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Render SVG to pixmap
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    except Exception:
        return create_simple_icon(size).pixmap(size, size)

def save_icon_to_file(file_path: str, size: int = 128, format: str = 'PNG') -> bool:
    """
    Save the application icon to a file.
    
    Args:
        file_path: Path where to save the icon
        size: Icon size in pixels (default: 128)
        format: Image format (PNG, ICO, etc.)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        pixmap = get_app_pixmap(size)
        return pixmap.save(file_path, format)
    except Exception:
        return False 