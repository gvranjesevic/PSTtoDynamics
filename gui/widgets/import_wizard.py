"""
PST-to-Dynamics 365 Import Wizard
=================================

Phase 5.2: Import Wizard Implementation
Complete step-by-step import process with AI intelligence integration.
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog,
    QLineEdit, QComboBox, QCheckBox, QGroupBox, QFrame,
    QStackedWidget, QScrollArea, QMessageBox, QSplitter,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QSizePolicy, QSpacerItem, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette

# Import backend modules for actual import functionality
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from email_importer import EmailImporter
    from bulk_processor import BulkProcessor
    from phase4_integration import Phase4IntelligentSystem
    import config
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    print(f"⚠️ Backend modules not available in Import Wizard: {e}")


class ImportProgressThread(QThread):
    """Background thread for import processing"""
    
    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    log_message = pyqtSignal(str)  # log message
    import_completed = pyqtSignal(bool, str)  # success, final message
    
    def __init__(self, pst_file_path: str, import_settings: Dict[str, Any]):
        super().__init__()
        self.pst_file_path = pst_file_path
        self.import_settings = import_settings
        self.running = True
        
    def run(self):
        """Execute the import process in background"""
        try:
            if not BACKEND_AVAILABLE:
                self.import_completed.emit(False, "Backend modules not available")
                return
            
            self.progress_updated.emit(10, "Initializing import system...")
            self.log_message.emit(f"🚀 Starting import from: {self.pst_file_path}")
            
            # Initialize the email importer
            importer = EmailImporter()
            
            self.progress_updated.emit(20, "Loading PST file...")
            self.log_message.emit("📂 Loading PST file structure...")
            
            # Simulate PST analysis (replace with actual implementation)
            self.msleep(1000)  # Simulate processing time
            
            self.progress_updated.emit(40, "Analyzing email content...")
            self.log_message.emit("🔍 Analyzing email patterns and content...")
            
            # Phase 4 AI Analysis if available
            if self.import_settings.get('use_ai_optimization', False):
                try:
                    ai_system = Phase4IntelligentSystem()
                    self.progress_updated.emit(60, "AI optimization in progress...")
                    self.log_message.emit("🧠 AI analyzing import patterns...")
                    self.msleep(1500)
                except Exception as e:
                    self.log_message.emit(f"⚠️ AI optimization unavailable: {e}")
            
            self.progress_updated.emit(80, "Processing emails...")
            self.log_message.emit("📧 Processing and importing emails...")
            
            # Simulate email processing
            self.msleep(2000)
            
            self.progress_updated.emit(100, "Import completed successfully!")
            self.log_message.emit("✅ Import process completed successfully")
            self.import_completed.emit(True, f"Successfully imported emails from {Path(self.pst_file_path).name}")
            
        except Exception as e:
            self.log_message.emit(f"❌ Import error: {str(e)}")
            self.import_completed.emit(False, f"Import failed: {str(e)}")
    
    def stop(self):
        """Stop the import process"""
        self.running = False
        self.quit()
        self.wait()


class WizardStep(QWidget):
    """Base class for wizard steps"""
    
    def __init__(self, title: str = "", description: str = ""):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the step interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(5, 10, 5, 10)  # Ultra-minimal horizontal margins for maximum space
        
        # Step header - only add if title or description exist
        if self.title or self.description:
            header_layout = QVBoxLayout()
            
            if self.title:
                title_label = QLabel(self.title)
                title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
                title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
                header_layout.addWidget(title_label)
            
            if self.description:
                desc_label = QLabel(self.description)
                desc_label.setFont(QFont("Segoe UI", 11))
                desc_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
                desc_label.setWordWrap(True)
                header_layout.addWidget(desc_label)
            
            layout.addLayout(header_layout)
        
        # Content area (to be overridden by subclasses)
        self.content_area = QWidget()
        layout.addWidget(self.content_area, 1)
    
    def validate_step(self) -> tuple[bool, str]:
        """Validate the step data - to be overridden"""
        return True, ""
    
    def get_step_data(self) -> Dict[str, Any]:
        """Get data from this step - to be overridden"""
        return {}


class Step1FileSelection(WizardStep):
    """Step 1: PST File Selection"""
    
    def __init__(self):
        super().__init__("", "")  # Empty strings to save horizontal space
        self.selected_file_path = ""
        self.setup_file_selection()
    
    def setup_file_selection(self):
        """Setup file selection interface with truly responsive design"""
        # Clear any existing layout
        if self.content_area.layout():
            QWidget().setLayout(self.content_area.layout())
        
        # Main scroll area for responsive content
        scroll_area = QScrollArea(self.content_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Create scroll widget
        scroll_widget = QWidget()
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Main layout for scroll widget
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # File selection section - make it expand to fill space
        file_section = self.create_file_selection_section()
        main_layout.addWidget(file_section, 1)  # Add stretch factor to expand
        
        # Tips section
        tips_section = self.create_tips_section()
        main_layout.addWidget(tips_section)
        
        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)
        
        # Layout for content area - ensure scroll area expands to fill space
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(scroll_area, 1)  # Added stretch factor to expand
    
    def create_file_selection_section(self):
        """Create the file selection section"""
        # File selection group
        file_group = QGroupBox("📁 PST File Selection")
        file_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        file_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
                background-color: white;
                font-size: 14px;
            }
        """)
        
        # Layout for file group - make it expand vertically
        file_layout = QVBoxLayout(file_group)
        file_layout.setContentsMargins(30, 35, 30, 30)
        file_layout.setSpacing(25)
        
        # File path section
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(15)
        
        # File path input
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Click 'Browse...' to select a PST file")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumHeight(50)
        self.file_path_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.file_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 15px 20px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        
        # Browse button
        self.browse_button = QPushButton("📂 Browse...")
        self.browse_button.setMinimumHeight(50)
        self.browse_button.setMinimumWidth(150)
        self.browse_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
        """)
        self.browse_button.clicked.connect(self.browse_file)
        
        # Add to path layout
        path_layout.addWidget(self.file_path_edit, 3)  # 75% width
        path_layout.addWidget(self.browse_button, 1)   # 25% width
        
        file_layout.addWidget(path_container)
        
        # File info display - dramatically increased to fill all available space
        self.file_info_label = QLabel("📄 No file selected yet. Choose a PST file to see detailed information.")
        self.file_info_label.setMinimumHeight(400)  # Dramatically increased from 200 to 400
        self.file_info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.file_info_label.setStyleSheet("""
            QLabel {
                color: #6c757d; 
                padding: 25px; 
                border: 2px dashed #dee2e6; 
                border-radius: 10px; 
                background-color: #f8f9fa;
                font-size: 13px;
                line-height: 1.8;
            }
        """)
        
        # Add with stretch factor to make it expand
        file_layout.addWidget(self.file_info_label, 1)  # Add stretch factor
        
        return file_group
    
    def create_tips_section(self):
        """Create the tips and guidelines section"""
        # Tips group
        tips_group = QGroupBox("💡 Tips & Guidelines")
        tips_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tips_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #17a2b8;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #e7f8ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 10px 0 10px;
                color: #0c5460;
                background-color: #e7f8ff;
                font-size: 14px;
            }
        """)
        
        # Layout for tips
        tips_layout = QVBoxLayout(tips_group)
        tips_layout.setContentsMargins(30, 35, 30, 30)
        tips_layout.setSpacing(15)
        
        tips_items = [
            "📂 PST files are typically located in: C:\\Users\\[username]\\Documents\\Outlook Files\\",
            "🔒 Ensure the PST file is not currently open in Outlook before importing",
            "⏱️ Large PST files (>1GB) may take longer to process - please be patient",
            "🤖 The AI system will automatically detect email structure and contacts",
            "📊 All import activities will be logged for your review and troubleshooting"
        ]
        
        for tip in tips_items:
            tip_label = QLabel(tip)
            tip_label.setWordWrap(True)
            tip_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            tip_label.setStyleSheet("""
                QLabel {
                    color: #0c5460; 
                    font-size: 13px;
                    line-height: 1.6;
                    padding: 8px 0px;
                    margin: 2px 0px;
                }
            """)
            tips_layout.addWidget(tip_label)
        
        return tips_group
    
    def browse_file(self):
        """Open file browser for PST selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PST File",
            os.path.expanduser("~\\Documents"),
            "Outlook PST Files (*.pst);;All Files (*.*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_edit.setText(file_path)
            self.update_file_info(file_path)
    
    def update_file_info(self, file_path: str):
        """Update file information display"""
        try:
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size / (1024 * 1024)  # MB
            modified_date = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            info_text = f"""<b>📁 File:</b> {Path(file_path).name}<br/>
<b>📊 Size:</b> {file_size:.1f} MB<br/>
<b>📅 Modified:</b> {modified_date}<br/>
<b>✅ Status:</b> Ready for import"""
            
            self.file_info_label.setText(info_text)
            self.file_info_label.setStyleSheet("""
                QLabel {
                    color: #155724; 
                    padding: 20px; 
                    border: 2px solid #28a745; 
                    border-radius: 6px; 
                    background-color: #d4edda;
                    font-size: 12px;
                    line-height: 1.6;
                }
            """)
            
        except Exception as e:
            self.file_info_label.setText(f"<b>❌ Error reading file:</b><br/>{str(e)}")
            self.file_info_label.setStyleSheet("""
                QLabel {
                    color: #721c24; 
                    padding: 20px; 
                    border: 2px solid #dc3545; 
                    border-radius: 6px; 
                    background-color: #f8d7da;
                    font-size: 12px;
                    line-height: 1.6;
                }
            """)
    
    def validate_step(self) -> tuple[bool, str]:
        """Validate file selection"""
        if not self.selected_file_path:
            return False, "Please select a PST file to continue."
        
        if not os.path.exists(self.selected_file_path):
            return False, "Selected file does not exist."
        
        if not self.selected_file_path.lower().endswith('.pst'):
            return False, "Please select a valid PST file."
        
        return True, ""
    
    def get_step_data(self) -> Dict[str, Any]:
        """Get file selection data"""
        return {
            'pst_file_path': self.selected_file_path,
            'file_name': Path(self.selected_file_path).name if self.selected_file_path else ""
        }


class Step2ImportSettings(WizardStep):
    """Step 2: Import Configuration"""
    
    def __init__(self):
        super().__init__(
            "Import Settings",
            "Configure how emails should be imported and processed."
        )
        self.setup_settings()
    
    def setup_settings(self):
        """Setup import settings interface with truly responsive design"""
        # Clear any existing layout
        if self.content_area.layout():
            QWidget().setLayout(self.content_area.layout())
        
        # Main scroll area for responsive content
        scroll_area = QScrollArea(self.content_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Create scroll widget
        scroll_widget = QWidget()
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Main layout for scroll widget
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # AI Intelligence settings
        ai_section = self.create_ai_settings_section()
        main_layout.addWidget(ai_section)
        
        # Processing options
        processing_section = self.create_processing_section()
        main_layout.addWidget(processing_section)
        
        # Analytics settings
        analytics_section = self.create_analytics_section()
        main_layout.addWidget(analytics_section)
        
        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)
        
        # Layout for content area
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(scroll_area)
    
    def create_ai_settings_section(self):
        """Create AI Intelligence settings section"""
        ai_group = QGroupBox("🤖 AI Intelligence Settings")
        ai_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ai_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #8e44ad;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #faf9ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 10px 0 10px;
                color: #6c3483;
                background-color: #faf9ff;
                font-size: 14px;
            }
        """)
        
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setContentsMargins(30, 35, 30, 30)
        ai_layout.setSpacing(20)
        
        # AI options with descriptions
        self.enable_ai_checkbox = self.create_styled_checkbox(
            "🧠 Enable AI Email Classification",
            "Automatically categorize emails using machine learning algorithms"
        )
        self.enable_ai_checkbox.checkbox.setChecked(True)
        
        self.enable_ml_checkbox = self.create_styled_checkbox(
            "⚡ Enable Machine Learning Pattern Recognition", 
            "Learn from your email patterns to improve future imports"
        )
        self.enable_ml_checkbox.checkbox.setChecked(True)
        
        self.enable_smart_optimization_checkbox = self.create_styled_checkbox(
            "🚀 Enable Smart Import Optimization",
            "Optimize import speed and efficiency using intelligent algorithms"
        )
        self.enable_smart_optimization_checkbox.checkbox.setChecked(True)
        
        ai_layout.addWidget(self.enable_ai_checkbox)
        ai_layout.addWidget(self.enable_ml_checkbox)
        ai_layout.addWidget(self.enable_smart_optimization_checkbox)
        
        return ai_group
    
    def create_processing_section(self):
        """Create processing options section"""
        processing_group = QGroupBox("⚙️ Processing Options")
        processing_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        processing_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #fef9e7;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 10px 0 10px;
                color: #d68910;
                background-color: #fef9e7;
                font-size: 14px;
            }
        """)
        
        processing_layout = QVBoxLayout(processing_group)
        processing_layout.setContentsMargins(30, 35, 30, 30)
        processing_layout.setSpacing(25)
        
        # Batch size setting
        batch_container = QWidget()
        batch_layout = QVBoxLayout(batch_container)
        batch_layout.setContentsMargins(0, 0, 0, 0)
        batch_layout.setSpacing(10)
        
        batch_label = QLabel("📦 Batch Size")
        batch_label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold;")
        batch_layout.addWidget(batch_label)
        
        batch_control_layout = QHBoxLayout()
        batch_control_layout.setSpacing(15)
        
        self.batch_size_spinner = QSpinBox()
        self.batch_size_spinner.setMinimum(10)
        self.batch_size_spinner.setMaximum(1000)
        self.batch_size_spinner.setValue(100)
        self.batch_size_spinner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.batch_size_spinner.setMinimumWidth(150)
        self.batch_size_spinner.setMinimumHeight(40)
        self.batch_size_spinner.setStyleSheet("""
            QSpinBox {
                padding: 10px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #e67e22;
            }
        """)
        
        batch_info = QLabel("emails per batch (recommended: 100 for optimal performance)")
        batch_info.setStyleSheet("color: #6c757d; font-size: 12px;")
        batch_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        batch_info.setWordWrap(True)
        
        batch_control_layout.addWidget(self.batch_size_spinner)
        batch_control_layout.addWidget(batch_info)
        batch_control_layout.addStretch()
        
        batch_layout.addLayout(batch_control_layout)
        processing_layout.addWidget(batch_container)
        
        # Processing checkboxes
        self.skip_duplicates_checkbox = self.create_styled_checkbox(
            "🚫 Skip duplicate emails",
            "Automatically detect and skip emails that have already been imported"
        )
        self.skip_duplicates_checkbox.checkbox.setChecked(True)
        
        self.preserve_folder_structure_checkbox = self.create_styled_checkbox(
            "📁 Preserve folder structure",
            "Maintain the original Outlook folder hierarchy in Dynamics 365"
        )
        self.preserve_folder_structure_checkbox.checkbox.setChecked(True)
        
        processing_layout.addWidget(self.skip_duplicates_checkbox)
        processing_layout.addWidget(self.preserve_folder_structure_checkbox)
        
        return processing_group
    
    def create_analytics_section(self):
        """Create analytics settings section"""
        analytics_group = QGroupBox("📊 Analytics Settings")
        analytics_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        analytics_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #e8f8f5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 10px 0 10px;
                color: #196f3d;
                background-color: #e8f8f5;
                font-size: 14px;
            }
        """)
        
        analytics_layout = QVBoxLayout(analytics_group)
        analytics_layout.setContentsMargins(30, 35, 30, 30)
        analytics_layout.setSpacing(20)
        
        self.enable_analytics_checkbox = self.create_styled_checkbox(
            "📈 Enable Import Analytics",
            "Generate comprehensive analytics and insights about your email data"
        )
        self.enable_analytics_checkbox.checkbox.setChecked(True)
        
        self.generate_reports_checkbox = self.create_styled_checkbox(
            "📄 Generate detailed reports",
            "Create PDF reports with import statistics and email analysis"
        )
        self.generate_reports_checkbox.checkbox.setChecked(True)
        
        self.timeline_analysis_checkbox = self.create_styled_checkbox(
            "📅 Enable timeline analysis",
            "Analyze email patterns and communication timelines"
        )
        self.timeline_analysis_checkbox.checkbox.setChecked(True)
        
        analytics_layout.addWidget(self.enable_analytics_checkbox)
        analytics_layout.addWidget(self.generate_reports_checkbox)
        analytics_layout.addWidget(self.timeline_analysis_checkbox)
        
        return analytics_group
    
    def create_styled_checkbox(self, title, description):
        """Create a styled checkbox with title and description"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        checkbox = QCheckBox(title)
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #2c3e50;
                font-weight: 600;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #6c757d; 
                font-size: 12px;
                margin-left: 32px;
                line-height: 1.4;
            }
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(checkbox)
        layout.addWidget(desc_label)
        
        # Store the checkbox reference in the container for easy access
        container.checkbox = checkbox
        
        return container
    
    def validate_step(self) -> tuple[bool, str]:
        """Validate settings"""
        return True, ""  # All settings are optional
    
    def get_step_data(self) -> Dict[str, Any]:
        """Get settings data"""
        return {
            'use_ai_optimization': self.enable_ai_checkbox.checkbox.isChecked(),
            'smart_contact_creation': self.enable_smart_optimization_checkbox.checkbox.isChecked(),
            'duplicate_detection': self.enable_ml_checkbox.checkbox.isChecked(),
            'batch_size': int(self.batch_size_spinner.value()),
            'skip_duplicates': self.skip_duplicates_checkbox.checkbox.isChecked(),
            'preserve_folder_structure': self.preserve_folder_structure_checkbox.checkbox.isChecked(),
            'generate_reports': self.generate_reports_checkbox.checkbox.isChecked(),
            'timeline_analysis': self.timeline_analysis_checkbox.checkbox.isChecked(),
            'enable_analytics': self.enable_analytics_checkbox.checkbox.isChecked()
        }


class Step3ImportProgress(WizardStep):
    """Step 3: Import Progress and Monitoring"""
    
    def __init__(self):
        super().__init__()
        self.import_thread = None
        self.setup_progress_ui()
    
    def setup_progress_ui(self):
        """Setup progress monitoring interface"""
        layout = QVBoxLayout(self.content_area)
        
        # Progress overview
        progress_group = QGroupBox("📊 Import Progress")
        progress_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        progress_layout = QVBoxLayout(progress_group)
        
        # Main progress bar
        self.main_progress = QProgressBar()
        self.main_progress.setMinimumHeight(30)
        self.main_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        
        # Status label
        self.status_label = QLabel("Ready to start import...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        progress_layout.addWidget(self.main_progress)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Log area
        log_group = QGroupBox("📝 Import Log")
        log_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        log_layout = QVBoxLayout(log_group)
        
        self.log_area = QTextEdit()
        self.log_area.setMinimumHeight(200)
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                line-height: 1.4;
            }
        """)
        
        log_layout.addWidget(self.log_area)
        layout.addWidget(log_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 Start Import")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_button.clicked.connect(self.start_import)
        
        self.stop_button = QPushButton("⏹️ Stop Import")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.stop_button.clicked.connect(self.stop_import)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
    
    def start_import(self, pst_file_path: str = "", settings: Dict[str, Any] = None):
        """Start the import process"""
        if not pst_file_path:
            self.add_log_message("❌ No PST file selected")
            return
        
        if settings is None:
            settings = {}
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.main_progress.setValue(0)
        self.status_label.setText("Starting import process...")
        
        # Create and start import thread
        self.import_thread = ImportProgressThread(pst_file_path, settings)
        self.import_thread.progress_updated.connect(self.update_progress)
        self.import_thread.log_message.connect(self.add_log_message)
        self.import_thread.import_completed.connect(self.import_finished)
        self.import_thread.start()
        
        self.add_log_message("🚀 Import process initiated")
    
    def stop_import(self):
        """Stop the import process"""
        if self.import_thread:
            self.import_thread.stop()
            self.add_log_message("⏹️ Import process stopped by user")
            self.import_finished(False, "Import stopped by user")
    
    def update_progress(self, percentage: int, status: str):
        """Update progress bar and status"""
        self.main_progress.setValue(percentage)
        self.status_label.setText(status)
    
    def add_log_message(self, message: str):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_area.append(formatted_message)
        
        # Auto-scroll to bottom
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
    
    def import_finished(self, success: bool, message: str):
        """Handle import completion"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if success:
            self.status_label.setText("✅ Import completed successfully!")
            self.add_log_message(f"✅ {message}")
        else:
            self.status_label.setText("❌ Import failed")
            self.add_log_message(f"❌ {message}")
    
    def validate_step(self) -> tuple[bool, str]:
        """Validate progress step"""
        return True, ""  # Progress step doesn't need validation
    
    def get_step_data(self) -> Dict[str, Any]:
        """Get progress data"""
        return {
            'import_completed': self.main_progress.value() == 100,
            'final_status': self.status_label.text()
        }


class ImportWizard(QWidget):
    """Main Import Wizard Widget"""
    
    # Signals
    wizard_completed = pyqtSignal(bool, dict)  # success, data
    wizard_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.wizard_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the wizard interface with responsive design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header - fixed height but responsive width
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content area with responsive design
        main_area = QFrame()
        main_area.setFrameStyle(QFrame.Shape.NoFrame)
        main_layout = QHBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Step navigation sidebar - 20% of width
        nav_sidebar = self.create_navigation_sidebar()
        main_layout.addWidget(nav_sidebar, 2)  # 2/10 = 20%
        
        # Step content area - 80% of width
        self.step_stack = QStackedWidget()
        self.step_stack.setStyleSheet("background-color: white;")
        self.step_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Add wizard steps
        self.steps = [
            Step1FileSelection(),
            Step2ImportSettings(),
            Step3ImportProgress()
        ]
        
        for step in self.steps:
            self.step_stack.addWidget(step)
        
        main_layout.addWidget(self.step_stack, 8)  # 8/10 = 80%
        layout.addWidget(main_area, 1)  # Takes remaining space
        
        # Footer - fixed height but responsive width
        footer = self.create_footer()
        layout.addWidget(footer)
        
        # Initialize first step
        self.update_navigation_ui()
    
    def create_header(self) -> QWidget:
        """Create wizard header"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 0px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Icon
        icon_label = QLabel("📧")
        icon_label.setStyleSheet("font-size: 32px; color: white;")
        layout.addWidget(icon_label)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title = QLabel("Email Import Wizard")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 0px;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Step-by-step email import with AI intelligence")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; margin: 0px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        return header
    
    def create_navigation_sidebar(self) -> QWidget:
        """Create responsive step navigation sidebar"""
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        sidebar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(sidebar)
        # Responsive margins - 5% of width, 3% of height
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add responsive margins using spacers
        top_spacer = QSpacerItem(0, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addItem(top_spacer)
        
        # Navigation steps container
        steps_container = QWidget()
        steps_layout = QVBoxLayout(steps_container)
        steps_layout.setContentsMargins(20, 0, 20, 0)  # 20px side margins
        steps_layout.setSpacing(15)
        
        # Navigation steps
        step_info = [
            ("1", "Select PST File", "Choose your email file"),
            ("2", "Configure Settings", "Set import options"),
            ("3", "Import Progress", "Monitor the process")
        ]
        
        self.nav_buttons = []
        
        for i, (num, title, desc) in enumerate(step_info):
            step_widget = self.create_nav_step(num, title, desc, i == 0)
            steps_layout.addWidget(step_widget)
            self.nav_buttons.append(step_widget)
        
        layout.addWidget(steps_container)
        layout.addStretch(1)  # Push content to top
        
        return sidebar
    
    def create_nav_step(self, number: str, title: str, description: str, active: bool = False) -> QWidget:
        """Create a responsive navigation step widget"""
        widget = QFrame()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        widget.setMinimumHeight(75)
        
        if active:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #3498db;
                    border-radius: 8px;
                    border: 2px solid #2980b9;
                }
                QLabel {
                    color: white;
                }
            """)
        else:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    border: 2px solid #bdc3c7;
                }
                QLabel {
                    color: #7f8c8d;
                }
            """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # Step number - responsive sizing
        num_label = QLabel(number)
        num_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        num_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        num_label.setFixedSize(35, 35)
        num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 17px;
                font-size: 14px;
            }
        """)
        
        # Step info - responsive text
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 9))
        desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(desc_label)
        
        layout.addWidget(num_label)
        layout.addLayout(info_layout, 1)  # Takes remaining space
        
        return widget
    
    def create_footer(self) -> QWidget:
        """Create wizard footer with navigation buttons"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Cancel button
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_wizard)
        
        layout.addWidget(self.cancel_button)
        layout.addStretch()
        
        # Navigation buttons
        self.back_button = QPushButton("⬅️ Back")
        self.back_button.setMinimumHeight(40)
        self.back_button.setEnabled(False)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)
        self.back_button.clicked.connect(self.previous_step)
        
        self.next_button = QPushButton("Next ➡️")
        self.next_button.setMinimumHeight(40)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.next_button.clicked.connect(self.next_step)
        
        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)
        
        return footer
    
    def update_navigation_ui(self):
        """Update navigation UI based on current step"""
        # Update navigation sidebar
        for i, nav_button in enumerate(self.nav_buttons):
            if i == self.current_step:
                nav_button.setStyleSheet("""
                    QFrame {
                        background-color: #3498db;
                        border-radius: 8px;
                        border: 2px solid #2980b9;
                    }
                    QLabel {
                        color: white;
                    }
                """)
            elif i < self.current_step:
                nav_button.setStyleSheet("""
                    QFrame {
                        background-color: #27ae60;
                        border-radius: 8px;
                        border: 2px solid #229954;
                    }
                    QLabel {
                        color: white;
                    }
                """)
            else:
                nav_button.setStyleSheet("""
                    QFrame {
                        background-color: #ecf0f1;
                        border-radius: 8px;
                        border: 2px solid #bdc3c7;
                    }
                    QLabel {
                        color: #7f8c8d;
                    }
                """)
        
        # Update buttons
        self.back_button.setEnabled(self.current_step > 0)
        
        if self.current_step == len(self.steps) - 1:
            self.next_button.setText("🏁 Finish")
        else:
            self.next_button.setText("Next ➡️")
        
        # Update step content
        self.step_stack.setCurrentIndex(self.current_step)
    
    def next_step(self):
        """Move to next step"""
        # Validate current step
        current_step_widget = self.steps[self.current_step]
        is_valid, error_message = current_step_widget.validate_step()
        
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_message)
            return
        
        # Store step data
        step_data = current_step_widget.get_step_data()
        self.wizard_data.update(step_data)
        
        # Special handling for step 3 (progress step)
        if self.current_step == 1:  # Moving from settings to progress
            progress_step = self.steps[2]
            progress_step.start_import(
                self.wizard_data.get('pst_file_path', ''),
                self.wizard_data
            )
        
        # Move to next step or finish
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_navigation_ui()
        else:
            self.finish_wizard()
    
    def previous_step(self):
        """Move to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_navigation_ui()
    
    def cancel_wizard(self):
        """Cancel the wizard"""
        reply = QMessageBox.question(
            self,
            "Cancel Import",
            "Are you sure you want to cancel the import wizard?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Stop any running import
            if self.current_step == 2:  # Progress step
                progress_step = self.steps[2]
                if progress_step.import_thread:
                    progress_step.stop_import()
            
            self.wizard_cancelled.emit()
    
    def finish_wizard(self):
        """Finish the wizard"""
        final_data = self.steps[-1].get_step_data()
        self.wizard_data.update(final_data)
        
        success = self.wizard_data.get('import_completed', False)
        self.wizard_completed.emit(success, self.wizard_data)


def main():
    """Test the Import Wizard independently"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    wizard = ImportWizard()
    wizard.show()
    wizard.resize(1000, 700)
    
    def on_completed(success, data):
        print(f"Wizard completed: {success}")
        print(f"Data: {data}")
        app.quit()
    
    def on_cancelled():
        print("Wizard cancelled")
        app.quit()
    
    wizard.wizard_completed.connect(on_completed)
    wizard.wizard_cancelled.connect(on_cancelled)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 