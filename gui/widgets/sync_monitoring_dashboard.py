"""
Sync Monitoring Dashboard
========================

A modern, professional dashboard for monitoring sync operations, resolving conflicts,
and viewing detailed sync metrics and logs.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QProgressBar, QTabWidget, QTextEdit,
    QSplitter, QFrame, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon

from sync.sync_engine import SyncEngine, SyncMonitor

# Theme manager to access LinkedIn Blue tokens dynamically
from gui.themes.theme_manager import get_theme_manager

class SyncMetricsWidget(QWidget):
    """Widget displaying real-time sync metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Prepare theme colours
        colors = get_theme_manager().get_theme_definition()['colors']
        primary = colors['primary']
        hover = colors.get('secondary', primary)
        surface = colors['surface']
        surface_alt = colors.get('surface_secondary', surface)
        text_secondary = colors['text_secondary']

        # Metrics Grid
        metrics_grid = QHBoxLayout()
        metrics_grid.setSpacing(20)
        
        # Sync Count
        sync_frame = QFrame()
        sync_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {surface};
                border: 2px solid {primary};
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {hover};
                background-color: {surface_alt};
            }}
        """)
        sync_layout = QVBoxLayout()
        sync_layout.setContentsMargins(20, 20, 20, 20)
        sync_layout.setSpacing(8)
        sync_title = QLabel("Total Syncs")
        sync_title.setStyleSheet(f"color: {text_secondary}; font-size: 11px; font-weight: bold;")
        self.sync_count_label = QLabel("0")
        self.sync_count_label.setStyleSheet(f"color: {primary}; font-size: 20px; font-weight: bold;")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(self.sync_count_label)
        sync_frame.setLayout(sync_layout)
        metrics_grid.addWidget(sync_frame)
        
        # Conflict Count
        conflict_frame = QFrame()
        conflict_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {surface};
                border: 2px solid {primary};
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {hover};
                background-color: {surface_alt};
            }}
        """)
        conflict_layout = QVBoxLayout()
        conflict_layout.setContentsMargins(20, 20, 20, 20)
        conflict_layout.setSpacing(8)
        conflict_title = QLabel("Conflicts")
        conflict_title.setStyleSheet(f"color: {text_secondary}; font-size: 11px; font-weight: bold;")
        self.conflict_count_label = QLabel("0")
        self.conflict_count_label.setStyleSheet(f"color: {primary}; font-size: 20px; font-weight: bold;")
        conflict_layout.addWidget(conflict_title)
        conflict_layout.addWidget(self.conflict_count_label)
        conflict_frame.setLayout(conflict_layout)
        metrics_grid.addWidget(conflict_frame)
        
        # Error Count
        error_frame = QFrame()
        error_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {surface};
                border: 2px solid {primary};
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {hover};
                background-color: {surface_alt};
            }}
        """)
        error_layout = QVBoxLayout()
        error_layout.setContentsMargins(20, 20, 20, 20)
        error_layout.setSpacing(8)
        error_title = QLabel("Errors")
        error_title.setStyleSheet(f"color: {text_secondary}; font-size: 11px; font-weight: bold;")
        self.error_count_label = QLabel("0")
        self.error_count_label.setStyleSheet(f"color: {primary}; font-size: 20px; font-weight: bold;")
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_count_label)
        error_frame.setLayout(error_layout)
        metrics_grid.addWidget(error_frame)
        
        layout.addLayout(metrics_grid)
        self.setLayout(layout)
    
    def update_metrics(self, metrics: Dict[str, int]):
        """Update the metrics display"""
        self.sync_count_label.setText(str(metrics.get('sync_count', 0)))
        self.conflict_count_label.setText(str(metrics.get('conflict_count', 0)))
        self.error_count_label.setText(str(metrics.get('error_count', 0)))

class ConflictResolutionWidget(QWidget):
    """Widget for resolving conflicts"""
    
    conflict_resolved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Get theme colors dynamically
        colors = get_theme_manager().get_theme_definition()['colors']
        primary = colors['primary']
        secondary = colors.get('secondary', primary)
        surface = colors['surface']
        border = colors['border']
        border_light = colors.get('border_light', border)
        text_inverse = colors.get('text_inverse', surface)
        
        # Conflict List
        self.conflict_table = QTableWidget()
        self.conflict_table.setColumnCount(4)
        self.conflict_table.setHorizontalHeaderLabels([
            "Field", "Source Value", "Target Value", "Resolution"
        ])
        self.conflict_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.conflict_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {surface};
                border: 1px solid {border};
                border-radius: 8px;
                gridline-color: {border_light};
                selection-background-color: {colors.get('ui_surfaceHoverAlt', '#E8F4FD')};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_light};
            }}
            QTableWidget::item:selected {{
                background-color: {colors.get('ui_surfaceHoverAlt', '#E8F4FD')};
                color: {primary};
            }}
            QHeaderView::section {{
                background-color: {primary};
                color: {text_inverse};
                font-weight: bold;
                padding: 12px;
                border: none;
                border-right: 1px solid {secondary};
            }}
        """)
        layout.addWidget(self.conflict_table)
        
        # Resolution Controls
        controls_layout = QHBoxLayout()
        
        self.resolution_strategy = QComboBox()
        self.resolution_strategy.addItems([
            "Last Write Wins",
            "Manual Resolution",
            "Merge Changes"
        ])
        controls_layout.addWidget(QLabel("Resolution Strategy:"))
        controls_layout.addWidget(self.resolution_strategy)
        
        resolve_button = QPushButton("Resolve Selected")
        resolve_button.clicked.connect(self.resolve_selected)
        resolve_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {secondary};
            }}
        """)
        controls_layout.addWidget(resolve_button)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_conflicts)
        clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('ui_buttonDark', '#5A6268')};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('ui_buttonDarker', '#545B62')};
            }}
        """)
        controls_layout.addWidget(clear_button)
        
        export_button = QPushButton("Export Conflicts")
        export_button.clicked.connect(self.export_conflicts)
        export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {secondary};
            }}
        """)
        controls_layout.addWidget(export_button)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
    
    def add_conflict(self, conflict: Dict[str, Any]):
        """Add a conflict to the resolution table"""
        row = self.conflict_table.rowCount()
        self.conflict_table.insertRow(row)
        
        self.conflict_table.setItem(row, 0, QTableWidgetItem(conflict['field']))
        self.conflict_table.setItem(row, 1, QTableWidgetItem(str(conflict['source_value'])))
        self.conflict_table.setItem(row, 2, QTableWidgetItem(str(conflict['target_value'])))
        
        resolution_combo = QComboBox()
        resolution_combo.addItems([
            "Use Source",
            "Use Target",
            "Merge"
        ])
        self.conflict_table.setCellWidget(row, 3, resolution_combo)
    
    def resolve_selected(self):
        """Resolve the selected conflicts"""
        for row in range(self.conflict_table.rowCount()):
            field = self.conflict_table.item(row, 0).text()
            resolution = self.conflict_table.cellWidget(row, 3).currentText()
            
            self.conflict_resolved.emit({
                'field': field,
                'resolution': resolution,
                'strategy': self.resolution_strategy.currentText()
            })
    
    def clear_conflicts(self):
        """Clear all conflicts from the table"""
        self.conflict_table.setRowCount(0)
    
    def export_conflicts(self):
        """Export conflicts to a file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sync_conflicts_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Conflicts", 
            filename,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"PST to Dynamics 365 Sync Conflicts\n")
                    f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for row in range(self.conflict_table.rowCount()):
                        field = self.conflict_table.item(row, 0).text()
                        source = self.conflict_table.item(row, 1).text()
                        target = self.conflict_table.item(row, 2).text()
                        resolution = self.conflict_table.cellWidget(row, 3).currentText()
                        
                        f.write(f"Field: {field}\n")
                        f.write(f"Source Value: {source}\n")
                        f.write(f"Target Value: {target}\n")
                        f.write(f"Resolution: {resolution}\n")
                        f.write("-" * 30 + "\n")
                
                QMessageBox.information(self, "Export Success", f"Conflicts exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export conflicts:\n{str(e)}")

class SyncLogWidget(QWidget):
    """Widget for displaying sync logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Get theme colors dynamically
        colors = get_theme_manager().get_theme_definition()['colors']
        primary = colors['primary']
        secondary = colors.get('secondary', primary)
        surface = colors['surface']
        text_primary = colors['text_primary']
        text_secondary = colors['text_secondary']
        text_inverse = colors.get('text_inverse', surface)
        
        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors.get('text_darkBackground', '#2C3E50')};
                color: {colors.get('text_lightOnDark', '#ECF0F1')};
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 10px;
                line-height: 1.4;
            }}
        """)
        layout.addWidget(self.log_display)
        
        # Log Controls
        controls_layout = QHBoxLayout()
        
        self.log_level = QComboBox()
        self.log_level.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.log_level)
        
        clear_log_button = QPushButton("Clear Logs")
        clear_log_button.clicked.connect(self.clear_logs)
        clear_log_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('state_errorButton', '#E74C3C')};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('state_error', '#C0392B')};
            }}
        """)
        controls_layout.addWidget(clear_log_button)
        
        export_log_button = QPushButton("Export Logs")
        export_log_button.clicked.connect(self.export_logs)
        export_log_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary};
                color: {text_inverse};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {secondary};
            }}
        """)
        controls_layout.addWidget(export_log_button)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
    
    def add_log(self, log_entry: Dict[str, Any]):
        """Add a log entry to the display"""
        timestamp = log_entry.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        event = log_entry.get('event', '')
        details = log_entry.get('details', {})
        
        log_text = f"[{timestamp}] {event}\n"
        if details:
            log_text += f"Details: {details}\n"
        log_text += "-" * 50 + "\n"
        
        self.log_display.append(log_text)
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.clear()
    
    def export_logs(self):
        """Export logs to a file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sync_logs_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Sync Logs", 
            filename,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"PST to Dynamics 365 Sync Logs\n")
                    f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.log_display.toPlainText())
                
                QMessageBox.information(self, "Export Success", f"Logs exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export logs:\n{str(e)}")

class SyncMonitoringDashboard(QWidget):
    """Main sync monitoring dashboard widget"""
    
    def __init__(self, sync_engine=None):
        super().__init__()
        self.sync_engine = sync_engine
        self.setup_ui()
        
        # Start update timer only if sync_engine is available
        if self.sync_engine:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_dashboard)
            self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        self.setMinimumSize(1200, 800)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header (standardized to match Settings panel)
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Set up content
        self.setup_content()
    
    def create_header(self) -> QWidget:
        """Create the dashboard header"""
        colors = get_theme_manager().get_theme_definition()['colors']
        primary = colors['primary']
        text_inverse = colors.get('text_inverse', colors['surface'])
        
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background-color: {primary};
            color: {text_inverse};
            border-bottom: 1px solid #006097;
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Title
        title = QLabel("🔄 Sync Monitor")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {text_inverse};
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.update_dashboard)
        refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('secondary', primary)};
                color: {text_inverse};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('brand_primaryActive', '#004A70')};
            }}
        """)
        layout.addWidget(refresh_button)
        
        return header
    
    def setup_content(self):
        """Set up the content area"""
        main_layout = self.layout()
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Add metrics widget
        self.metrics_widget = SyncMetricsWidget()
        content_layout.addWidget(self.metrics_widget)
        
        # Create tab widget for conflicts and logs
        self.tab_widget = QTabWidget()
        colors = get_theme_manager().get_theme_definition()['colors']
        primary = colors['primary']
        surface_alt = colors.get('surface_secondary', '#F9FAFB')
        canvas = colors.get('background', '#F3F6F8')
        text_secondary = colors['text_secondary']
        hover_bg = colors.get('border_light', '#E8EBED')
        text_inverse = colors.get('text_inverse', colors['surface'])
        
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {canvas};
            }}
            QTabBar::tab {{
                background-color: {surface_alt};
                color: {text_secondary};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {hover_bg};
                color: {primary};
            }}
            QTabBar::tab:selected {{
                background-color: {primary};
                color: {text_inverse};
            }}
        """)
        
        # Add conflict resolution tab
        self.conflict_widget = ConflictResolutionWidget()
        self.conflict_widget.conflict_resolved.connect(self.handle_conflict_resolution)
        self.tab_widget.addTab(self.conflict_widget, "Conflict Resolution")
        
        # Add sync logs tab
        self.log_widget = SyncLogWidget()
        self.tab_widget.addTab(self.log_widget, "Sync Logs")
        
        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(content_widget)
    
    def update_dashboard(self):
        """Update dashboard with latest sync data"""
        if not self.sync_engine or not hasattr(self, 'metrics_widget'):
            return
            
        # Update metrics
        try:
            metrics = self.sync_engine.monitor.get_metrics()
            self.metrics_widget.update_metrics(metrics)
            
            # Update logs
            logs = self.sync_engine.monitor.get_recent_logs()
            for log in logs:
                self.log_widget.add_log(log)
        except AttributeError:
            # Sync engine or monitor not available
            pass
    
    def handle_conflict_resolution(self, resolution: Dict[str, Any]):
        """Handle conflict resolution from the UI"""
        try:
            field = resolution.get('field')
            strategy = resolution.get('strategy', 'Last Write Wins').lower().replace(' ', '_')
            
            # Log the resolution
            self.log_widget.add_log({
                'timestamp': datetime.now(),
                'event': 'Conflict Resolved',
                'details': {
                    'field': field,
                    'strategy': strategy,
                    'resolution': resolution.get('resolution')
                }
            })
            
            # Apply the resolution to the sync engine
            # This would typically involve updating the data and re-syncing
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Conflict Resolved",
                f"Conflict for field '{field}' resolved using {strategy} strategy."
            )
            
            # Update dashboard metrics
            self.update_dashboard()
            
        except Exception as e:
            logger.error(f"Error handling conflict resolution: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Resolution Error", f"Failed to resolve conflict:\n{str(e)}") 