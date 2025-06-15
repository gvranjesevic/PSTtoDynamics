from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt
import sys

app = QApplication(sys.argv)
main = QWidget()
main_layout = QVBoxLayout(main)
main_layout.setContentsMargins(0, 0, 0, 0)
main_layout.setSpacing(0)

header = QLabel("HEADER")
header.setStyleSheet("background: #0077B5; color: white; font-size: 20px; padding: 12px;")
main_layout.addWidget(header)

scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setFrameShape(QFrame.Shape.NoFrame)
scroll.setSizePolicy(scroll.sizePolicy().horizontalPolicy(), scroll.sizePolicy().verticalPolicy())
scroll_widget = QWidget()
scroll_layout = QVBoxLayout(scroll_widget)
scroll_layout.setContentsMargins(0, 0, 0, 0)
scroll_layout.setSpacing(10)
scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
for i in range(1, 8):
    scroll_layout.addWidget(QLabel(f"Test Label {i}"))
scroll.setWidget(scroll_widget)
main_layout.addWidget(scroll)

main.resize(800, 400)
main.show()
sys.exit(app.exec()) 