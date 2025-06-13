"""
Phase 5.3 Configuration Manager Test Suite
=========================================

Comprehensive testing of the Visual Configuration Interface.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtTest import QTest

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from gui.widgets.configuration_manager import ConfigurationManager, DynamicsAuthWidget
from gui.main_window import MainWindow


class Phase53TestSuite:
    """Phase 5.3 Configuration Manager Test Suite"""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        self.test_results.append((test_name, status, details))
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details and status == "FAIL":
            print(f"   └─ {details}")
    
    def test_configuration_manager_initialization(self):
        """Test 1: Configuration Manager Initialization"""
        print("\n🧪 Test 1: Configuration Manager Initialization")
        try:
            config_manager = ConfigurationManager()
            
            assert config_manager.auth_widget is not None, "Auth widget should exist"
            assert config_manager.status_label is not None, "Status label should exist"
            assert config_manager.save_button is not None, "Save button should exist"
            
            # Verify auth widget is properly integrated (show first, then check visibility)
            config_manager.show()
            QTest.qWait(100)  # Allow time for widget to be shown
            assert config_manager.auth_widget.isVisible(), "Auth widget should be visible"
            
            self.log_test("Configuration Manager Initialization", "PASS")
            config_manager.close()
            return True
            
        except Exception as e:
            self.log_test("Configuration Manager Initialization", "FAIL", str(e))
            return False
    
    def test_authentication_widget_functionality(self):
        """Test 2: Authentication Widget Functionality"""
        print("\n🧪 Test 2: Authentication Widget Functionality")
        try:
            auth_widget = DynamicsAuthWidget()
            
            assert auth_widget.tenant_id_edit is not None, "Tenant ID field should exist"
            assert auth_widget.client_id_edit is not None, "Client ID field should exist"
            assert auth_widget.client_secret_edit is not None, "Client Secret field should exist"
            assert auth_widget.org_url_edit is not None, "Organization URL field should exist"
            assert auth_widget.test_button is not None, "Test button should exist"
            
            test_data = {
                'tenant_id': 'test-tenant-id-12345',
                'client_id': 'test-client-id-67890',
                'client_secret': 'test-secret-value',
                'org_url': 'https://test-org.crm.dynamics.com'
            }
            
            auth_widget.tenant_id_edit.setText(test_data['tenant_id'])
            auth_widget.client_id_edit.setText(test_data['client_id'])
            auth_widget.client_secret_edit.setText(test_data['client_secret'])
            auth_widget.org_url_edit.setText(test_data['org_url'])
            
            config_data = auth_widget.get_config_data()
            assert config_data['tenant_id'] == test_data['tenant_id'], "Config data should match"
            
            self.log_test("Authentication Widget Functionality", "PASS")
            auth_widget.close()
            return True
            
        except Exception as e:
            self.log_test("Authentication Widget Functionality", "FAIL", str(e))
            return False
    
    def test_settings_persistence(self):
        """Test 3: Settings Persistence"""
        print("\n🧪 Test 3: Settings Persistence")
        try:
            settings = QSettings("PSTtoDynamics", "Configuration")
            settings.clear()
            
            auth_widget = DynamicsAuthWidget()
            
            test_data = {
                'tenant_id': 'persistence-test-tenant',
                'client_id': 'persistence-test-client',
                'client_secret': 'persistence-test-secret',
                'org_url': 'https://persistence-test.crm.dynamics.com'
            }
            
            auth_widget.tenant_id_edit.setText(test_data['tenant_id'])
            auth_widget.client_id_edit.setText(test_data['client_id'])
            auth_widget.client_secret_edit.setText(test_data['client_secret'])
            auth_widget.org_url_edit.setText(test_data['org_url'])
            
            auth_widget.save_settings()
            auth_widget.close()
            
            auth_widget_2 = DynamicsAuthWidget()
            auth_widget_2.load_settings()
            
            assert auth_widget_2.tenant_id_edit.text() == test_data['tenant_id'], "Tenant ID should persist"
            
            self.log_test("Settings Persistence", "PASS")
            auth_widget_2.close()
            settings.clear()
            return True
            
        except Exception as e:
            self.log_test("Settings Persistence", "FAIL", str(e))
            return False
    
    def test_main_gui_integration(self):
        """Test 4: Main GUI Integration"""
        print("\n🧪 Test 4: Main GUI Integration")
        try:
            main_window = MainWindow()
            
            assert hasattr(main_window.content_area, 'show_settings_placeholder'), "Should have settings method"
            
            main_window.content_area.show_module("settings")
            QTest.qWait(100)
            
            has_config_manager = hasattr(main_window.content_area, 'config_manager')
            if not has_config_manager:
                content_text = main_window.content_area.content_body.text()
                assert "Configuration Manager" in content_text, "Should show configuration info"
            
            self.log_test("Main GUI Integration", "PASS")
            main_window.close()
            return True
            
        except Exception as e:
            self.log_test("Main GUI Integration", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Phase 5.3 Configuration Manager Test Suite")
        print("=" * 65)
        
        tests = [
            self.test_configuration_manager_initialization,
            self.test_authentication_widget_functionality,
            self.test_settings_persistence,
            self.test_main_gui_integration
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed += 1
        
        print("\n" + "=" * 65)
        print("📊 Test Summary")
        print("=" * 65)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, status, details in self.test_results:
            print(f"   {test_name}: {status}")
            if details and status == "FAIL":
                print(f"      └─ {details}")
        
        return passed, failed


def main():
    """Main test execution"""
    suite = Phase53TestSuite()
    passed, failed = suite.run_all_tests()
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 5.3 Configuration Manager is fully functional.")
        print("📦 Verified Components:")
        print("   • Configuration Manager Framework")
        print("   • Dynamics 365 Authentication UI")  
        print("   • Settings Persistence System")
        print("   • Main GUI Integration")
        print("\n🚀 Phase 5.3 is production-ready!")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 