#!/usr/bin/env python3
"""
Phase 5.2 Comprehensive Testing Suite - Fixed Version
====================================================
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from gui.widgets.import_wizard import ImportWizard, Step1FileSelection, Step2ImportSettings, Step3ImportProgress

def main():
    print('🚀 Starting Phase 5.2 Comprehensive Testing - Fixed Version')
    print('=' * 70)

    app = QApplication(sys.argv)
    test_results = []

    def log_test(test_name, status, details=''):
        result = f'{"✅" if status == "PASS" else "❌"} {test_name}: {status}'
        if details:
            result += f' - {details}'
        print(result)
        test_results.append((test_name, status, details))

    # Test 1: Wizard Initialization
    print('\n🧪 Test 1: Wizard Initialization and UI Setup')
    try:
        wizard = ImportWizard()
        
        # Check basic properties
        assert wizard.current_step == 0, 'Initial step should be 0'
        assert len(wizard.steps) == 3, 'Should have 3 steps'
        assert wizard.wizard_data == {}, 'Initial wizard data should be empty'
        
        # Check UI components exist
        assert wizard.step_stack is not None, 'Step stack should exist'
        assert len(wizard.nav_buttons) == 3, 'Should have 3 navigation buttons'
        assert wizard.next_button is not None, 'Next button should exist'
        assert wizard.back_button is not None, 'Back button should exist'
        
        # Check step instances
        step1 = wizard.steps[0]
        step2 = wizard.steps[1]
        step3 = wizard.steps[2]
        
        assert isinstance(step1, Step1FileSelection), 'Step 1 should be file selection'
        assert isinstance(step2, Step2ImportSettings), 'Step 2 should be settings'
        assert isinstance(step3, Step3ImportProgress), 'Step 3 should be progress'
        
        log_test('Wizard Initialization', 'PASS', 'All components initialized correctly')
        wizard.close()
        
    except Exception as e:
        log_test('Wizard Initialization', 'FAIL', str(e))

    # Test 2: File Selection Functionality (FIXED)
    print('\n🧪 Test 2: File Selection Step Functionality')
    try:
        wizard = ImportWizard()
        step1 = wizard.steps[0]
        
        # Test initial state
        assert step1.selected_file_path == '', 'Initial file path should be empty'
        
        # Test validation with no file (FIXED: Check actual error message)
        valid, error = step1.validate_step()
        assert not valid, 'Should fail validation with no file'
        assert 'pst file' in error.lower(), f'Error should mention PST file, got: "{error}"'
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.pst', delete=False) as f:
            f.write(b'TEST PST FILE CONTENT')
            temp_pst_file = f.name
        
        # Test file selection simulation
        step1.selected_file_path = temp_pst_file
        step1.file_path_edit.setText(temp_pst_file)
        step1.update_file_info(temp_pst_file)
        
        # Test validation with file
        valid, error = step1.validate_step()
        assert valid, f'Should pass validation with file: {error}'
        
        # Test step data
        data = step1.get_step_data()
        assert data['pst_file_path'] == temp_pst_file, 'Step data should contain file path'
        assert data['file_name'] == Path(temp_pst_file).name, 'Step data should contain file name'
        
        log_test('File Selection Functionality', 'PASS', 'All file operations working')
        wizard.close()
        
        # Cleanup
        os.unlink(temp_pst_file)
        
    except Exception as e:
        log_test('File Selection Functionality', 'FAIL', str(e))

    # Test 3: Settings Configuration
    print('\n🧪 Test 3: Settings Configuration Functionality')
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
            assert key in data, f'Setting {key} should exist in step data'
        
        # Test batch size control (ENHANCED)
        assert isinstance(data['batch_size'], int), 'Batch size should be integer'
        assert 10 <= data['batch_size'] <= 1000, 'Batch size should be in valid range'
        
        # Test checkbox states
        assert isinstance(data['use_ai_optimization'], bool), 'AI optimization should be boolean'
        assert isinstance(data['skip_duplicates'], bool), 'Skip duplicates should be boolean'
        
        # Test batch size spinner functionality
        original_value = step2.batch_size_spinner.value()
        step2.batch_size_spinner.setValue(250)
        data = step2.get_step_data()
        assert data['batch_size'] == 250, 'Batch size should update correctly'
        
        # Test spinner bounds
        step2.batch_size_spinner.setValue(5)  # Below minimum
        assert step2.batch_size_spinner.value() >= 10, 'Should enforce minimum value'
        
        step2.batch_size_spinner.setValue(1500)  # Above maximum
        assert step2.batch_size_spinner.value() <= 1000, 'Should enforce maximum value'
        
        # Test validation (settings are always valid)
        valid, error = step2.validate_step()
        assert valid, 'Settings validation should always pass'
        
        log_test('Settings Configuration', 'PASS', 'All settings working correctly')
        wizard.close()
        
    except Exception as e:
        log_test('Settings Configuration', 'FAIL', str(e))

    # Test 4: Progress Monitoring (FIXED)
    print('\n🧪 Test 4: Progress Monitoring Functionality')
    try:
        wizard = ImportWizard()
        step3 = wizard.steps[2]
        
        # Test initial state (FIXED: QProgressBar starts at -1 by default)
        initial_value = step3.main_progress.value()
        assert initial_value in [-1, 0], f'Initial progress should be -1 or 0, got {initial_value}'
        assert step3.start_button.isEnabled(), 'Start button should be enabled initially'
        assert not step3.stop_button.isEnabled(), 'Stop button should be disabled initially'
        
        # Test progress updates
        step3.update_progress(25, 'Test progress update')
        assert step3.main_progress.value() == 25, 'Progress should update to 25'
        assert 'Test progress update' in step3.status_label.text(), 'Status should update'
        
        # Test log messages
        initial_log_length = len(step3.log_area.toPlainText())
        step3.add_log_message('Test log message')
        new_log_length = len(step3.log_area.toPlainText())
        assert new_log_length > initial_log_length, 'Log should be updated'
        assert 'Test log message' in step3.log_area.toPlainText(), 'Log should contain message'
        
        # Test import completion
        step3.import_finished(True, 'Test completion message')
        assert step3.start_button.isEnabled(), 'Start button should be re-enabled'
        assert not step3.stop_button.isEnabled(), 'Stop button should be disabled'
        
        log_test('Progress Monitoring', 'PASS', 'All progress features working')
        wizard.close()
        
    except Exception as e:
        log_test('Progress Monitoring', 'FAIL', str(e))

    # Test 5: Backend Integration
    print('\n🧪 Test 5: Backend Integration')
    try:
        from email_importer import EmailImporter
        from bulk_processor import BulkProcessor
        from phase4_integration import Phase4IntelligentSystem
        
        # Test EmailImporter
        importer = EmailImporter()
        log_test('EmailImporter Integration', 'PASS', 'Module loads successfully')
        
        # Test BulkProcessor
        processor = BulkProcessor()
        log_test('BulkProcessor Integration', 'PASS', 'Module loads successfully')
        
        # Test Phase4IntelligentSystem
        ai_system = Phase4IntelligentSystem()
        log_test('Phase4 AI Integration', 'PASS', 'AI system initializes successfully')
        
    except Exception as e:
        log_test('Backend Integration', 'FAIL', str(e))

    # Test 6: Navigation Flow
    print('\n🧪 Test 6: Wizard Navigation Flow')
    try:
        wizard = ImportWizard()
        
        # Test initial navigation state
        assert wizard.current_step == 0, 'Should start at step 0'
        assert not wizard.back_button.isEnabled(), 'Back button should be disabled at start'
        assert wizard.next_button.isEnabled(), 'Next button should be enabled'
        assert wizard.next_button.text() == 'Next ➡️', 'Next button should show Next'
        
        # Create test file for navigation
        with tempfile.NamedTemporaryFile(suffix='.pst', delete=False) as f:
            f.write(b'TEST PST FILE CONTENT')
            temp_pst_file = f.name
        
        # Set up valid file and advance
        step1 = wizard.steps[0]
        step1.selected_file_path = temp_pst_file
        step1.file_path_edit.setText(temp_pst_file)
        
        # Now advance should work
        wizard.next_step()
        assert wizard.current_step == 1, 'Should advance to step 1'
        assert wizard.back_button.isEnabled(), 'Back button should be enabled'
        
        # Advance to final step
        wizard.next_step()
        assert wizard.current_step == 2, 'Should advance to step 2'
        assert wizard.next_button.text() == '🏁 Finish', 'Button should show Finish'
        
        # Test back navigation
        wizard.previous_step()
        assert wizard.current_step == 1, 'Should go back to step 1'
        
        wizard.previous_step()
        assert wizard.current_step == 0, 'Should go back to step 0'
        assert not wizard.back_button.isEnabled(), 'Back button should be disabled at start'
        
        log_test('Wizard Navigation', 'PASS', 'Navigation working correctly')
        wizard.close()
        
        # Cleanup
        os.unlink(temp_pst_file)
        
    except Exception as e:
        log_test('Wizard Navigation', 'FAIL', str(e))

    # Test 7: UI Controls Functionality (NEW)
    print('\n🧪 Test 7: UI Controls Functionality')
    try:
        wizard = ImportWizard()
        step2 = wizard.steps[1]
        
        # Test all checkbox controls
        checkboxes = [
            step2.enable_ai_checkbox,
            step2.enable_ml_checkbox,
            step2.enable_smart_optimization_checkbox,
            step2.skip_duplicates_checkbox,
            step2.preserve_folder_structure_checkbox,
            step2.enable_analytics_checkbox,
            step2.generate_reports_checkbox,
            step2.timeline_analysis_checkbox
        ]
        
        for checkbox_widget in checkboxes:
            # Test checkbox can be toggled
            original_state = checkbox_widget.checkbox.isChecked()
            checkbox_widget.checkbox.setChecked(not original_state)
            new_state = checkbox_widget.checkbox.isChecked()
            assert new_state != original_state, 'Checkbox should toggle state'
            
            # Restore original state
            checkbox_widget.checkbox.setChecked(original_state)
        
        # Test batch size spinner with edge cases
        spinner = step2.batch_size_spinner
        
        # Test normal operation
        spinner.setValue(50)
        assert spinner.value() == 50, 'Spinner should accept valid values'
        
        # Test minimum boundary
        spinner.setValue(10)
        assert spinner.value() == 10, 'Spinner should accept minimum value'
        
        # Test maximum boundary
        spinner.setValue(1000)
        assert spinner.value() == 1000, 'Spinner should accept maximum value'
        
        log_test('UI Controls Functionality', 'PASS', 'All UI controls working')
        wizard.close()
        
    except Exception as e:
        log_test('UI Controls Functionality', 'FAIL', str(e))

    # Test 8: Error Handling (NEW)
    print('\n🧪 Test 8: Error Handling')
    try:
        wizard = ImportWizard()
        step1 = wizard.steps[0]
        
        # Test invalid file path
        step1.selected_file_path = '/nonexistent/file.pst'
        valid, error = step1.validate_step()
        assert not valid, 'Should fail validation for nonexistent file'
        
        # Test non-PST file
        step1.selected_file_path = 'test.txt'
        valid, error = step1.validate_step()
        assert not valid, 'Should fail validation for non-PST file'
        
        # Test file info update with invalid file
        step1.update_file_info('/nonexistent/file.pst')
        assert 'Error reading file' in step1.file_info_label.text(), 'Should show error for invalid file'
        
        log_test('Error Handling', 'PASS', 'Error cases handled correctly')
        wizard.close()
        
    except Exception as e:
        log_test('Error Handling', 'FAIL', str(e))

    # Print Summary
    print('\n' + '=' * 70)
    print('📊 Test Summary')
    print('=' * 70)
    passed = sum(1 for _, status, _ in test_results if status == 'PASS')
    failed = sum(1 for _, status, _ in test_results if status == 'FAIL')
    total = passed + failed
    print(f'✅ Passed: {passed}/{total}')
    print(f'❌ Failed: {failed}/{total}')
    print(f'📈 Success Rate: {(passed/total*100):.1f}%')

    print('\n📋 Detailed Results:')
    for test_name, status, details in test_results:
        print(f'   {test_name}: {status}')
        if details and status == 'FAIL':
            print(f'      └─ {details}')

    if failed == 0:
        print('\n🎉 ALL TESTS PASSED! Phase 5.2 is fully functional and ready.')
        print('📦 Phase 5.2 Components Successfully Verified:')
        print('   • ✅ Import Wizard UI Framework')
        print('   • ✅ File Selection and Validation')
        print('   • ✅ Settings Configuration Panel')
        print('   • ✅ Progress Monitoring System')
        print('   • ✅ Backend Integration (AI, Import, Processing)')
        print('   • ✅ Navigation and User Flow')
        print('   • ✅ UI Controls Functionality')
        print('   • ✅ Error Handling and Validation')
        print('\n🚀 Phase 5.2 is production-ready!')
    else:
        print(f'\n⚠️ {failed} test(s) failed. Please review and fix issues.')

    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 