import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QBuffer, QIODevice

from gui.widgets.analytics_dashboard import AnalyticsDashboard
from gui.widgets.ai_intelligence_dashboard import AIIntelligenceDashboard
from gui.widgets.contact_management_dashboard import ContactManagementDashboard
from gui.widgets.sync_monitoring_dashboard import SyncMonitoringDashboard
from gui.widgets.configuration_manager import ConfigurationManager
from gui.widgets.import_wizard import ImportWizard

# Ensure a QApplication instance exists for the test run
@pytest.fixture(scope="session")
def qapp_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def capture_widget_snapshot(widget: QWidget, qtbot) -> bytes:
    """Helper function to capture a widget's pixmap and return its bytes."""
    widget.show()
    qtbot.addWidget(widget)
    qtbot.waitExposed(widget)
    
    pixmap = widget.grab()
    
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.toImage().save(buffer, "PNG")
    return bytes(buffer.data())

@pytest.mark.parametrize("dashboard_class, header_name", [
    (AnalyticsDashboard, "analytics_dashboard_header.png"),
    (AIIntelligenceDashboard, "ai_intelligence_dashboard_header.png"),
    (ContactManagementDashboard, "contact_management_dashboard_header.png"),
    (SyncMonitoringDashboard, "sync_monitoring_dashboard_header.png"),
    (ConfigurationManager, "configuration_manager_header.png"),
    (ImportWizard, "import_wizard_header.png"),
])
def test_dashboard_header_snapshots(qtbot, snapshot, qapp_instance, dashboard_class, header_name):
    """
    Tests the visual appearance of all main dashboard headers.
    """
    dashboard = dashboard_class()
    header = dashboard.create_header()
    
    image_bytes = capture_widget_snapshot(header, qtbot)
    
    snapshot.assert_match(image_bytes, header_name) 