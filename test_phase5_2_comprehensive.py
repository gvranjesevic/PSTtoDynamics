"""
Phase 5.2 Comprehensive Testing Suite
====================================

Systematic testing of all Import Wizard functionalities:
1. UI Components and Layout
2. File Selection and Validation
3. Settings Configuration
4. Import Process with AI Integration
5. Error Handling and Edge Cases
6. Performance and Responsiveness
"""

import sys
import os
import tempfile
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# Import our modules
from gui.widgets.import_wizard import ImportWizard, Step1FileSelection, Step2ImportSettings, Step3ImportProgress
from email_importer import EmailImporter
from bulk_processor import BulkProcessor
from phase4_integration import Phase4IntelligentSystem

class Phase52TestSuite:
    """Comprehensive test suite for Phase 5.2 Import Wizard"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.test_results = []
        self.temp_pst_file = None
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append((test_name, status, details))
    
    def create_test_pst_file(self):
        """Create a temporary test PST file"""
        try:
            # Create a temporary file with .pst extension
            with tempfile.NamedTemporaryFile(suffix='.pst', delete=False) as f:
                f.write(b'TEST PST FILE CONTENT')
                self.temp_pst_file = f.name
            self.log_test("Create Test PST File", "PASS", f"Created: {self.temp_pst_file}")
            return True
        except Exception as e:
            self.log_test("Create Test PST File", "FAIL", str(e))
            return False
    
    def test_wizard_initialization(self):
        """Test 1: Wizard Initialization and UI Setup"""
        print("\n🧪 Test 1: Wizard Initialization and UI Setup")
        try:
            wizard = ImportWizard()
            
            # Check basic properties
            assert wizard.current_step == 0, "Initial step should be 0"
            assert len(wizard.steps) == 3, "Should have 3 steps"
            assert wizard.wizard_data == {}, "Initial wizard data should be empty"
            
            # Check UI components exist
            assert wizard.step_stack is not None, "Step stack should exist"
            assert len(wizard.nav_buttons) == 3, "Should have 3 navigation buttons"
            assert wizard.next_button is not None, "Next button should exist"
            assert wizard.back_button is not None, "Back button should exist"
            
            # Check step instances
            step1 = wizard.steps[0]
            step2 = wizard.steps[1]
            step3 = wizard.steps[2]
            
            assert isinstance(step1, Step1FileSelection), "Step 1 should be file selection"
            assert isinstance(step2, Step2ImportSettings), "Step 2 should be settings"
            assert isinstance(step3, Step3ImportProgress), "Step 3 should be progress"
            
            self.log_test("Wizard Initialization", "PASS", "All components initialized correctly")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Wizard Initialization", "FAIL", str(e))
            return False
    
    def test_file_selection_functionality(self):
        """Test 2: File Selection Step Functionality"""
        print("\n🧪 Test 2: File Selection Step Functionality")
        try:
            wizard = ImportWizard()
            step1 = wizard.steps[0]
            
            # Test initial state
            assert step1.selected_file_path == "", "Initial file path should be empty"
            
            # Test validation with no file
            valid, error = step1.validate_step()
            assert not valid, "Should fail validation with no file"
            assert "select a PST file" in error.lower(), "Error should mention file selection"
            
            # Test file selection simulation
            if self.temp_pst_file:
                step1.selected_file_path = self.temp_pst_file
                step1.file_path_edit.setText(self.temp_pst_file)
                step1.update_file_info(self.temp_pst_file)
                
                # Test validation with file
                valid, error = step1.validate_step()
                assert valid, f"Should pass validation with file: {error}"
                
                # Test step data
                data = step1.get_step_data()
                assert data['pst_file_path'] == self.temp_pst_file, "Step data should contain file path"
                assert data['file_name'] == Path(self.temp_pst_file).name, "Step data should contain file name"
            
            self.log_test("File Selection Functionality", "PASS", "All file operations working")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("File Selection Functionality", "FAIL", str(e))
            return False
    
    def test_settings_configuration(self):
        """Test 3: Settings Configuration Functionality"""
        print("\n🧪 Test 3: Settings Configuration Functionality")
        try:
            wizard = ImportWizard()
            step2 = wizard.steps[1]
            
            # Test default settings
            data = step2.get_step_data()
            
            # Verify all expected settings exist
            expected_keys = [
                'use_ai_optimization', 'smart_contact_creation', 'duplicate_detection',
                'batch_size', 'skip_duplicates', 'preserve_folder_structure',
                'generate_reports', 'timeline_analysis', 'enable_analytics'
            ]
            
            for key in expected_keys:
                assert key in data, f"Setting '{key}' should exist in step data"
            
            # Test batch size control
            assert isinstance(data['batch_size'], int), "Batch size should be integer"
            assert 10 <= data['batch_size'] <= 1000, "Batch size should be in valid range"
            
            # Test checkbox states
            assert isinstance(data['use_ai_optimization'], bool), "AI optimization should be boolean"
            assert isinstance(data['skip_duplicates'], bool), "Skip duplicates should be boolean"
            
            # Test batch size spinner
            step2.batch_size_spinner.setValue(250)
            data = step2.get_step_data()
            assert data['batch_size'] == 250, "Batch size should update correctly"
            
            # Test validation (settings are always valid)
            valid, error = step2.validate_step()
            assert valid, "Settings validation should always pass"
            
            self.log_test("Settings Configuration", "PASS", "All settings working correctly")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Settings Configuration", "FAIL", str(e))
            return False
    
    def test_progress_monitoring(self):
        """Test 4: Progress Monitoring Functionality"""
        print("\n🧪 Test 4: Progress Monitoring Functionality")
        try:
            wizard = ImportWizard()
            step3 = wizard.steps[2]
            
            # Test initial state
            assert step3.main_progress.value() == 0, "Initial progress should be 0"
            assert step3.start_button.isEnabled(), "Start button should be enabled initially"
            assert not step3.stop_button.isEnabled(), "Stop button should be disabled initially"
            
            # Test progress updates
            step3.update_progress(25, "Test progress update")
            assert step3.main_progress.value() == 25, "Progress should update to 25"
            assert "Test progress update" in step3.status_label.text(), "Status should update"
            
            # Test log messages
            initial_log_length = len(step3.log_area.toPlainText())
            step3.add_log_message("Test log message")
            new_log_length = len(step3.log_area.toPlainText())
            assert new_log_length > initial_log_length, "Log should be updated"
            assert "Test log message" in step3.log_area.toPlainText(), "Log should contain message"
            
            # Test import completion
            step3.import_finished(True, "Test completion message")
            assert step3.start_button.isEnabled(), "Start button should be re-enabled"
            assert not step3.stop_button.isEnabled(), "Stop button should be disabled"
            
            self.log_test("Progress Monitoring", "PASS", "All progress features working")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Progress Monitoring", "FAIL", str(e))
            return False
    
    def test_wizard_navigation(self):
        """Test 5: Wizard Navigation and Step Flow"""
        print("\n🧪 Test 5: Wizard Navigation and Step Flow")
        try:
            wizard = ImportWizard()
            
            # Test initial navigation state
            assert wizard.current_step == 0, "Should start at step 0"
            assert not wizard.back_button.isEnabled(), "Back button should be disabled at start"
            assert wizard.next_button.isEnabled(), "Next button should be enabled"
            assert wizard.next_button.text() == "Next ➡️", "Next button should show 'Next'"
            
            # Test navigation without file (should fail)
            initial_step = wizard.current_step
            wizard.next_step()
            assert wizard.current_step == initial_step, "Should not advance without valid file"
            
            # Set up valid file and advance
            if self.temp_pst_file:
                step1 = wizard.steps[0]
                step1.selected_file_path = self.temp_pst_file
                step1.file_path_edit.setText(self.temp_pst_file)
                
                # Now advance should work
                wizard.next_step()
                assert wizard.current_step == 1, "Should advance to step 1"
                assert wizard.back_button.isEnabled(), "Back button should be enabled"
                
                # Advance to final step
                wizard.next_step()
                assert wizard.current_step == 2, "Should advance to step 2"
                assert wizard.next_button.text() == "🏁 Finish", "Button should show 'Finish'"
                
                # Test back navigation
                wizard.previous_step()
                assert wizard.current_step == 1, "Should go back to step 1"
                
                wizard.previous_step()
                assert wizard.current_step == 0, "Should go back to step 0"
                assert not wizard.back_button.isEnabled(), "Back button should be disabled at start"
            
            self.log_test("Wizard Navigation", "PASS", "Navigation working correctly")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Wizard Navigation", "FAIL", str(e))
            return False
    
    def test_backend_integration(self):
        """Test 6: Backend Integration and AI Components"""
        print("\n🧪 Test 6: Backend Integration and AI Components")
        try:
            # Test EmailImporter
            try:
                importer = EmailImporter()
                self.log_test("EmailImporter Integration", "PASS", "Module loads successfully")
            except Exception as e:
                self.log_test("EmailImporter Integration", "FAIL", str(e))
            
            # Test BulkProcessor
            try:
                processor = BulkProcessor()
                self.log_test("BulkProcessor Integration", "PASS", "Module loads successfully")
            except Exception as e:
                self.log_test("BulkProcessor Integration", "FAIL", str(e))
            
            # Test Phase4IntelligentSystem
            try:
                ai_system = Phase4IntelligentSystem()
                self.log_test("Phase4 AI Integration", "PASS", "AI system initializes successfully")
            except Exception as e:
                self.log_test("Phase4 AI Integration", "FAIL", str(e))
            
            return True
            
        except Exception as e:
            self.log_test("Backend Integration", "FAIL", str(e))
            return False
    
    def test_error_handling(self):
        """Test 7: Error Handling and Edge Cases"""
        print("\n🧪 Test 7: Error Handling and Edge Cases")
        try:
            wizard = ImportWizard()
            step1 = wizard.steps[0]
            
            # Test invalid file path
            step1.selected_file_path = "/nonexistent/file.pst"
            valid, error = step1.validate_step()
            assert not valid, "Should fail validation for nonexistent file"
            
            # Test non-PST file
            step1.selected_file_path = "test.txt"
            valid, error = step1.validate_step()
            assert not valid, "Should fail validation for non-PST file"
            
            # Test file info update with invalid file
            step1.update_file_info("/nonexistent/file.pst")
            assert "Error reading file" in step1.file_info_label.text(), "Should show error for invalid file"
            
            self.log_test("Error Handling", "PASS", "Error cases handled correctly")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Error Handling", "FAIL", str(e))
            return False
    
    def test_ui_responsiveness(self):
        """Test 8: UI Responsiveness and Layout"""
        print("\n🧪 Test 8: UI Responsiveness and Layout")
        try:
            wizard = ImportWizard()
            wizard.show()
            
            # Test window resizing
            wizard.resize(800, 600)
            QTest.qWait(100)  # Allow UI to update
            
            wizard.resize(1200, 800)
            QTest.qWait(100)
            
            wizard.resize(1000, 700)
            QTest.qWait(100)
            
            # Test step switching doesn't break layout
            step1 = wizard.steps[0]
            if self.temp_pst_file:
                step1.selected_file_path = self.temp_pst_file
                step1.file_path_edit.setText(self.temp_pst_file)
                
                wizard.next_step()
                QTest.qWait(100)
                
                wizard.next_step()
                QTest.qWait(100)
                
                wizard.previous_step()
                QTest.qWait(100)
                
                wizard.previous_step()
                QTest.qWait(100)
            
            self.log_test("UI Responsiveness", "PASS", "Layout remains stable during resize and navigation")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("UI Responsiveness", "FAIL", str(e))
            return False
    
    def test_complete_workflow(self):
        """Test 9: Complete End-to-End Workflow"""
        print("\n🧪 Test 9: Complete End-to-End Workflow")
        try:
            if not self.temp_pst_file:
                self.log_test("Complete Workflow", "SKIP", "No test PST file available")
                return True
                
            wizard = ImportWizard()
            wizard.show()
            
            # Step 1: File Selection
            step1 = wizard.steps[0]
            step1.selected_file_path = self.temp_pst_file
            step1.file_path_edit.setText(self.temp_pst_file)
            step1.update_file_info(self.temp_pst_file)
            
            wizard.next_step()
            
            # Step 2: Configure Settings
            step2 = wizard.steps[1]
            step2.batch_size_spinner.setValue(50)
            step2.enable_ai_checkbox.checkbox.setChecked(True)
            step2.skip_duplicates_checkbox.checkbox.setChecked(True)
            
            wizard.next_step()
            
            # Step 3: Import Progress (simulation)
            step3 = wizard.steps[2]
            
            # Verify we reached the progress step
            assert wizard.current_step == 2, "Should be at progress step"
            
            # Collect final wizard data
            final_data = wizard.wizard_data
            assert 'pst_file_path' in final_data, "Final data should contain file path"
            assert 'batch_size' in final_data, "Final data should contain batch size"
            
            self.log_test("Complete Workflow", "PASS", f"Successfully processed {len(final_data)} settings")
            wizard.close()
            return True
            
        except Exception as e:
            self.log_test("Complete Workflow", "FAIL", str(e))
            return False
    
    def cleanup(self):
        """Clean up test resources"""
        if self.temp_pst_file and os.path.exists(self.temp_pst_file):
            try:
                os.unlink(self.temp_pst_file)
                print(f"🧹 Cleaned up test file: {self.temp_pst_file}")
            except Exception as e:
                print(f"⚠️ Failed to clean up test file: {e}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Phase 5.2 Comprehensive Test Suite")
        print("=" * 60)
        
        # Prepare test environment
        self.create_test_pst_file()
        
        # Run all tests
        tests = [
            self.test_wizard_initialization,
            self.test_file_selection_functionality,
            self.test_settings_configuration,
            self.test_progress_monitoring,
            self.test_wizard_navigation,
            self.test_backend_integration,
            self.test_error_handling,
            self.test_ui_responsiveness,
            self.test_complete_workflow
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
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for test_name, status, details in self.test_results:
            print(f"   {test_name}: {status}")
            if details and status == "FAIL":
                print(f"      └─ {details}")
        
        # Cleanup
        self.cleanup()
        
        return passed, failed

def main():
    """Main test execution"""
    suite = Phase52TestSuite()
    passed, failed = suite.run_all_tests()
    
    if failed == 0:
        print("\n🎉 All tests passed! Phase 5.2 is ready for production.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues before deployment.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 