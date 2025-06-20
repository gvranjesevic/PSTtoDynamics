import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice
from gui.widgets.sync_monitoring_dashboard import SyncMetricsWidget

# Ensure a QApplication instance exists for the test run
@pytest.fixture(scope="session")
def qapp_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No need to app.exec_()

def test_sync_metrics_widget_snapshot(qtbot, snapshot, qapp_instance):
    """
    Tests the visual appearance of the SyncMetricsWidget.
    """
    widget = SyncMetricsWidget()
    widget.show()
    qtbot.addWidget(widget)
    
    # Wait for the widget to be fully drawn and painted
    qtbot.waitExposed(widget)
    
    # Grab the widget's visual representation
    pixmap = widget.grab()
    
    # Convert QImage to bytes (PNG format) in memory
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.toImage().save(buffer, "PNG")
    # Explicitly convert QByteArray to bytes
    image_bytes = bytes(buffer.data())

    # The snapshot assertion will now compare the raw bytes of the PNG image
    snapshot.assert_match(image_bytes, 'sync_metrics_widget.png') 