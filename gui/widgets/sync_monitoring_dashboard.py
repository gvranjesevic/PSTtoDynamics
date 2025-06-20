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

class SyncMetricsWidget(QWidget):
    """Widget displaying real-time sync metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Metrics Grid
        metrics_grid = QHBoxLayout()
        metrics_grid.setSpacing(20)
        
        # Sync Count
        sync_frame = QFrame()
        sync_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #005885;
                background-color: #F9FAFB;
            }
        """)
        sync_layout = QVBoxLayout()
        sync_layout.setContentsMargins(20, 20, 20, 20)
        sync_layout.setSpacing(8)
        sync_title = QLabel("Total Syncs")
        sync_title.setStyleSheet("color: #666666; font-size: 11px; font-weight: bold;")
        self.sync_count_label = QLabel("0")
        self.sync_count_label.setStyleSheet("color: #0077B5; font-size: 20px; font-weight: bold;")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(self.sync_count_label)
        sync_frame.setLayout(sync_layout)
        metrics_grid.addWidget(sync_frame)
        
        # Conflict Count
        conflict_frame = QFrame()
        conflict_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #005885;
                background-color: #F9FAFB;
            }
        """)
        conflict_layout = QVBoxLayout()
        conflict_layout.setContentsMargins(20, 20, 20, 20)
        conflict_layout.setSpacing(8)
        conflict_title = QLabel("Conflicts")
        conflict_title.setStyleSheet("color: #666666; font-size: 11px; font-weight: bold;")
        self.conflict_count_label = QLabel("0")
        self.conflict_count_label.setStyleSheet("color: #0077B5; font-size: 20px; font-weight: bold;")
        conflict_layout.addWidget(conflict_title)
        conflict_layout.addWidget(self.conflict_count_label)
        conflict_frame.setLayout(conflict_layout)
        metrics_grid.addWidget(conflict_frame)
        
        # Error Count
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #005885;
                background-color: #F9FAFB;
            }
        """)
        error_layout = QVBoxLayout()
        error_layout.setContentsMargins(20, 20, 20, 20)
        error_layout.setSpacing(8)
        error_title = QLabel("Errors")
        error_title.setStyleSheet("color: #666666; font-size: 11px; font-weight: bold;")
        self.error_count_label = QLabel("0")
        self.error_count_label.setStyleSheet("color: #0077B5; font-size: 20px; font-weight: bold;")
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
        
        # Conflict List
        self.conflict_table = QTableWidget()
        self.conflict_table.setColumnCount(4)
        self.conflict_table.setHorizontalHeaderLabels([
            "Field", "Source Value", "Target Value", "Resolution"
        ])
        self.conflict_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.conflict_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
                border-radius: 6px;
                gridline-color: #E1E4E8;
                selection-background-color: #E8F4FD;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E1E4E8;
            }
            QTableWidget::item:selected {
                background-color: #E8F4FD;
                color: #0077B5;
            }
            QHeaderView::section {
                background-color: #0077B5;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-right: 1px solid #005885;
            }
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
        resolve_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        controls_layout.addWidget(resolve_button)
        
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

class SyncLogWidget(QWidget):
    """Widget for displaying sync logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # Log Controls
        controls_layout = QHBoxLayout()
        
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.log_display.clear)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        controls_layout.addWidget(clear_button)
        
        export_button = QPushButton("Export Logs")
        export_button.clicked.connect(self.export_logs)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005885;
            }
            QPushButton:pressed {
                background-color: #004A70;
            }
        """)
        controls_layout.addWidget(export_button)
        
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
        """Create dashboard header (standardized to match Settings panel)"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background-color: #0077B5;
            border-bottom: 1px solid #006097;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        title = QLabel("Sync Monitor")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
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
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #F3F6F8;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                color: #666666;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #E8EBED;
                color: #0077B5;
            }
            QTabBar::tab:selected {
                background-color: #0077B5;
                color: white;
            }
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