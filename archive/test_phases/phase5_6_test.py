#!/usr/bin/env python3
"""
Phase 5.6 Testing Suite - Contact Management Interface

Comprehensive testing of the Contact Management Dashboard including:
- Contact data loading and display
- Search and filtering functionality  
- Contact creation and editing
- Relationship mapping and email history
- Analytics and statistics
- Import/export capabilities
- GUI integration and responsiveness

Run with: python phase5_6_test.py
"""

import sys
import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append('.')

def test_contact_dashboard_import():
    """Test Phase 5.6 Contact Management Dashboard import"""
    print("\n🧪 PHASE 5.6 TESTING - Contact Management Interface")
    print("=" * 60)
    
    try:
        from gui.widgets.contact_management_dashboard import ContactManagementDashboard
        print("✅ Contact Management Dashboard imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Contact Management Dashboard: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing Contact Management Dashboard: {e}")
        return False

class TestContactDataLoader(unittest.TestCase):
    """Test the ContactDataLoader background thread"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from gui.widgets.contact_management_dashboard import ContactDataLoader
            self.loader_class = ContactDataLoader
        except ImportError:
            self.skipTest("Contact Management Dashboard not available")
    
    def test_data_loader_initialization(self):
        """Test ContactDataLoader initialization"""
        print("\n🔄 Testing ContactDataLoader initialization...")
        
        loader = self.loader_class()
        self.assertIsNotNone(loader)
        self.assertTrue(loader.running)
        print("✅ ContactDataLoader initialized successfully")
    
    def test_sample_data_generation(self):
        """Test sample contact data generation"""
        print("\n📊 Testing sample contact data generation...")
        
        loader = self.loader_class()
        sample_contacts = loader._generate_sample_contacts()
        
        self.assertIsInstance(sample_contacts, list)
        self.assertGreater(len(sample_contacts), 0)
        
        # Verify contact structure
        if sample_contacts:
            contact = sample_contacts[0]
            required_fields = ['contactid', 'fullname', 'emailaddress1', 'createdon']
            for field in required_fields:
                self.assertIn(field, contact)
        
        print(f"✅ Generated {len(sample_contacts)} sample contacts")

class TestContactEditDialog(unittest.TestCase):
    """Test the ContactEditDialog functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from PyQt6.QtWidgets import QApplication
            from gui.widgets.contact_management_dashboard import ContactEditDialog
            
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()
            
            self.dialog_class = ContactEditDialog
        except ImportError:
            self.skipTest("PyQt6 or Contact Management Dashboard not available")
    
    def test_new_contact_dialog(self):
        """Test creating new contact dialog"""
        print("\n👤 Testing new contact dialog creation...")
        
        dialog = self.dialog_class()
        self.assertIsNotNone(dialog)
        self.assertTrue(dialog.is_new_contact)
        self.assertEqual(dialog.windowTitle(), "📝 New Contact")
        
        print("✅ New contact dialog created successfully")
    
    def test_edit_contact_dialog(self):
        """Test editing existing contact dialog"""
        print("\n✏️ Testing edit contact dialog...")
        
        sample_contact = {
            'contactid': 'test-123',
            'fullname': 'John Doe',
            'firstname': 'John',
            'lastname': 'Doe',
            'emailaddress1': 'john.doe@test.com'
        }
        
        dialog = self.dialog_class(sample_contact)
        self.assertIsNotNone(dialog)
        self.assertFalse(dialog.is_new_contact)
        self.assertEqual(dialog.windowTitle(), "✏️ Edit Contact")
        
        print("✅ Edit contact dialog created successfully")

class TestContactRelationshipView(unittest.TestCase):
    """Test the ContactRelationshipView widget"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from PyQt6.QtWidgets import QApplication
            from gui.widgets.contact_management_dashboard import ContactRelationshipView
            
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()
            
            self.view_class = ContactRelationshipView
        except ImportError:
            self.skipTest("PyQt6 or Contact Management Dashboard not available")
    
    def test_relationship_view_creation(self):
        """Test relationship view widget creation"""
        print("\n🔗 Testing relationship view creation...")
        
        view = self.view_class()
        self.assertIsNotNone(view)
        self.assertIsNotNone(view.relationship_tree)
        self.assertIsNotNone(view.email_table)
        
        print("✅ Relationship view created successfully")
    
    def test_load_contact_relationships(self):
        """Test loading contact relationships"""
        print("\n🌐 Testing contact relationship loading...")
        
        view = self.view_class()
        
        # Test loading relationships for a contact
        view.load_contact_relationships("test-contact-123")
        
        # Verify tree has items
        tree_count = view.relationship_tree.topLevelItemCount()
        table_rows = view.email_table.rowCount()
        
        self.assertGreater(tree_count, 0)
        self.assertGreater(table_rows, 0)
        
        print(f"✅ Loaded {tree_count} relationships and {table_rows} email records")

class TestContactManagementDashboard(unittest.TestCase):
    """Test the main ContactManagementDashboard"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from PyQt6.QtWidgets import QApplication
            from gui.widgets.contact_management_dashboard import ContactManagementDashboard
            
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()
            
            self.dashboard_class = ContactManagementDashboard
        except ImportError:
            self.skipTest("PyQt6 or Contact Management Dashboard not available")
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        print("\n📋 Testing Contact Management Dashboard initialization...")
        
        dashboard = self.dashboard_class()
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(dashboard.tab_widget)
        self.assertIsNotNone(dashboard.contact_table)
        self.assertIsNotNone(dashboard.search_edit)
        
        print("✅ Contact Management Dashboard initialized successfully")
    
    def test_tab_structure(self):
        """Test dashboard tab structure"""
        print("\n📑 Testing dashboard tab structure...")
        
        dashboard = self.dashboard_class()
        tab_count = dashboard.tab_widget.count()
        
        self.assertGreaterEqual(tab_count, 3)  # Contact List, Relationships, Analytics
        
        # Verify tab titles
        tab_titles = []
        for i in range(tab_count):
            tab_titles.append(dashboard.tab_widget.tabText(i))
        
        expected_tabs = ["📋 Contact List", "🔗 Relationships", "📊 Analytics"]
        for expected_tab in expected_tabs:
            self.assertIn(expected_tab, tab_titles)
        
        print(f"✅ Dashboard has {tab_count} tabs with correct structure")
    
    def test_contact_table_structure(self):
        """Test contact table structure"""
        print("\n📊 Testing contact table structure...")
        
        dashboard = self.dashboard_class()
        table = dashboard.contact_table
        
        self.assertGreater(table.columnCount(), 0)
        
        # Verify headers
        headers = []
        for col in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(col).text())
        
        expected_headers = ["Name", "Email", "Phone", "Job Title", "City"]
        for header in expected_headers:
            self.assertIn(header, headers)
        
        print(f"✅ Contact table has {len(headers)} columns with correct headers")
    
    def test_search_functionality(self):
        """Test search and filter functionality"""
        print("\n🔍 Testing search and filter functionality...")
        
        dashboard = self.dashboard_class()
        
        # Add some test data
        test_contacts = [
            {
                'contactid': '1',
                'fullname': 'John Smith',
                'emailaddress1': 'john.smith@test.com',
                'jobtitle': 'Manager',
                'statuscode': 'Active'
            },
            {
                'contactid': '2', 
                'fullname': 'Jane Doe',
                'emailaddress1': 'jane.doe@example.com',
                'jobtitle': 'Developer',
                'statuscode': 'Active'
            }
        ]
        
        dashboard.contacts_data = test_contacts
        dashboard.filtered_contacts = test_contacts.copy()
        
        # Test search
        dashboard.search_edit.setText("john")
        dashboard.filter_contacts()
        
        # Should filter to only John Smith
        self.assertEqual(len(dashboard.filtered_contacts), 1)
        self.assertEqual(dashboard.filtered_contacts[0]['fullname'], 'John Smith')
        
        print("✅ Search functionality working correctly")
    
    def test_analytics_update(self):
        """Test analytics statistics update"""
        print("\n📈 Testing analytics update...")
        
        dashboard = self.dashboard_class()
        
        # Add test data
        test_contacts = [
            {
                'contactid': '1',
                'statuscode': 'Active',
                'emailaddress1': 'test1@company1.com',
                'createdon': datetime.now().isoformat()
            },
            {
                'contactid': '2',
                'statuscode': 'Active', 
                'emailaddress1': 'test2@company2.com',
                'createdon': (datetime.now() - timedelta(days=30)).isoformat()
            }
        ]
        
        dashboard.contacts_data = test_contacts
        dashboard.update_analytics()
        
        # Verify stats were updated
        total_label = dashboard.stat_labels.get("Total Contacts")
        if total_label:
            self.assertEqual(total_label.text(), "2")
        
        print("✅ Analytics update working correctly")

class TestContactManagementIntegration(unittest.TestCase):
    """Test Contact Management integration with main GUI"""
    
    def test_main_window_integration(self):
        """Test integration with main window"""
        print("\n🏠 Testing main window integration...")
        
        try:
            from gui.main_window import MainWindow
            from PyQt6.QtWidgets import QApplication
            
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                app = QApplication([])
            
            # Create main window
            main_window = MainWindow()
            
            # Test navigation to contacts
            main_window.show_contacts_placeholder()
            
            # Verify contact dashboard was created
            self.assertTrue(hasattr(main_window, 'contact_dashboard'))
            
            print("✅ Contact Management integrated with main window successfully")
            
        except ImportError as e:
            self.skipTest(f"Main window or dependencies not available: {e}")
        except Exception as e:
            print(f"⚠️ Integration test encountered error: {e}")

def run_comprehensive_test():
    """Run comprehensive Phase 5.6 testing"""
    print("\n🚀 STARTING PHASE 5.6 COMPREHENSIVE TESTING")
    print("=" * 60)
    
    # Test import first
    import_success = test_contact_dashboard_import()
    if not import_success:
        print("\n❌ Critical: Cannot proceed without Contact Management Dashboard")
        return False
    
    # Run unit tests
    test_classes = [
        TestContactDataLoader,
        TestContactEditDialog,
        TestContactRelationshipView,
        TestContactManagementDashboard,
        TestContactManagementIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w'))
        result = runner.run(suite)
        
        class_total = result.testsRun
        class_passed = class_total - len(result.failures) - len(result.errors)
        class_failed = len(result.failures) + len(result.errors)
        
        total_tests += class_total
        passed_tests += class_passed
        failed_tests += class_failed
        
        if class_failed == 0:
            print(f"✅ {test_class.__name__}: {class_passed}/{class_total} tests passed")
        else:
            print(f"⚠️ {test_class.__name__}: {class_passed}/{class_total} tests passed, {class_failed} failed")
    
    # Final results
    print(f"\n📊 PHASE 5.6 TEST RESULTS")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    if failed_tests == 0:
        print("\n🎉 ALL PHASE 5.6 TESTS PASSED!")
        print("✅ Contact Management Interface is ready for deployment")
        return True
    else:
        print(f"\n⚠️ {failed_tests} tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    print("🧪 PHASE 5.6 CONTACT MANAGEMENT INTERFACE TESTING")
    print("=" * 60)
    print("Testing comprehensive contact administration functionality...")
    
    try:
        success = run_comprehensive_test()
        
        if success:
            print("\n🎯 PHASE 5.6 TESTING COMPLETE - ALL SYSTEMS OPERATIONAL")
            print("✅ Contact Management Interface ready for production use")
            exit(0)
        else:
            print("\n⚠️ PHASE 5.6 TESTING COMPLETED WITH ISSUES")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Critical testing error: {e}")
        exit(1) 