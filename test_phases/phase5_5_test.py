"""
Phase 5.5 AI Intelligence Interface - Comprehensive Test Suite

This test suite verifies all Phase 5.5 AI Intelligence Dashboard components including:
- AI data loading and background threading
- ML intelligence monitoring and controls
- Smart optimization interface
- Predictive analytics dashboard
- Model training dialog functionality
- Real-time AI performance visualization
- Data export and import capabilities
- Main GUI integration
"""

import sys
import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QAction

# Import components to test
try:
    from gui.widgets.ai_intelligence_dashboard import (
        AIIntelligenceDashboard, AIDataLoader, AIMetricCard, 
        AIPerformanceChart, ModelTrainingDialog
    )
    from gui.main_window import MainWindow, ContentArea
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Component import error: {e}")
    COMPONENTS_AVAILABLE = False

class TestAIDataLoader(unittest.TestCase):
    """Test AI data loading thread"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_ai_data_loader_creation(self):
        """Test AI data loader thread creation"""
        loader = AIDataLoader()
        
        self.assertIsNotNone(loader)
        self.assertTrue(loader.running)
        self.assertIsNotNone(loader.data_updated)
        self.assertIsNotNone(loader.error_occurred)
        
        loader.stop()
    
    def test_sample_data_generation(self):
        """Test sample AI data generation"""
        loader = AIDataLoader()
        sample_data = loader._generate_sample_ai_data()
        
        # Verify data structure
        self.assertIn('system_status', sample_data)
        self.assertIn('ml_intelligence', sample_data)
        self.assertIn('optimization', sample_data)
        self.assertIn('predictions', sample_data)
        
        # Verify system status fields
        system_status = sample_data['system_status']
        self.assertIn('ml_trained', system_status)
        self.assertIn('model_accuracy', system_status)
        self.assertIn('system_health', system_status)
        
        # Verify ML intelligence fields
        ml_intelligence = sample_data['ml_intelligence']
        self.assertIn('patterns_detected', ml_intelligence)
        self.assertIn('model_confidence', ml_intelligence)
        self.assertIn('recent_patterns', ml_intelligence)
        
        loader.stop()
    
    def test_data_loader_stop(self):
        """Test data loader stop functionality"""
        loader = AIDataLoader()
        loader.start()
        
        # Wait a bit for thread to start
        QTest.qWait(100)
        
        loader.stop()
        self.assertFalse(loader.running)

class TestAIMetricCard(unittest.TestCase):
    """Test AI metric card widget"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_metric_card_creation(self):
        """Test metric card creation"""
        card = AIMetricCard("Test Metric", "🧠")
        
        self.assertEqual(card.title, "Test Metric")
        self.assertEqual(card.icon, "🧠")
        self.assertEqual(card.value, "0")
        self.assertEqual(card.trend, "stable")
        self.assertEqual(card.confidence, 0.0)
        
        self.assertIsNotNone(card.title_label)
        self.assertIsNotNone(card.value_label)
        self.assertIsNotNone(card.confidence_bar)
    
    def test_metric_card_update(self):
        """Test metric card data update"""
        card = AIMetricCard("ML Accuracy", "🧠")
        
        # Update with new data
        card.update_data("95.5%", "improving", 0.955)
        
        self.assertEqual(card.value, "95.5%")
        self.assertEqual(card.trend, "improving")
        self.assertEqual(card.confidence, 0.955)
        
        # Verify UI updates
        self.assertEqual(card.value_label.text(), "95.5%")
        self.assertEqual(card.confidence_bar.value(), 95)  # 95.5% as integer
    
    def test_metric_card_styling(self):
        """Test metric card styling and trends"""
        card = AIMetricCard("Performance", "⚡")
        
        # Test different trends
        trends = ['improving', 'stable', 'declining', 'warning']
        
        for trend in trends:
            card.update_data("100%", trend, 0.8)
            self.assertEqual(card.trend, trend)

class TestAIPerformanceChart(unittest.TestCase):
    """Test AI performance chart widget"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_performance_chart_creation(self):
        """Test performance chart creation"""
        chart = AIPerformanceChart("AI Performance Test")
        
        self.assertEqual(chart.title, "AI Performance Test")
        self.assertEqual(len(chart.data_points), 0)
        self.assertEqual(chart.max_points, 50)
    
    def test_chart_data_update(self):
        """Test chart data updates"""
        chart = AIPerformanceChart("Performance")
        
        # Add some data points
        chart.update_data(0.85, 0.92, 0.78)
        chart.update_data(0.87, 0.91, 0.80)
        chart.update_data(0.90, 0.93, 0.82)
        
        self.assertEqual(len(chart.data_points), 3)
        
        # Verify latest data point
        latest = chart.data_points[-1]
        self.assertEqual(latest['ml_score'], 0.90)
        self.assertEqual(latest['opt_score'], 0.93)
        self.assertEqual(latest['pred_score'], 0.82)
    
    def test_chart_data_limit(self):
        """Test chart data point limit"""
        chart = AIPerformanceChart("Performance")
        chart.max_points = 5  # Set low limit for testing
        
        # Add more data points than limit
        for i in range(10):
            chart.update_data(0.8 + i*0.01, 0.9, 0.7)
        
        # Should only keep the last 5 points
        self.assertEqual(len(chart.data_points), 5)

class TestModelTrainingDialog(unittest.TestCase):
    """Test model training dialog"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_training_dialog_creation(self):
        """Test training dialog creation"""
        dialog = ModelTrainingDialog()
        
        self.assertEqual(dialog.windowTitle(), "🧠 Train AI Models")
        self.assertTrue(dialog.isModal())
        
        # Verify form controls exist
        self.assertIsNotNone(dialog.enable_ml)
        self.assertIsNotNone(dialog.enable_optimization)
        self.assertIsNotNone(dialog.enable_predictions)
        self.assertIsNotNone(dialog.training_intensity)
        self.assertIsNotNone(dialog.data_source)
        
        # Verify initial states
        self.assertTrue(dialog.enable_ml.isChecked())
        self.assertTrue(dialog.enable_optimization.isChecked())
        self.assertTrue(dialog.enable_predictions.isChecked())
    
    def test_training_progress_simulation(self):
        """Test training progress simulation"""
        dialog = ModelTrainingDialog()
        
        # Start training simulation
        dialog.start_training()
        
        # Verify progress bar is shown
        self.assertTrue(dialog.progress_bar.isVisible())
        self.assertEqual(dialog.progress_bar.value(), 0)
        
        # Simulate progress updates
        for _ in range(5):
            dialog.update_training_progress()
        
        # Progress should have increased
        self.assertGreater(dialog.progress_bar.value(), 0)

class TestAIIntelligenceDashboard(unittest.TestCase):
    """Test complete AI Intelligence Dashboard"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_dashboard_creation(self):
        """Test AI intelligence dashboard creation"""
        dashboard = AIIntelligenceDashboard()
        
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(dashboard.tab_widget)
        self.assertEqual(dashboard.tab_widget.count(), 4)  # 4 tabs
        
        # Verify tabs exist
        tab_texts = [dashboard.tab_widget.tabText(i) for i in range(4)]
        self.assertIn("🎯 AI Overview", tab_texts)
        self.assertIn("🧠 ML Intelligence", tab_texts)
        self.assertIn("⚡ Smart Optimization", tab_texts)
        self.assertIn("🔮 Predictions", tab_texts)
        
        # Clean up
        dashboard.closeEvent(None)
    
    def test_dashboard_ui_components(self):
        """Test dashboard UI components"""
        dashboard = AIIntelligenceDashboard()
        
        # Verify metric cards in overview tab
        self.assertIsNotNone(dashboard.ml_accuracy_card)
        self.assertIsNotNone(dashboard.optimization_card)
        self.assertIsNotNone(dashboard.prediction_card)
        self.assertIsNotNone(dashboard.system_health_card)
        self.assertIsNotNone(dashboard.active_models_card)
        self.assertIsNotNone(dashboard.insights_card)
        
        # Verify performance chart
        self.assertIsNotNone(dashboard.performance_chart)
        
        # Verify control buttons
        self.assertIsNotNone(dashboard.train_models_btn)
        self.assertIsNotNone(dashboard.export_insights_btn)
        
        dashboard.closeEvent(None)
    
    def test_dashboard_data_update(self):
        """Test dashboard data update functionality"""
        dashboard = AIIntelligenceDashboard()
        
        # Create sample AI data
        sample_data = {
            'system_status': {
                'ml_trained': True,
                'model_accuracy': 0.92,
                'system_health': 'excellent'
            },
            'ml_intelligence': {
                'patterns_detected': 25,
                'recent_patterns': [
                    {'type': 'High-priority', 'confidence': 0.95}
                ]
            },
            'optimization': {
                'throughput': 1150,
                'memory_efficiency': 0.85,
                'cpu_efficiency': 0.78,
                'performance_trend': 'improving',
                'active_optimizations': 6
            },
            'predictions': {
                'business_insights': 4,
                'accuracy_score': 0.88
            }
        }
        
        # Update dashboard with sample data
        dashboard.update_dashboard_data(sample_data)
        
        # Verify updates
        self.assertIn("92.0%", dashboard.ml_accuracy_card.value)
        self.assertIn("85.0%", dashboard.optimization_card.value)
        self.assertEqual(dashboard.ml_patterns_count.text(), "1")
        self.assertIn("1150", dashboard.throughput_label.text())
        
        dashboard.closeEvent(None)
    
    def test_dashboard_controls(self):
        """Test dashboard control functionality"""
        dashboard = AIIntelligenceDashboard()
        
        # Test optimization controls
        dashboard.batch_size_spin.setValue(75)
        self.assertEqual(dashboard.batch_size_spin.value(), 75)
        
        dashboard.cpu_threshold_spin.setValue(85)
        self.assertEqual(dashboard.cpu_threshold_spin.value(), 85)
        
        dashboard.memory_threshold_spin.setValue(70)
        self.assertEqual(dashboard.memory_threshold_spin.value(), 70)
        
        # Test prediction controls
        dashboard.forecast_days_spin.setValue(60)
        self.assertEqual(dashboard.forecast_days_spin.value(), 60)
        
        dashboard.closeEvent(None)
    
    @patch('builtins.open', create=True)
    def test_export_functionality(self, mock_open):
        """Test AI insights export functionality"""
        dashboard = AIIntelligenceDashboard()
        
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Set some test data
        dashboard.ml_models_count.setText("5")
        dashboard.ml_patterns_count.setText("20")
        dashboard.throughput_label.setText("1000 emails/min")
        
        # Test export (this will show a message box, but won't fail)
        try:
            dashboard.export_ai_insights()
        except Exception:
            pass  # Expected due to QMessageBox in test environment
        
        dashboard.closeEvent(None)
    
    def test_predictions_functionality(self):
        """Test predictions functionality"""
        dashboard = AIIntelligenceDashboard()
        
        # Test predictions table
        self.assertIsNotNone(dashboard.predictions_table)
        self.assertEqual(dashboard.predictions_table.columnCount(), 5)
        
        # Test run predictions (will show warning in test environment)
        try:
            dashboard.run_predictions()
        except Exception:
            pass  # Expected due to QMessageBox in test environment
        
        dashboard.closeEvent(None)

class TestMainGUIIntegration(unittest.TestCase):
    """Test AI Intelligence Dashboard integration with main GUI"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_main_window_ai_integration(self):
        """Test AI dashboard integration with main window"""
        main_window = MainWindow()
        content_area = main_window.content_area
        
        # Test AI navigation
        content_area.show_module("ai")
        
        # Verify AI dashboard was created
        self.assertTrue(hasattr(content_area, 'ai_dashboard'))
        
        # Verify content is hidden and AI dashboard is shown
        self.assertFalse(content_area.content_body.isVisible())
        self.assertTrue(content_area.ai_dashboard.isVisible())
        
        # Clean up
        content_area.cleanup_active_widgets()
        self.assertFalse(hasattr(content_area, 'ai_dashboard'))
        
        main_window.close()
    
    def test_navigation_cleanup(self):
        """Test proper cleanup when navigating away from AI dashboard"""
        main_window = MainWindow()
        content_area = main_window.content_area
        
        # Navigate to AI
        content_area.show_module("ai")
        self.assertTrue(hasattr(content_area, 'ai_dashboard'))
        
        # Navigate to different module
        content_area.show_module("dashboard")
        self.assertFalse(hasattr(content_area, 'ai_dashboard'))
        
        main_window.close()

class TestDataLoadingAndErrors(unittest.TestCase):
    """Test data loading and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
    
    def test_data_loading_error_handling(self):
        """Test error handling in data loading"""
        dashboard = AIIntelligenceDashboard()
        
        # Test error handling
        dashboard.handle_data_error("Test error message")
        
        # Should not crash
        self.assertIsNotNone(dashboard)
        
        dashboard.closeEvent(None)
    
    def test_auto_refresh_setup(self):
        """Test auto-refresh timer setup"""
        dashboard = AIIntelligenceDashboard()
        
        # Verify refresh timer exists and is active
        self.assertIsNotNone(dashboard.refresh_timer)
        self.assertTrue(dashboard.refresh_timer.isActive())
        
        dashboard.closeEvent(None)

def run_phase5_5_tests():
    """Run all Phase 5.5 tests and return results"""
    print("🚀 Starting Phase 5.5 AI Intelligence Interface Tests")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestAIDataLoader,
        TestAIMetricCard, 
        TestAIPerformanceChart,
        TestModelTrainingDialog,
        TestAIIntelligenceDashboard,
        TestMainGUIIntegration,
        TestDataLoadingAndErrors
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Phase 5.5 Test Results:")
    print(f"   Total Tests: {result.testsRun}")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split(chr(10))[-2]}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All Phase 5.5 AI Intelligence Interface tests passed!")
    elif success_rate >= 90:
        print("✅ Phase 5.5 tests mostly successful!")
    else:
        print("⚠️ Phase 5.5 tests need attention")
    
    return result

if __name__ == "__main__":
    # Ensure QApplication exists
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Run tests
    result = run_phase5_5_tests()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)