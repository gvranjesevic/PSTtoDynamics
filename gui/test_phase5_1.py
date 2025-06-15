"""
Phase 5.1 Foundation Automated Tests
===================================

Automated testing for main window framework, navigation, and basic functionality.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

if PYQT_AVAILABLE:
    from gui.main_window import MainWindow, NavigationSidebar, ContentArea, PSTDynamicsApp


class TestPhase51Foundation(unittest.TestCase):
    """Test Phase 5.1 Foundation components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not PYQT_AVAILABLE:
            raise unittest.SkipTest("PyQt6 not available")
            
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up for each test"""
        self.main_window = MainWindow()
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'main_window'):
            self.main_window.close()
    
    def test_main_window_creation(self):
        """Test main window can be created"""
        self.assertIsNotNone(self.main_window)
        self.assertEqual(self.main_window.windowTitle(), "PST-to-Dynamics 365 - AI-Powered Email Import")
        self.assertGreaterEqual(self.main_window.width(), 1200)
        self.assertGreaterEqual(self.main_window.height(), 800)
    
    def test_navigation_sidebar(self):
        """Test navigation sidebar functionality"""
        sidebar = self.main_window.navigation_sidebar
        
        # Check sidebar exists and has correct width
        self.assertIsNotNone(sidebar)
        self.assertEqual(sidebar.width(), 200)  # Updated to compact width
        
        # Check navigation buttons exist
        expected_nav_items = ["dashboard", "import", "analytics", "ai", "contacts", "settings"]
        for nav_id in expected_nav_items:
            self.assertIn(nav_id, sidebar.nav_buttons)
            self.assertIsNotNone(sidebar.nav_buttons[nav_id])
    
    def test_content_area(self):
        """Test content area functionality"""
        content_area = self.main_window.content_area
        
        # Check content area exists
        self.assertIsNotNone(content_area)
        
        # Test module switching (just verify it doesn't crash)
        test_modules = ["dashboard", "import", "analytics", "ai", "contacts", "settings"]
        for module_id in test_modules:
            try:
            content_area.show_module(module_id)
                # Just verify the method runs without error
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"show_module failed for {module_id}: {e}")
    
    def test_menu_bar(self):
        """Test menu bar creation"""
        menubar = self.main_window.menuBar()
        self.assertIsNotNone(menubar)
        
        # Check main menus exist
        menu_titles = [action.text() for action in menubar.actions()]
        expected_menus = ["&File", "&View", "&Tools", "&Help"]
        
        for expected_menu in expected_menus:
            self.assertIn(expected_menu, menu_titles)
    
    def test_status_bar(self):
        """Test status bar functionality"""
        status_bar = self.main_window.statusBar()
        self.assertIsNotNone(status_bar)
        
        # Check status components exist
        self.assertIsNotNone(self.main_window.status_message)
        self.assertIsNotNone(self.main_window.progress_bar)
    
    def test_navigation_signals(self):
        """Test navigation signal handling"""
        # Mock navigation signal
        with patch.object(self.main_window.content_area, 'show_module') as mock_show:
            self.main_window.on_navigate("dashboard")
            mock_show.assert_called_once_with("dashboard")
    
    def test_status_monitoring(self):
        """Test system status monitoring"""
        # Check status monitor is created
        self.assertIsNotNone(self.main_window.status_monitor)
        
        # Test status update
        self.main_window.update_status("Test Status", "#ff0000")
        self.assertEqual(self.main_window.status_message.text(), "Test Status")


class TestNavigationFunctionality(unittest.TestCase):
    """Test navigation-specific functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not PYQT_AVAILABLE:
            raise unittest.SkipTest("PyQt6 not available")
            
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up for each test"""
        self.sidebar = NavigationSidebar()
    
    def test_navigation_button_creation(self):
        """Test navigation buttons are created correctly"""
        # Check all expected buttons exist
        expected_buttons = ["dashboard", "import", "analytics", "ai", "contacts", "settings"]
        
        for button_id in expected_buttons:
            self.assertIn(button_id, self.sidebar.nav_buttons)
            button = self.sidebar.nav_buttons[button_id]
            self.assertIsNotNone(button)
            self.assertEqual(button.height(), 50)  # Updated to compact height
    
    def test_navigation_selection(self):
        """Test navigation item selection"""
        # Test selecting different navigation items
        test_items = ["dashboard", "import", "analytics"]
        
        for item_id in test_items:
            self.sidebar.select_nav_item(item_id)
            # Check button styling changes (basic check)
            selected_button = self.sidebar.nav_buttons[item_id]
            self.assertIsNotNone(selected_button)
    
    def test_status_update(self):
        """Test status indicator updates - SKIPPED: Status indicator removed for compact design"""
        # Status indicator was removed from sidebar for more compact design
        # Status updates now only go to the main status bar
        self.skipTest("Status indicator removed from sidebar for compact design")


class TestApplicationLaunch(unittest.TestCase):
    """Test application launch functionality"""
    
    def test_app_creation(self):
        """Test PSTDynamicsApp can be created"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt6 not available")
        
        # Create app without running it
        with patch('sys.argv', ['test']):
            app = PSTDynamicsApp()
            self.assertIsNotNone(app)
            self.assertEqual(app.applicationName(), "PST to Dynamics 365")
            self.assertEqual(app.applicationVersion(), "1.0.0")


def run_automated_tests():
    """Run all automated tests"""
    print("🧪 Running Phase 5.1 Foundation Automated Tests")
    print("=" * 55)
    
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available - skipping GUI tests")
        return False
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestPhase51Foundation,
        TestNavigationFunctionality,
        TestApplicationLaunch
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 55)
    print("🧪 Test Summary:")
    print(f"   ✅ Tests run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   ⚠️ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('Error:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All tests passed! Phase 5.1 Foundation is ready for manual review.")
    else:
        print("\n⚠️ Some tests failed. Please review before proceeding.")
    
    return success


if __name__ == "__main__":
    success = run_automated_tests()
    sys.exit(0 if success else 1) 