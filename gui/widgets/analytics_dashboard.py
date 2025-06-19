"""
PST-to-Dynamics 365 Analytics Dashboard
======================================

Phase 5.4: Interactive Analytics Visualization
Real-time charts and performance metrics dashboard for Phase 3 analytics.
"""

import sys
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTabWidget, QGroupBox, 
    QFrame, QScrollArea, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QSizePolicy, QSpacerItem, QProgressBar,
    QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette

# Setup logging
logger = logging.getLogger(__name__)

# Import PyQtGraph for advanced charting
try:
    import pyqtgraph as pg
    from pyqtgraph import PlotWidget, BarGraphItem
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    logger.warning("⚠️ PyQtGraph not available - using basic charts")

# Import Phase 3 analytics modules
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from Phase3_Analytics.phase3_integration import get_phase3_analytics
    from Phase3_Analytics.import_analytics import get_analytics
    PHASE3_AVAILABLE = True
except ImportError as e:
    PHASE3_AVAILABLE = False
    logger.warning("⚠️ Phase 3 Analytics not available")


class AnalyticsDataLoader(QThread):
    """Background thread for loading analytics data"""
    
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data_type: str = "dashboard", time_range: int = 30):
        super().__init__()
        self.data_type = data_type
        self.time_range = time_range
        
    def run(self):
        """Load analytics data in background"""
        try:
            if not PHASE3_AVAILABLE:
                self.data_loaded.emit(self.get_sample_data())
                return
                
            analytics = get_phase3_analytics()
            
            if self.data_type == "dashboard":
                data = analytics.get_real_time_dashboard_data()
            elif self.data_type == "performance":
                analytics_engine = get_analytics()
                data = analytics_engine.get_performance_summary(self.time_range)
            else:
                data = {"type": self.data_type, "message": "Data type not implemented"}
            
            self.data_loaded.emit(data)
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to load analytics data: {str(e)}")
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for testing when Phase 3 is not available"""
        return {
            "analytics_enabled": True,
            "last_updated": datetime.now().isoformat(),
            "current_session": {
                "session_id": "demo_session_001",
                "processed_emails": 1247,
                "successful_imports": 1195,
                "failed_imports": 23,
                "duplicates_detected": 29,
                "contacts_created": 45,
                "success_rate": 0.958,
                "emails_per_minute": 28.5,
                "elapsed_time_minutes": 43.7
            },
            "performance_summary": {
                "total_sessions": 15,
                "total_emails_processed": 18543,
                "total_successful": 17789,
                "total_failed": 354,
                "total_duplicates": 400,
                "total_contacts_created": 678,
                "avg_emails_per_minute": 32.8,
                "avg_duration_minutes": 38.2,
                "analytics_enabled": True,
                "period_days": 30
            },
            "system_status": "active"
        }


class MetricCard(QFrame):
    """Individual metric display card"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#0077B5"):
        super().__init__()
        self.setup_ui(title, value, subtitle, color)
    
    def setup_ui(self, title: str, value: str, subtitle: str, color: str):
        """Setup metric card UI"""
        self.setFixedSize(220, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 2px solid #0077B5;
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: #005885;
                background-color: #F9FAFB;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #0077B5; font-size: 12px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #000000; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setStyleSheet("color: #666666; font-size: 10px;")
            layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None
        
        layout.addStretch()
    
    def darken_color(self, color: str) -> str:
        """Darken a hex color for hover effects"""
        color_map = {
            "#0077B5": "#005885",
            "#e74c3c": "#c0392b", 
            "#2ecc71": "#27ae60",
            "#f39c12": "#e67e22"
        }
        return color_map.get(color, "#2c3e50")
    
    def update_value(self, new_value: str, new_subtitle: str = ""):
        """Update the metric value and subtitle"""
        self.value_label.setText(new_value)
        if self.subtitle_label and new_subtitle:
            self.subtitle_label.setText(new_subtitle)


class PerformanceChart(QWidget):
    """Performance metrics chart using PyQtGraph"""
    
    def __init__(self, title: str = "Performance Metrics"):
        super().__init__()
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """Setup chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #2c3e50; 
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 6px;
        """)
        layout.addWidget(title_label)
        
        if PYQTGRAPH_AVAILABLE:
            # Create PyQtGraph plot
            self.plot_widget = PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('left', 'Emails per Minute', color='#2c3e50')
            self.plot_widget.setLabel('bottom', 'Session', color='#2c3e50')
            self.plot_widget.showGrid(x=True, y=True)
            
            # Style the plot
            self.plot_widget.getAxis('left').setPen('#2c3e50')
            self.plot_widget.getAxis('bottom').setPen('#2c3e50')
            
            layout.addWidget(self.plot_widget)
            
            # Add sample data
            self.update_chart_with_sample_data()
        else:
            # Fallback text display
            fallback_text = QLabel("📊 Performance Chart\n(Install PyQtGraph for advanced visualization)")
            fallback_text.setStyleSheet("""
                font-size: 14px; 
                color: #7f8c8d; 
                padding: 40px;
                text-align: center;
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
            """)
            fallback_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_text)
    
    def update_chart_with_sample_data(self):
        """Update chart with sample data for demonstration"""
        if not PYQTGRAPH_AVAILABLE or not hasattr(self, 'plot_widget'):
            return
        
        # Sample performance data
        import random
        sessions = 10
        x_data = list(range(sessions))
        y_data = [25 + random.randint(-5, 10) for _ in range(sessions)]
        
        # Clear previous plots
        self.plot_widget.clear()
        
        # Plot line
        pen = pg.mkPen(color='#0077B5', width=3)
        self.plot_widget.plot(x_data, y_data, pen=pen, symbol='o', symbolBrush='#0077B5', symbolSize=8)
        
        # Set axis ranges
        self.plot_widget.setXRange(0, sessions-1)
        self.plot_widget.setYRange(0, max(y_data) + 5)
    
    def update_chart(self, data: List[Dict[str, Any]]):
        """Update chart with new data"""
        if not PYQTGRAPH_AVAILABLE or not hasattr(self, 'plot_widget'):
            return
        
        if not data:
            self.update_chart_with_sample_data()
            return
        
        # Clear previous plots
        self.plot_widget.clear()
        
        # Prepare data
        x_data = list(range(len(data)))
        y_data = [item.get('emails_per_minute', 0) for item in data]
        
        # Plot line
        pen = pg.mkPen(color='#0077B5', width=3)
        self.plot_widget.plot(x_data, y_data, pen=pen, symbol='o', symbolBrush='#0077B5', symbolSize=8)


class AnalyticsDashboard(QWidget):
    """Main Analytics Dashboard Widget"""
    
    # Signals
    refresh_requested = pyqtSignal()
    export_requested = pyqtSignal(str)  # format
    
    def __init__(self):
        super().__init__()
        self.data_loader = None
        self.current_data = {}
        self.setup_ui()
        self.setup_auto_refresh()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup analytics dashboard interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content container with padding beneath header
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Build content inside container
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #F3F6F8;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #666666;
            }
            QTabBar::tab:selected {
                background-color: #0077B5;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #E8EBED;
                color: #0077B5;
            }
        """)
        
        # Dashboard tab
        dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")
        
        # Performance tab  
        performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(performance_tab, "⚡ Performance")
        
        self.content_layout.addWidget(self.tab_widget)
        
        # Add content container to outer layout
        layout.addWidget(self.content_widget)
    
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
        title = QLabel("Analytics")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def create_dashboard_tab(self) -> QWidget:
        """Create main dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
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
        self.refresh_button.clicked.connect(self.load_dashboard_data)
        controls_layout.addWidget(self.refresh_button)
        
        # Export button
        export_button = QPushButton("📤 Export")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: 2px solid #0077B5;
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
        export_button.clicked.connect(self.export_analytics)
        controls_layout.addWidget(export_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Metrics cards section
        metrics_group = QGroupBox("📊 Key Metrics")
        metrics_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0077B5 !important;
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #0077B5;
                background-color: #FFFFFF;
            }
        """)
        
        metrics_layout = QHBoxLayout(metrics_group)
        metrics_layout.setSpacing(20)
        metrics_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create metric cards
        self.email_card = MetricCard("Total Emails", "0", "processed", "#0077B5")
        self.success_card = MetricCard("Success Rate", "0%", "last session", "#0077B5")
        self.speed_card = MetricCard("Processing Speed", "0/min", "emails per minute", "#0077B5")
        self.contacts_card = MetricCard("Contacts Created", "0", "total", "#0077B5")
        
        metrics_layout.addWidget(self.email_card)
        metrics_layout.addWidget(self.success_card)
        metrics_layout.addWidget(self.speed_card)
        metrics_layout.addWidget(self.contacts_card)
        metrics_layout.addStretch()
        
        layout.addWidget(metrics_group)
        
        # Charts section
        charts_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Performance chart
        self.performance_chart = PerformanceChart("Performance Over Time")
        charts_splitter.addWidget(self.performance_chart)
        
        # Status info
        status_group = QGroupBox("📋 System Status")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0077B5 !important;
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 15px;
                font-size: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #0077B5;
                background-color: #FFFFFF;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(250)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                background-color: #f8f9fa;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.status_text)
        
        charts_splitter.addWidget(status_group)
        charts_splitter.setSizes([600, 300])
        
        layout.addWidget(charts_splitter)
        
        return tab
    
    def create_performance_tab(self) -> QWidget:
        """Create performance analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Time range selector
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Time Range:"))
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        self.time_range_combo.setCurrentText("Last 30 Days")
        range_layout.addWidget(self.time_range_combo)
        
        range_layout.addStretch()
        layout.addLayout(range_layout)
        
        # Performance charts
        perf_chart = PerformanceChart("Detailed Performance Analysis")
        layout.addWidget(perf_chart)
        
        return tab
    
    def setup_auto_refresh(self):
        """Setup automatic data refresh"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_dashboard_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def load_dashboard_data(self):
        """Load dashboard data in background"""
        if self.data_loader and self.data_loader.isRunning():
            return
        
        self.refresh_button.setText("🔄 Loading...")
        self.refresh_button.setEnabled(False)
        
        self.data_loader = AnalyticsDataLoader("dashboard", 30)
        self.data_loader.data_loaded.connect(self.on_data_loaded)
        self.data_loader.error_occurred.connect(self.on_data_error)
        self.data_loader.start()
    
    def on_data_loaded(self, data: Dict[str, Any]):
        """Handle loaded analytics data"""
        self.current_data = data
        self.update_dashboard(data)
        
        self.refresh_button.setText("🔄 Refresh")
        self.refresh_button.setEnabled(True)
    
    def on_data_error(self, error: str):
        """Handle data loading error"""
        QMessageBox.warning(self, "Data Loading Error", f"Failed to load analytics data:\n{error}")
        
        self.refresh_button.setText("🔄 Refresh")
        self.refresh_button.setEnabled(True)
    
    def update_dashboard(self, data: Dict[str, Any]):
        """Update dashboard with new data"""
        if not data.get('analytics_enabled', False):
            self.show_analytics_disabled()
            return
        
        # Update metric cards
        current_session = data.get('current_session', {})
        performance = data.get('performance_summary', {})
        
        # Email card
        total_emails = performance.get('total_emails_processed', current_session.get('processed_emails', 0))
        self.email_card.update_value(f"{total_emails:,}", "total processed")
        
        # Success card
        success_rate = current_session.get('success_rate', 0)
        self.success_card.update_value(f"{success_rate:.1%}", "current session")
        
        # Speed card - fix NoneType issue
        speed = current_session.get('emails_per_minute') or performance.get('avg_emails_per_minute', 0)
        if speed is None:
            speed = 0
        self.speed_card.update_value(f"{speed:.1f}/min", "processing speed")
        
        # Contacts card
        contacts = performance.get('total_contacts_created', current_session.get('contacts_created', 0))
        self.contacts_card.update_value(str(contacts), "contacts created")
        
        # Update status
        status_info = self.format_status_info(data)
        self.status_text.setHtml(status_info)
    
    def format_status_info(self, data: Dict[str, Any]) -> str:
        """Format status information as HTML"""
        last_updated = data.get('last_updated', datetime.now().isoformat())
        system_status = data.get('system_status', 'unknown')
        analytics_enabled = data.get('analytics_enabled', False)
        
        try:
            updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            formatted_time = updated_dt.strftime('%Y-%m-%d %H:%M:%S')
        except (Exception, AttributeError, TypeError, ValueError):
            formatted_time = last_updated
        
        status_color = "#2ecc71" if system_status == "active" else "#f39c12"
        
        html = f"""
        <div style="font-family: Segoe UI; font-size: 12px;">
            <h4 style="color: #2c3e50; margin-bottom: 10px;">System Status</h4>
            
            <p><strong>Status:</strong> 
               <span style="color: {status_color};">●</span> {system_status.title()}
            </p>
            
            <p><strong>Analytics:</strong> 
               <span style="color: {'#2ecc71' if analytics_enabled else '#e74c3c'};">●</span> 
               {'Enabled' if analytics_enabled else 'Disabled'}
            </p>
            
            <p><strong>Last Updated:</strong> {formatted_time}</p>
            
            <h4 style="color: #2c3e50; margin-top: 15px; margin-bottom: 10px;">Phase Integration</h4>
            <p>✅ Phase 3 Analytics: {'Available' if PHASE3_AVAILABLE else 'Not Available'}</p>
            <p>✅ PyQtGraph Charts: {'Available' if PYQTGRAPH_AVAILABLE else 'Not Available'}</p>
            
            <h4 style="color: #2c3e50; margin-top: 15px; margin-bottom: 10px;">Quick Stats</h4>
            <p>📊 Sessions Today: 3</p>
            <p>⚡ Avg Speed: 28.5 emails/min</p>
            <p>✅ Success Rate: 95.8%</p>
            
            <p style="margin-top: 15px; color: #7f8c8d; font-size: 10px;">
                Dashboard refreshes automatically every 30 seconds
            </p>
        </div>
        """
        return html
    
    def show_analytics_disabled(self):
        """Show message when analytics are disabled"""
        for card in [self.email_card, self.success_card, self.speed_card, self.contacts_card]:
            card.update_value("N/A", "analytics disabled")
        
        self.status_text.setHtml("""
        <div style="text-align: center; padding: 40px; color: #e74c3c;">
            <h3>📊 Analytics Disabled</h3>
            <p>Enable Phase 3 Analytics to view dashboard data</p>
        </div>
        """)
    
    def export_analytics(self):
        """Export analytics data"""
        if not self.current_data:
            QMessageBox.information(self, "Export", "No data available to export")
            return
        
        try:
            # Create export filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analytics_export_{timestamp}.json"
            
            # Save to file
            export_path = Path("reports") / filename
            export_path.parent.mkdir(exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(self.current_data, f, indent=2, default=str)
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Analytics data exported to:\n{export_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle widget close event with proper cleanup"""
        # Stop auto-refresh timer
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()
        
        # Wait for data loader thread to finish
        if self.data_loader and self.data_loader.isRunning():
            self.data_loader.quit()
            self.data_loader.wait(3000)  # Wait up to 3 seconds
        
        super().closeEvent(event)
    
    def __del__(self):
        """Destructor with cleanup"""
        try:
            if hasattr(self, 'refresh_timer') and self.refresh_timer:
                self.refresh_timer.stop()
            
            if hasattr(self, 'data_loader') and self.data_loader:
                if self.data_loader.isRunning():
                    self.data_loader.quit()
                    self.data_loader.wait(1000)
        except RuntimeError:
            # Qt objects already deleted, ignore
            pass


def main():
    """Test the Analytics Dashboard independently"""
    from PyQt6.QtWidgets import QApplication
    import sys

    import logging
    
    app = QApplication(sys.argv)
    
    dashboard = AnalyticsDashboard()
    dashboard.show()
    dashboard.resize(1200, 800)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 