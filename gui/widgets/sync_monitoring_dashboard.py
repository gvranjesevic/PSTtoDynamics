"""
Sync Monitoring Dashboard
========================

A modern, professional dashboard for monitoring sync operations, resolving conflicts,
and viewing detailed sync metrics and logs.
"""

import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QProgressBar, QTabWidget, QTextEdit,
    QSplitter, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon

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
        
        # Sync Count
        sync_frame = QFrame()
        sync_frame.setFrameStyle(QFrame.StyledPanel)
        sync_layout = QVBoxLayout()
        self.sync_count_label = QLabel("0")
        self.sync_count_label.setFont(QFont("Arial", 24, QFont.Bold))
        sync_layout.addWidget(QLabel("Total Syncs"))
        sync_layout.addWidget(self.sync_count_label)
        sync_frame.setLayout(sync_layout)
        metrics_grid.addWidget(sync_frame)
        
        # Conflict Count
        conflict_frame = QFrame()
        conflict_frame.setFrameStyle(QFrame.StyledPanel)
        conflict_layout = QVBoxLayout()
        self.conflict_count_label = QLabel("0")
        self.conflict_count_label.setFont(QFont("Arial", 24, QFont.Bold))
        conflict_layout.addWidget(QLabel("Conflicts"))
        conflict_layout.addWidget(self.conflict_count_label)
        conflict_frame.setLayout(conflict_layout)
        metrics_grid.addWidget(conflict_frame)
        
        # Error Count
        error_frame = QFrame()
        error_frame.setFrameStyle(QFrame.StyledPanel)
        error_layout = QVBoxLayout()
        self.error_count_label = QLabel("0")
        self.error_count_label.setFont(QFont("Arial", 24, QFont.Bold))
        error_layout.addWidget(QLabel("Errors"))
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
        self.conflict_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        controls_layout.addWidget(clear_button)
        
        export_button = QPushButton("Export Logs")
        export_button.clicked.connect(self.export_logs)
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
        # TODO: Implement log export
        pass

class SyncMonitoringDashboard(QMainWindow):
    """Main sync monitoring dashboard window"""
    
    def __init__(self, sync_engine: SyncEngine):
        super().__init__()
        self.sync_engine = sync_engine
        self.setup_ui()
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        self.setWindowTitle("Sync Monitoring Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add metrics widget
        self.metrics_widget = SyncMetricsWidget()
        main_layout.addWidget(self.metrics_widget)
        
        # Create tab widget for conflicts and logs
        tab_widget = QTabWidget()
        
        # Add conflict resolution tab
        self.conflict_widget = ConflictResolutionWidget()
        self.conflict_widget.conflict_resolved.connect(self.handle_conflict_resolution)
        tab_widget.addTab(self.conflict_widget, "Conflict Resolution")
        
        # Add sync logs tab
        self.log_widget = SyncLogWidget()
        tab_widget.addTab(self.log_widget, "Sync Logs")
        
        main_layout.addWidget(tab_widget)
    
    def update_dashboard(self):
        """Update dashboard with latest sync data"""
        # Update metrics
        metrics = self.sync_engine.monitor.get_metrics()
        self.metrics_widget.update_metrics(metrics)
        
        # Update logs
        logs = self.sync_engine.monitor.get_logs()
        for log in logs:
            self.log_widget.add_log(log)
    
    def handle_conflict_resolution(self, resolution: Dict[str, Any]):
        """Handle conflict resolution from the UI"""
        # TODO: Implement conflict resolution handling
        pass 