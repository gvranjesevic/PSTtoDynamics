#!/usr/bin/env python3
"""
Phase 5.2 Comprehensive Testing Suite
====================================
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
    print('🚀 Starting Phase 5.2 Comprehensive Testing')
    print('=' * 60)

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

    # Test 2: File Selection Functionality
    print('\n🧪 Test 2: File Selection Step Functionality')
    try:
        wizard = ImportWizard()
        step1 = wizard.steps[0]
        
        # Test initial state
        assert step1.selected_file_path == '', 'Initial file path should be empty'
        
        # Test validation with no file
        valid, error = step1.validate_step()
        assert not valid, 'Should fail validation with no file'
        assert 'select a PST file' in error.lower(), 'Error should mention file selection'
        
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
        
        # Test batch size control
        assert isinstance(data['batch_size'], int), 'Batch size should be integer'
        assert 10 <= data['batch_size'] <= 1000, 'Batch size should be in valid range'
        
        # Test checkbox states
        assert isinstance(data['use_ai_optimization'], bool), 'AI optimization should be boolean'
        assert isinstance(data['skip_duplicates'], bool), 'Skip duplicates should be boolean'
        
        # Test batch size spinner
        step2.batch_size_spinner.setValue(250)
        data = step2.get_step_data()
        assert data['batch_size'] == 250, 'Batch size should update correctly'
        
        # Test validation (settings are always valid)
        valid, error = step2.validate_step()
        assert valid, 'Settings validation should always pass'
        
        log_test('Settings Configuration', 'PASS', 'All settings working correctly')
        wizard.close()
        
    except Exception as e:
        log_test('Settings Configuration', 'FAIL', str(e))

    # Test 4: Progress Monitoring
    print('\n🧪 Test 4: Progress Monitoring Functionality')
    try:
        wizard = ImportWizard()
        step3 = wizard.steps[2]
        
        # Test initial state
        assert step3.main_progress.value() == 0, 'Initial progress should be 0'
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

    # Print Summary
    print('\n' + '=' * 60)
    print('📊 Test Summary')
    print('=' * 60)
    passed = sum(1 for _, status, _ in test_results if status == 'PASS')
    failed = sum(1 for _, status, _ in test_results if status == 'FAIL')
    print(f'✅ Passed: {passed}')
    print(f'❌ Failed: {failed}')
    print(f'📈 Success Rate: {(passed/(passed+failed)*100):.1f}%')

    print('\n📋 Detailed Results:')
    for test_name, status, details in test_results:
        print(f'   {test_name}: {status}')
        if details and status == 'FAIL':
            print(f'      └─ {details}')

    if failed == 0:
        print('\n🎉 All core tests passed! Phase 5.2 functionality is working correctly.')
        print('📦 Phase 5.2 Components Verified:')
        print('   • Import Wizard UI Framework')
        print('   • File Selection and Validation')
        print('   • Settings Configuration Panel')
        print('   • Progress Monitoring System')
        print('   • Backend Integration (AI, Import, Processing)')
        print('   • Navigation and User Flow')
    else:
        print(f'\n⚠️ {failed} test(s) failed. Please review and fix issues.')

    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 