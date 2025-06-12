"""
Unit tests for the sync monitoring dashboard components.
"""

import unittest
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from sync.sync_engine import SyncEngine
from gui.widgets.sync_monitoring_dashboard import (
    SyncMetricsWidget,
    ConflictResolutionWidget,
    SyncLogWidget,
    SyncMonitoringDashboard
)

class TestSyncMonitoringDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance
        cls.app = QApplication([])
    
    def setUp(self):
        self.sync_engine = SyncEngine()
    
    def test_metrics_widget(self):
        widget = SyncMetricsWidget()
        
        # Test initial state
        self.assertEqual(widget.sync_count_label.text(), "0")
        self.assertEqual(widget.conflict_count_label.text(), "0")
        self.assertEqual(widget.error_count_label.text(), "0")
        
        # Test update
        metrics = {
            'sync_count': 5,
            'conflict_count': 2,
            'error_count': 1
        }
        widget.update_metrics(metrics)
        
        self.assertEqual(widget.sync_count_label.text(), "5")
        self.assertEqual(widget.conflict_count_label.text(), "2")
        self.assertEqual(widget.error_count_label.text(), "1")
    
    def test_conflict_resolution_widget(self):
        widget = ConflictResolutionWidget()
        
        # Test initial state
        self.assertEqual(widget.conflict_table.rowCount(), 0)
        
        # Test adding conflict
        conflict = {
            'field': 'email',
            'source_value': 'source@test.com',
            'target_value': 'target@test.com'
        }
        widget.add_conflict(conflict)
        
        self.assertEqual(widget.conflict_table.rowCount(), 1)
        self.assertEqual(widget.conflict_table.item(0, 0).text(), 'email')
        self.assertEqual(widget.conflict_table.item(0, 1).text(), 'source@test.com')
        self.assertEqual(widget.conflict_table.item(0, 2).text(), 'target@test.com')
    
    def test_sync_log_widget(self):
        widget = SyncLogWidget()
        
        # Test initial state
        self.assertEqual(widget.log_display.toPlainText(), "")
        
        # Test adding log
        log_entry = {
            'timestamp': datetime(2024, 3, 12, 10, 0, 0),
            'event': 'Sync Started',
            'details': {'source': 'PST', 'target': 'Dynamics'}
        }
        widget.add_log(log_entry)
        
        log_text = widget.log_display.toPlainText()
        self.assertIn('2024-03-12 10:00:00', log_text)
        self.assertIn('Sync Started', log_text)
        self.assertIn('PST', log_text)
        self.assertIn('Dynamics', log_text)
    
    def test_sync_monitoring_dashboard(self):
        dashboard = SyncMonitoringDashboard(self.sync_engine)
        
        # Test initial state
        self.assertEqual(dashboard.windowTitle(), "Sync Monitoring Dashboard")
        self.assertIsNotNone(dashboard.metrics_widget)
        self.assertIsNotNone(dashboard.conflict_widget)
        self.assertIsNotNone(dashboard.log_widget)
        
        # Test update
        self.sync_engine.monitor.track_sync('Test Sync')
        dashboard.update_dashboard()
        
        metrics = dashboard.metrics_widget.sync_count_label.text()
        self.assertEqual(metrics, "1")

if __name__ == '__main__':
    unittest.main() 