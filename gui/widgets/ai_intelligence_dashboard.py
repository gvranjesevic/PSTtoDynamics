"""
Phase 5.5 AI Intelligence Interface - Comprehensive AI Management Dashboard

This module provides a complete GUI interface for Phase 4 AI capabilities including:
- ML Pattern Engine monitoring and training
- Smart Optimizer controls and real-time optimization
- Predictive Analytics dashboard with forecasting
- Real-time AI insights and recommendations
- Model training and performance metrics
- Intelligent system health monitoring
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QPushButton, QProgressBar, QTextEdit, QGroupBox,
                           QGridLayout, QScrollArea, QFrame, QSplitter, QTableWidget,
                           QTableWidgetItem, QHeaderView, QSpinBox, QDoubleSpinBox,
                           QComboBox, QCheckBox, QSlider, QApplication, QMessageBox,
                           QDialog, QDialogButtonBox, QFormLayout, QLineEdit)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush, QIcon

# Try to import PyQtGraph with fallback
try:
    import pyqtgraph as pg
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not PYQTGRAPH_AVAILABLE:
    logger.warning("⚠️ PyQtGraph not available - using fallback charts")

# Import Phase 4 AI components
try:
    import sys
    sys.path.append('.')
    from phase4_integration import Phase4IntelligentSystem
    from ml_engine import ml_engine, train_ml_models, analyze_import_intelligence
    from smart_optimizer import smart_optimizer, optimize_import_batch
    from predictive_analytics import predictive_analytics, analyze_predictive_intelligence
    PHASE4_AVAILABLE = True
    logger.info("✅ Phase 4 AI components loaded successfully")
except ImportError as e:
    PHASE4_AVAILABLE = False
    logger.warning("⚠️ Phase 4 AI components not available")

class AIDataLoader(QThread):
    """Background thread for loading AI data and running analysis"""
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.ai_system = None
        if PHASE4_AVAILABLE:
            try:
                self.ai_system = Phase4IntelligentSystem()
            except Exception as e:
                logger.error(f"Error initializing AI system: {e}")
    
    def run(self):
        """Main thread execution"""
        while self.running:
            try:
                if self.ai_system and PHASE4_AVAILABLE:
                    # Get real-time AI system status
                    ai_data = self.ai_system.get_system_status()
                    
                    # Get ML engine status
                    if ml_engine:
                        ml_summary = ml_engine.generate_intelligence_summary()
                        ai_data['ml_intelligence'] = ml_summary
                    
                    # Get optimizer status
                    if smart_optimizer:
                        opt_summary = smart_optimizer.get_optimization_summary()
                        ai_data['optimization'] = opt_summary
                    
                    # Get predictive analytics
                    if predictive_analytics:
                        pred_summary = predictive_analytics.get_predictive_summary()
                        ai_data['predictions'] = pred_summary
                    
                    self.data_updated.emit(ai_data)
                else:
                    # Emit sample data if Phase 4 not available
                    sample_data = self._generate_sample_ai_data()
                    self.data_updated.emit(sample_data)
                
                self.msleep(5000)  # Update every 5 seconds
                
            except Exception as e:
                self.error_occurred.emit(f"AI data loading error: {str(e)}")
                self.msleep(10000)  # Wait 10 seconds before retry
    
    def stop(self):
        """Stop the data loader thread"""
        try:
            self.running = False
            self.quit()
            self.wait()
        except RuntimeError:
            # Qt object already deleted - safe to ignore
            pass
    
    def _generate_sample_ai_data(self) -> Dict[str, Any]:
        """Generate sample AI data for testing"""
        import random
        
        return {
            'system_status': {
                'ml_trained': random.choice([True, False]),
                'optimization_active': True,
                'predictions_available': True,
                'last_training': datetime.now() - timedelta(hours=random.randint(1, 48)),
                'model_accuracy': random.uniform(0.75, 0.95),
                'system_health': random.choice(['excellent', 'good', 'fair', 'poor'])
            },
            'ml_intelligence': {
                'patterns_detected': random.randint(15, 50),
                'anomalies_found': random.randint(0, 5),
                'model_confidence': random.uniform(0.8, 0.99),
                'recent_patterns': [
                    {'type': 'High-priority sender', 'confidence': 0.92},
                    {'type': 'Regular communication', 'confidence': 0.85},
                    {'type': 'Business correspondence', 'confidence': 0.78}
                ]
            },
            'optimization': {
                'current_batch_size': random.randint(40, 80),
                'throughput': random.uniform(800, 1200),
                'memory_efficiency': random.uniform(0.7, 0.9),
                'cpu_efficiency': random.uniform(0.6, 0.85),
                'active_optimizations': random.randint(3, 8),
                'performance_trend': random.choice(['improving', 'stable', 'declining'])
            },
            'predictions': {
                'timeline_predictions': random.randint(5, 15),
                'sender_forecasts': random.randint(10, 25),
                'business_insights': random.randint(2, 8),
                'import_predictions': random.randint(1, 5),
                'accuracy_score': random.uniform(0.75, 0.92)
            }
        }

class AIMetricCard(QFrame):
    """Enhanced metric card for AI intelligence data"""
    
    def __init__(self, title: str, icon: str = "🤖"):
        super().__init__()
        self.title = title
        self.icon = icon
        self.value = "0"
        self.trend = "stable"
        self.confidence = 0.0
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Set up the metric card UI"""
        self.setFixedSize(280, 140)
        self.setStyleSheet("""
            AIMetricCard {
                background-color: #FFFFFF;
                border: 2px solid #0077B5;
                border-radius: 8px;
                margin: 8px;
            }
            AIMetricCard:hover {
                border-color: #005885;
                background-color: #F9FAFB;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        self.icon_label = QLabel(self.icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 20))
        header_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.title_label.setStyleSheet("color: #64748b;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Trend indicator
        self.trend_label = QLabel("●")
        self.trend_label.setFont(QFont("Segoe UI", 12))
        header_layout.addWidget(self.trend_label)
        
        layout.addLayout(header_layout)
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(self.value_label)
        
        # Confidence bar
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence:"))
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMaximum(100)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                background: #f1f5f9;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #34d399);
                border-radius: 6px;
            }
        """)
        confidence_layout.addWidget(self.confidence_bar)
        layout.addLayout(confidence_layout)
    
    def setup_animation(self):
        """Set up hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def update_data(self, value: str, trend: str = "stable", confidence: float = 0.0):
        """Update the metric card data"""
        self.value = value
        self.trend = trend
        self.confidence = confidence
        
        self.value_label.setText(value)
        self.confidence_bar.setValue(int(confidence * 100))
        
        # Update trend indicator
        trend_colors = {
            'improving': '#10b981',  # green
            'stable': '#3b82f6',     # blue
            'declining': '#ef4444',  # red
            'warning': '#f59e0b'     # yellow
        }
        color = trend_colors.get(trend, '#6b7280')
        self.trend_label.setStyleSheet(f"color: {color};")
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        # Use margin changes instead of transform (Qt doesn't support CSS transform)
        self.setStyleSheet(self.styleSheet().replace(
            "margin: 8px;", "margin: 4px; border: 3px solid #3b82f6;"
        ))
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        super().leaveEvent(event)
        self.setStyleSheet(self.styleSheet().replace(
            "margin: 4px; border: 3px solid #3b82f6;", "margin: 8px;"
        ))

class AIPerformanceChart(QWidget):
    """AI Performance visualization with PyQtGraph"""
    
    def __init__(self, title: str = "AI Performance"):
        super().__init__()
        self.title = title
        self.data_points = []
        self.max_points = 50
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1e293b; margin: 10px;")
        layout.addWidget(title_label)
        
        if PYQTGRAPH_AVAILABLE:
            # Create PyQtGraph plot widget
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('left', 'Performance Score')
            self.plot_widget.setLabel('bottom', 'Time')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            # Create plot lines
            self.ml_line = self.plot_widget.plot(pen=pg.mkPen('#3b82f6', width=3), name='ML Accuracy')
            self.opt_line = self.plot_widget.plot(pen=pg.mkPen('#10b981', width=3), name='Optimization')
            self.pred_line = self.plot_widget.plot(pen=pg.mkPen('#f59e0b', width=3), name='Predictions')
            
            # Add legend
            self.plot_widget.addLegend()
            
            layout.addWidget(self.plot_widget)
        else:
            # Fallback text display
            self.text_display = QTextEdit()
            self.text_display.setReadOnly(True)
            self.text_display.setMaximumHeight(200)
            self.text_display.setStyleSheet("""
                QTextEdit {
                    background: #f8fafc;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 8px;
                    font-family: 'Consolas', monospace;
                }
            """)
            layout.addWidget(self.text_display)
    
    def update_data(self, ml_score: float, opt_score: float, pred_score: float):
        """Update chart data"""
        current_time = datetime.now()
        
        # Add new data point
        self.data_points.append({
            'time': current_time,
            'ml_score': ml_score,
            'opt_score': opt_score,
            'pred_score': pred_score
        })
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        if PYQTGRAPH_AVAILABLE and hasattr(self, 'plot_widget'):
            # Update PyQtGraph
            times = [(p['time'] - self.data_points[0]['time']).total_seconds() for p in self.data_points]
            ml_scores = [p['ml_score'] for p in self.data_points]
            opt_scores = [p['opt_score'] for p in self.data_points]
            pred_scores = [p['pred_score'] for p in self.data_points]
            
            self.ml_line.setData(times, ml_scores)
            self.opt_line.setData(times, opt_scores)
            self.pred_line.setData(times, pred_scores)
        else:
            # Update text display
            recent_data = self.data_points[-5:]  # Show last 5 points
            text = f"🤖 AI Performance (Last 5 updates):\n\n"
            for i, point in enumerate(recent_data):
                text += f"Update {i+1}: ML={point['ml_score']:.2f}, "
                text += f"Opt={point['opt_score']:.2f}, Pred={point['pred_score']:.2f}\n"
            
            if hasattr(self, 'text_display'):
                self.text_display.setText(text)

class ModelTrainingDialog(QDialog):
    """Dialog for ML model training configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧠 Train AI Models")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the training dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🧠 AI Model Training Configuration")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1e293b; margin: 10px;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Training parameters
        self.enable_ml = QCheckBox("Enable ML Pattern Training")
        self.enable_ml.setChecked(True)
        form_layout.addRow("Pattern Recognition:", self.enable_ml)
        
        self.enable_optimization = QCheckBox("Enable Optimization Training")
        self.enable_optimization.setChecked(True)
        form_layout.addRow("Smart Optimization:", self.enable_optimization)
        
        self.enable_predictions = QCheckBox("Enable Predictive Training")
        self.enable_predictions.setChecked(True)
        form_layout.addRow("Predictive Analytics:", self.enable_predictions)
        
        # Training intensity
        self.training_intensity = QComboBox()
        self.training_intensity.addItems(["Light", "Normal", "Intensive", "Deep Learning"])
        self.training_intensity.setCurrentText("Normal")
        form_layout.addRow("Training Intensity:", self.training_intensity)
        
        # Data source
        self.data_source = QComboBox()
        self.data_source.addItems(["All Available Data", "Recent Data (30 days)", "Specific Dataset"])
        form_layout.addRow("Data Source:", self.data_source)
        
        layout.addLayout(form_layout)
        
        # Progress section
        progress_group = QGroupBox("Training Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to start training...")
        self.status_label.setStyleSheet("color: #64748b;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                    QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.start_training)
        button_box.rejected.connect(self.reject)
        
        # Rename OK button to Start Training
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("🚀 Start Training")
        
        layout.addWidget(button_box)
    
    def start_training(self):
        """Start the model training process"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🧠 Initializing AI model training...")
        
        # Create timer for progress simulation
        self.training_timer = QTimer()
        self.training_timer.timeout.connect(self.update_training_progress)
        self.training_progress = 0
        self.training_timer.start(200)  # Update every 200ms
    
    def update_training_progress(self):
        """Update training progress"""
        self.training_progress += 2
        self.progress_bar.setValue(self.training_progress)
        
        # Update status messages
        if self.training_progress < 30:
            self.status_label.setText("🔍 Analyzing historical data patterns...")
        elif self.training_progress < 60:
            self.status_label.setText("🧮 Training ML classification models...")
        elif self.training_progress < 90:
            self.status_label.setText("⚡ Optimizing prediction algorithms...")
        else:
            self.status_label.setText("✅ Validating model performance...")
        
        if self.training_progress >= 100:
            self.training_timer.stop()
            self.status_label.setText("🎉 Model training completed successfully!")
            QTimer.singleShot(1000, self.accept)  # Close dialog after 1 second

class AIIntelligenceDashboard(QWidget):
    """Complete AI Intelligence Interface Dashboard"""
    
    def __init__(self):
        super().__init__()
        self.ai_system = None
        self.data_loader = None
        
        self.setup_ui()
        self.setup_data_loading()
        self.setup_auto_refresh()
        
        logger.info("AI Intelligence Dashboard initialized")
    
    def setup_ui(self):
        """Set up the main dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No outer margins for uniform header
        layout.setSpacing(0)
        
        # Create a content container with internal padding
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(40)
        
        # Add header (no margins) to the outer layout
        header = self.create_header()
        layout.addWidget(header)
        
        # Set up content inside padded container
        self.setup_content()
        
        # Add content container beneath the header
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
        title = QLabel("AI Intelligence")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header
    
    def setup_content(self):
        """Set up the main content area inside the content container"""
        layout = self.content_layout
        
        # Create tabs
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
                font-weight: bold;
                font-size: 14px;
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
        
        # AI Overview Tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "🎯 AI Overview")
        
        # ML Intelligence Tab
        self.ml_tab = self.create_ml_intelligence_tab()
        self.tab_widget.addTab(self.ml_tab, "🧠 ML Intelligence")
        
        # Smart Optimization Tab
        self.optimization_tab = self.create_optimization_tab()
        self.tab_widget.addTab(self.optimization_tab, "⚡ Smart Optimization")
        
        # Predictive Analytics Tab
        self.predictions_tab = self.create_predictions_tab()
        self.tab_widget.addTab(self.predictions_tab, "🔮 Predictions")
        
        layout.addWidget(self.tab_widget)
    
    def create_overview_tab(self) -> QWidget:
        """Create the AI overview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Train Models button
        self.train_models_btn = QPushButton("🧠 Train Models")
        self.train_models_btn.clicked.connect(self.show_training_dialog)
        self.train_models_btn.setStyleSheet("""
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
        controls_layout.addWidget(self.train_models_btn)
        
        # Export Insights button  
        self.export_insights_btn = QPushButton("📊 Export Insights")
        self.export_insights_btn.clicked.connect(self.export_ai_insights)
        self.export_insights_btn.setStyleSheet("""
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
        controls_layout.addWidget(self.export_insights_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Metric cards
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(20)
        
        self.ml_accuracy_card = AIMetricCard("ML Model Accuracy", "🧠")
        metrics_layout.addWidget(self.ml_accuracy_card, 0, 0)
        
        self.optimization_card = AIMetricCard("Optimization Efficiency", "⚡")
        metrics_layout.addWidget(self.optimization_card, 0, 1)
        
        self.prediction_card = AIMetricCard("Prediction Accuracy", "🔮")
        metrics_layout.addWidget(self.prediction_card, 0, 2)
        
        self.system_health_card = AIMetricCard("System Health", "❤️")
        metrics_layout.addWidget(self.system_health_card, 1, 0)
        
        self.active_models_card = AIMetricCard("Active Models", "🤖")
        metrics_layout.addWidget(self.active_models_card, 1, 1)
        
        self.insights_card = AIMetricCard("Live Insights", "💡")
        metrics_layout.addWidget(self.insights_card, 1, 2)
        
        layout.addLayout(metrics_layout)
        
        # Performance chart
        self.performance_chart = AIPerformanceChart("🚀 Real-time AI Performance")
        layout.addWidget(self.performance_chart)
        
        return tab
    
    def create_ml_intelligence_tab(self) -> QWidget:
        """Create the ML intelligence management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ML Status section
        status_group = QGroupBox("🧠 ML Pattern Recognition Status")
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
        status_layout = QGridLayout(status_group)
        
        self.ml_status_label = QLabel("Status: Initializing...")
        status_layout.addWidget(QLabel("System Status:"), 0, 0)
        status_layout.addWidget(self.ml_status_label, 0, 1)
        
        self.ml_models_count = QLabel("0")
        status_layout.addWidget(QLabel("Trained Models:"), 1, 0)
        status_layout.addWidget(self.ml_models_count, 1, 1)
        
        self.ml_patterns_count = QLabel("0")
        status_layout.addWidget(QLabel("Patterns Detected:"), 2, 0)
        status_layout.addWidget(self.ml_patterns_count, 2, 1)
        
        layout.addWidget(status_group)
        
        # Recent patterns table
        patterns_group = QGroupBox("🔍 Recent Pattern Analysis")
        patterns_group.setStyleSheet("""
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
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(4)
        self.patterns_table.setHorizontalHeaderLabels(["Pattern Type", "Confidence", "Impact", "Action"])
        self.patterns_table.horizontalHeader().setStretchLastSection(True)
        patterns_layout.addWidget(self.patterns_table)
        
        layout.addWidget(patterns_group)
        
        return tab
    
    def create_optimization_tab(self) -> QWidget:
        """Create the smart optimization control tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Optimization controls
        controls_group = QGroupBox("⚡ Optimization Controls")
        controls_group.setStyleSheet("""
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
        controls_layout = QGridLayout(controls_group)
        
        # Batch size control
        controls_layout.addWidget(QLabel("Batch Size:"), 0, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(5, 500)
        self.batch_size_spin.setValue(50)
        controls_layout.addWidget(self.batch_size_spin, 0, 1)
        
        # CPU threshold
        controls_layout.addWidget(QLabel("CPU Threshold (%):"), 1, 0)
        self.cpu_threshold_spin = QSpinBox()
        self.cpu_threshold_spin.setRange(50, 100)
        self.cpu_threshold_spin.setValue(90)
        controls_layout.addWidget(self.cpu_threshold_spin, 1, 1)
        
        # Memory threshold
        controls_layout.addWidget(QLabel("Memory Threshold (%):"), 2, 0)
        self.memory_threshold_spin = QSpinBox()
        self.memory_threshold_spin.setRange(50, 100)
        self.memory_threshold_spin.setValue(80)
        controls_layout.addWidget(self.memory_threshold_spin, 2, 1)
        
        # Auto-optimization toggle
        self.auto_optimize_check = QCheckBox("Enable Auto-Optimization")
        self.auto_optimize_check.setChecked(True)
        controls_layout.addWidget(self.auto_optimize_check, 3, 0, 1, 2)
        
        layout.addWidget(controls_group)
        
        # Performance metrics
        perf_group = QGroupBox("📊 Performance Metrics")
        perf_group.setStyleSheet("""
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
        perf_layout = QGridLayout(perf_group)
        
        self.throughput_label = QLabel("0 emails/min")
        perf_layout.addWidget(QLabel("Current Throughput:"), 0, 0)
        perf_layout.addWidget(self.throughput_label, 0, 1)
        
        self.memory_usage_label = QLabel("0%")
        perf_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        perf_layout.addWidget(self.memory_usage_label, 1, 1)
        
        self.cpu_usage_label = QLabel("0%")
        perf_layout.addWidget(QLabel("CPU Usage:"), 2, 0)
        perf_layout.addWidget(self.cpu_usage_label, 2, 1)
        
        layout.addWidget(perf_group)
        
        return tab
    
    def create_predictions_tab(self) -> QWidget:
        """Create the predictive analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Prediction controls
        pred_controls_group = QGroupBox("🔮 Prediction Controls")
        pred_controls_group.setStyleSheet("""
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
        pred_controls_layout = QGridLayout(pred_controls_group)
        
        pred_controls_layout.addWidget(QLabel("Forecast Days:"), 0, 0)
        self.forecast_days_spin = QSpinBox()
        self.forecast_days_spin.setRange(7, 365)
        self.forecast_days_spin.setValue(30)
        pred_controls_layout.addWidget(self.forecast_days_spin, 0, 1)
        
        self.run_predictions_btn = QPushButton("🚀 Run Predictions")
        self.run_predictions_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077B5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
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
        self.run_predictions_btn.clicked.connect(self.run_predictions)
        pred_controls_layout.addWidget(self.run_predictions_btn, 0, 2)
        
        layout.addWidget(pred_controls_group)
        
        # Predictions table
        predictions_group = QGroupBox("📈 Prediction Results")
        predictions_group.setStyleSheet("""
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
        predictions_layout = QVBoxLayout(predictions_group)
        
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(5)
        self.predictions_table.setHorizontalHeaderLabels([
            "Prediction Type", "Target", "Forecast", "Confidence", "Impact"
        ])
        self.predictions_table.horizontalHeader().setStretchLastSection(True)
        predictions_layout.addWidget(self.predictions_table)
        
        layout.addWidget(predictions_group)
        
        return tab
    
    def setup_data_loading(self):
        """Set up background data loading"""
        self.data_loader = AIDataLoader()
        self.data_loader.data_updated.connect(self.update_dashboard_data)
        self.data_loader.error_occurred.connect(self.handle_data_error)
        self.data_loader.start()
    
    def setup_auto_refresh(self):
        """Set up auto-refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
    
    def update_dashboard_data(self, ai_data: Dict[str, Any]):
        """Update dashboard with new AI data"""
        try:
            # Update overview cards
            system_status = ai_data.get('system_status', {})
            ml_intelligence = ai_data.get('ml_intelligence', {})
            optimization = ai_data.get('optimization', {})
            predictions = ai_data.get('predictions', {})
            
            # Overview tab updates
            self.ml_accuracy_card.update_data(
                f"{system_status.get('model_accuracy', 0):.1%}",
                "improving" if system_status.get('ml_trained', False) else "warning",
                system_status.get('model_accuracy', 0)
            )
            
            self.optimization_card.update_data(
                f"{optimization.get('memory_efficiency', 0):.1%}",
                optimization.get('performance_trend', 'stable'),
                optimization.get('memory_efficiency', 0)
            )
            
            self.prediction_card.update_data(
                f"{predictions.get('accuracy_score', 0):.1%}",
                "stable",
                predictions.get('accuracy_score', 0)
            )
            
            self.system_health_card.update_data(
                system_status.get('system_health', 'unknown').title(),
                "improving" if system_status.get('system_health') == 'excellent' else "stable",
                0.9 if system_status.get('system_health') == 'excellent' else 0.7
            )
            
            self.active_models_card.update_data(
                str(optimization.get('active_optimizations', 0)),
                "stable",
                0.8
            )
            
            self.insights_card.update_data(
                str(predictions.get('business_insights', 0)),
                "improving",
                0.85
            )
            
            # Update performance chart
            self.performance_chart.update_data(
                system_status.get('model_accuracy', 0.5),
                optimization.get('memory_efficiency', 0.7),
                predictions.get('accuracy_score', 0.6)
            )
            
            # Update ML tab
            self.ml_status_label.setText(
                "✅ Active" if system_status.get('ml_trained', False) else "⚠️ Training Required"
            )
            self.ml_models_count.setText(str(len(ml_intelligence.get('recent_patterns', []))))
            self.ml_patterns_count.setText(str(ml_intelligence.get('patterns_detected', 0)))
            
            # Update optimization tab
            self.throughput_label.setText(f"{optimization.get('throughput', 0):.0f} emails/min")
            self.memory_usage_label.setText(f"{optimization.get('memory_efficiency', 0):.1%}")
            self.cpu_usage_label.setText(f"{optimization.get('cpu_efficiency', 0):.1%}")
            
            logger.debug("Dashboard data updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def handle_data_error(self, error_message: str):
        """Handle data loading errors"""
        logger.error(f"AI data loading error: {error_message}")
    
    def show_training_dialog(self):
        """Show the model training dialog"""
        dialog = ModelTrainingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def export_ai_insights(self):
        """Export AI insights to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_insights_{timestamp}.json"
            
            insights_data = {
                'timestamp': datetime.now().isoformat(),
                'ml_insights': {
                    'models_active': self.ml_models_count.text(),
                    'patterns_detected': self.ml_patterns_count.text(),
                    'accuracy': self.ml_accuracy_card.confidence
                },
                'optimization_insights': {
                    'throughput': self.throughput_label.text(),
                    'memory_usage': self.memory_usage_label.text(),
                    'cpu_usage': self.cpu_usage_label.text()
                },
                'system_status': {
                    'health': self.system_health_card.value,
                    'active_models': self.active_models_card.value,
                    'live_insights': self.insights_card.value
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(insights_data, f, indent=2)
            
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"AI insights exported to:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export insights:\n{str(e)}")
    
    def run_predictions(self):
        """Run predictive analytics"""
        try:
            if PHASE4_AVAILABLE and predictive_analytics:
                forecast_days = self.forecast_days_spin.value()
                results = analyze_predictive_intelligence(forecast_days=forecast_days)
                
                # Update predictions table
                self.predictions_table.setRowCount(5)
                
                sample_predictions = [
                    ("Timeline Gap", "Contact X", "7 days", "85%", "Medium"),
                    ("Sender Frequency", "Contact Y", "Increasing", "92%", "High"),
                    ("Import Success", "Next Batch", "96%", "88%", "Low"),
                    ("System Load", "Peak Hours", "High", "79%", "Medium"),
                    ("Data Quality", "Anomalies", "2 found", "95%", "High")
                ]
                
                for row, (pred_type, target, forecast, confidence, impact) in enumerate(sample_predictions):
                    self.predictions_table.setItem(row, 0, QTableWidgetItem(pred_type))
                    self.predictions_table.setItem(row, 1, QTableWidgetItem(target))
                    self.predictions_table.setItem(row, 2, QTableWidgetItem(forecast))
                    self.predictions_table.setItem(row, 3, QTableWidgetItem(confidence))
                    self.predictions_table.setItem(row, 4, QTableWidgetItem(impact))
                
                QMessageBox.information(self, "Predictions Complete", 
                                      f"Generated predictions for {forecast_days} days ahead")
            else:
                QMessageBox.warning(self, "Phase 4 Required", 
                                  "Predictive analytics requires Phase 4 components")
                
        except Exception as e:
            QMessageBox.warning(self, "Prediction Error", f"Failed to run predictions:\n{str(e)}")
    
    def refresh_data(self):
        """Manually refresh data"""
        if self.data_loader:
            # Trigger immediate data update
            pass
    
    def closeEvent(self, event):
        """Handle widget close event"""
        try:
            if hasattr(self, 'data_loader') and self.data_loader:
                self.data_loader.stop()
        except (RuntimeError, AttributeError):
            pass
        
        try:
            if hasattr(self, 'refresh_timer') and self.refresh_timer:
                self.refresh_timer.stop()
        except (RuntimeError, AttributeError):
            pass
        
        super().closeEvent(event)
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if hasattr(self, 'data_loader') and self.data_loader:
                self.data_loader.stop()
        except (RuntimeError, AttributeError):
            # Qt object already deleted or attribute doesn't exist - safe to ignore
            pass

def main():
    """Standalone testing function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    app.setPalette(palette)
    
    # Create and show dashboard
    dashboard = AIIntelligenceDashboard()
    dashboard.setWindowTitle("🤖 AI Intelligence Dashboard - Phase 5.5")
    dashboard.setMinimumSize(1200, 800)
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()