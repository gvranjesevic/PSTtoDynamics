from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to PST to Dynamics 365!")
        self.setMinimumSize(500, 350)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("👋 Welcome to PST to Dynamics 365!")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Your professional tool for importing, synchronizing, and managing emails and contacts between PST files and Microsoft Dynamics 365.")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        features = QLabel("""
        <ul>
        <li>📧 Guided Import Wizard</li>
        <li>🔄 Real-time Sync & Conflict Resolution</li>
        <li>📊 Analytics & Monitoring Dashboard</li>
        <li>👥 Contact Management</li>
        <li>🆘 Built-in Help & Support</li>
        </ul>
        """)
        features.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(features)

        layout.addSpacing(10)

        help_label = QLabel("Find help anytime from the Help menu or by hovering over icons for tooltips.")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        get_started_btn = QPushButton("Get Started")
        get_started_btn.clicked.connect(self.accept)
        btn_layout.addWidget(get_started_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout) 