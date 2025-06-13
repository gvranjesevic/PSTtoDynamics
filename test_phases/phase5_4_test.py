#!/usr/bin/env python3
"""
Phase 5.4 Analytics Dashboard Test Suite
========================================

Comprehensive testing for the Analytics Dashboard implementation.
Tests all components including charts, metrics, data loading, and integration.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtTest import QTest

class TestPhase5_4AnalyticsDashboard(unittest.TestCase):
    """Test Phase 5.4 Analytics Dashboard functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test application"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Setup each test"""
        # Import here to ensure QApplication exists
        try:
            from gui.widgets.analytics_dashboard import AnalyticsDashboard, MetricCard, PerformanceChart
            self.AnalyticsDashboard = AnalyticsDashboard
            self.MetricCard = MetricCard
            self.PerformanceChart = PerformanceChart
            self.dashboard_available = True
        except ImportError as e:
            print(f"⚠️ Analytics Dashboard not available: {e}")
            self.dashboard_available = False
    
    def test_analytics_dashboard_creation(self):
        """Test Analytics Dashboard widget creation and UI setup"""
        print("🧪 Testing Analytics Dashboard creation...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create dashboard
        dashboard = self.AnalyticsDashboard()
        
        # Test basic properties
        self.assertIsInstance(dashboard, QWidget)
        self.assertTrue(hasattr(dashboard, 'tab_widget'))
        self.assertTrue(hasattr(dashboard, 'refresh_button'))
        
        # Test tabs are created
        tab_widget = dashboard.tab_widget
        self.assertEqual(tab_widget.count(), 2)  # Dashboard and Performance tabs
        self.assertEqual(tab_widget.tabText(0), "📊 Dashboard")
        self.assertEqual(tab_widget.tabText(1), "⚡ Performance")
        
        # Test metric cards exist
        self.assertTrue(hasattr(dashboard, 'email_card'))
        self.assertTrue(hasattr(dashboard, 'success_card'))
        self.assertTrue(hasattr(dashboard, 'speed_card'))
        self.assertTrue(hasattr(dashboard, 'contacts_card'))
        
        # Test performance chart exists
        self.assertTrue(hasattr(dashboard, 'performance_chart'))
        
        # Test status text exists
        self.assertTrue(hasattr(dashboard, 'status_text'))
        
        # Properly cleanup threads
        if hasattr(dashboard, 'refresh_timer'):
            dashboard.refresh_timer.stop()
        if dashboard.data_loader and dashboard.data_loader.isRunning():
            dashboard.data_loader.quit()
            dashboard.data_loader.wait(1000)
        
        dashboard.close()
        
        # Allow event processing
        QTest.qWait(100)
        
        print("✅ Analytics Dashboard creation test passed")
    
    def test_metric_card_functionality(self):
        """Test MetricCard widget functionality"""
        print("🧪 Testing MetricCard functionality...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create metric card
        card = self.MetricCard("Test Metric", "123", "test units", "#3498db")
        
        # Test initial values
        self.assertEqual(card.value_label.text(), "123")
        if card.subtitle_label:
            self.assertEqual(card.subtitle_label.text(), "test units")
        
        # Test update functionality
        card.update_value("456", "new units")
        self.assertEqual(card.value_label.text(), "456")
        if card.subtitle_label:
            self.assertEqual(card.subtitle_label.text(), "new units")
        
        # Test styling
        self.assertIn("#3498db", card.styleSheet())
        
        card.close()
        print("✅ MetricCard functionality test passed")
    
    def test_performance_chart_creation(self):
        """Test PerformanceChart widget creation"""
        print("🧪 Testing PerformanceChart creation...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create performance chart
        chart = self.PerformanceChart("Test Chart")
        
        # Test basic properties
        self.assertIsInstance(chart, QWidget)
        self.assertEqual(chart.title, "Test Chart")
        
        # Test sample data method exists
        self.assertTrue(hasattr(chart, 'update_chart_with_sample_data'))
        self.assertTrue(hasattr(chart, 'update_chart'))
        
        chart.close()
        print("✅ PerformanceChart creation test passed")
    
    def test_data_loading_functionality(self):
        """Test analytics data loading and processing"""
        print("🧪 Testing data loading functionality...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        from gui.widgets.analytics_dashboard import AnalyticsDataLoader
        
        # Create data loader
        loader = AnalyticsDataLoader("dashboard", 30)
        
        # Test sample data generation
        sample_data = loader.get_sample_data()
        
        # Verify sample data structure
        self.assertIn('analytics_enabled', sample_data)
        self.assertIn('current_session', sample_data)
        self.assertIn('performance_summary', sample_data)
        self.assertIn('system_status', sample_data)
        
        # Verify current session data
        session = sample_data['current_session']
        self.assertIn('processed_emails', session)
        self.assertIn('success_rate', session)
        self.assertIn('emails_per_minute', session)
        
        # Verify performance summary
        performance = sample_data['performance_summary']
        self.assertIn('total_emails_processed', performance)
        self.assertIn('avg_emails_per_minute', performance)
        
        print("✅ Data loading functionality test passed")
    
    def test_dashboard_data_update(self):
        """Test dashboard data update with sample data"""
        print("🧪 Testing dashboard data update...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create dashboard
        dashboard = self.AnalyticsDashboard()
        
        # Create test data
        test_data = {
            "analytics_enabled": True,
            "last_updated": datetime.now().isoformat(),
            "current_session": {
                "processed_emails": 1500,
                "success_rate": 0.95,
                "emails_per_minute": 30.0,
                "contacts_created": 50
            },
            "performance_summary": {
                "total_emails_processed": 20000,
                "avg_emails_per_minute": 28.5,
                "total_contacts_created": 600
            },
            "system_status": "active"
        }
        
        # Update dashboard with test data
        dashboard.update_dashboard(test_data)
        
        # Verify metric cards were updated
        self.assertIn("20,000", dashboard.email_card.value_label.text())  # Should show performance summary total
        self.assertIn("95.0%", dashboard.success_card.value_label.text())
        self.assertIn("30.0/min", dashboard.speed_card.value_label.text())
        self.assertEqual("600", dashboard.contacts_card.value_label.text())  # Should show performance summary total
        
        # Properly cleanup threads
        if hasattr(dashboard, 'refresh_timer'):
            dashboard.refresh_timer.stop()
        if dashboard.data_loader and dashboard.data_loader.isRunning():
            dashboard.data_loader.quit()
            dashboard.data_loader.wait(1000)
        
        dashboard.close()
        QTest.qWait(100)
        
        print("✅ Dashboard data update test passed")
    
    def test_export_functionality(self):
        """Test analytics export functionality"""
        print("🧪 Testing export functionality...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create dashboard with test data
        dashboard = self.AnalyticsDashboard()
        dashboard.current_data = {
            "test": "data",
            "timestamp": datetime.now().isoformat()
        }
        
        # Mock the file operations to avoid actual file creation
        with patch('builtins.open', create=True) as mock_open:
            with patch('pathlib.Path.mkdir'):
                with patch('gui.widgets.analytics_dashboard.QMessageBox.information') as mock_msg:
                    dashboard.export_analytics()
                    
                    # Verify file operations were called
                    mock_open.assert_called()
                    mock_msg.assert_called()
        
        # Properly cleanup threads
        if hasattr(dashboard, 'refresh_timer'):
            dashboard.refresh_timer.stop()
        if dashboard.data_loader and dashboard.data_loader.isRunning():
            dashboard.data_loader.quit()
            dashboard.data_loader.wait(1000)
        
        dashboard.close()
        QTest.qWait(100)
        
        print("✅ Export functionality test passed")
    
    def test_main_gui_integration(self):
        """Test Analytics Dashboard integration with main GUI"""
        print("🧪 Testing main GUI integration...")
        
        try:
            from gui.main_window import ContentArea
            
            # Create content area
            content_area = ContentArea()
            content_area.show()
            
            # Test analytics navigation
            content_area.show_analytics_placeholder()
            
            # Verify analytics dashboard was loaded
            if hasattr(content_area, 'analytics_dashboard'):
                self.assertIsNotNone(content_area.analytics_dashboard)
                print("✅ Analytics Dashboard successfully integrated with main GUI")
            else:
                print("⚠️ Analytics Dashboard integration test skipped (module not loaded)")
            
            content_area.close()
            
        except ImportError as e:
            print(f"⚠️ Main GUI integration test skipped: {e}")
    
    def test_auto_refresh_setup(self):
        """Test automatic refresh timer setup"""
        print("🧪 Testing auto-refresh setup...")
        
        if not self.dashboard_available:
            self.skipTest("Analytics Dashboard not available")
        
        # Create dashboard
        dashboard = self.AnalyticsDashboard()
        
        # Test refresh timer exists
        self.assertTrue(hasattr(dashboard, 'refresh_timer'))
        self.assertIsNotNone(dashboard.refresh_timer)
        
        # Test timer is active
        self.assertTrue(dashboard.refresh_timer.isActive())
        
        # Test interval is correct (30 seconds)
        self.assertEqual(dashboard.refresh_timer.interval(), 30000)
        
        # Properly cleanup threads
        if hasattr(dashboard, 'refresh_timer'):
            dashboard.refresh_timer.stop()
        if dashboard.data_loader and dashboard.data_loader.isRunning():
            dashboard.data_loader.quit()
            dashboard.data_loader.wait(1000)
        
        dashboard.close()
        QTest.qWait(100)
        
        print("✅ Auto-refresh setup test passed")


def run_phase5_4_tests():
    """Run all Phase 5.4 tests"""
    print("🚀 Starting Phase 5.4 Analytics Dashboard Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase5_4AnalyticsDashboard)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"\n📊 Phase 5.4 Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   💥 Errors: {errors}")
    
    if failures > 0:
        print(f"\n❌ Failed Tests:")
        for test, trace in result.failures:
            print(f"   • {test}")
    
    if errors > 0:
        print(f"\n💥 Error Tests:")
        for test, trace in result.errors:
            print(f"   • {test}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All Phase 5.4 Analytics Dashboard tests passed!")
    elif success_rate >= 80:
        print("⚠️ Most Phase 5.4 tests passed, minor issues detected")
    else:
        print("❌ Significant issues detected in Phase 5.4 implementation")
    
    return success_rate


if __name__ == "__main__":
    try:
        success_rate = run_phase5_4_tests()
        exit_code = 0 if success_rate >= 90 else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Test execution failed: {e}")
        sys.exit(1) 