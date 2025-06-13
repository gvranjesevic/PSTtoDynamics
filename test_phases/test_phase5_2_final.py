#!/usr/bin/env python3
"""
Phase 5.2 Final Comprehensive Testing Suite
==========================================
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from gui.widgets.import_wizard import ImportWizard, Step1FileSelection, Step2ImportSettings, Step3ImportProgress

def main():
    print('🚀 Phase 5.2 Final Comprehensive Test Suite')
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
    print('\n🧪 Test 1: Wizard Initialization')
    try:
        wizard = ImportWizard()
        assert wizard.current_step == 0
        assert len(wizard.steps) == 3
        assert len(wizard.nav_buttons) == 3
        log_test('Wizard Initialization', 'PASS')
        wizard.close()
    except Exception as e:
        log_test('Wizard Initialization', 'FAIL', str(e))

    # Test 2: File Selection (FIXED)
    print('\n🧪 Test 2: File Selection')
    try:
        wizard = ImportWizard()
        step1 = wizard.steps[0]
        
        valid, error = step1.validate_step()
        assert not valid
        assert 'pst file' in error.lower()
        
        with tempfile.NamedTemporaryFile(suffix='.pst', delete=False) as f:
            f.write(b'TEST')
            temp_file = f.name
        
        step1.selected_file_path = temp_file
        valid, error = step1.validate_step()
        assert valid
        
        log_test('File Selection', 'PASS')
        wizard.close()
        os.unlink(temp_file)
    except Exception as e:
        log_test('File Selection', 'FAIL', str(e))

    # Test 3: Settings Configuration
    print('\n🧪 Test 3: Settings Configuration')
    try:
        wizard = ImportWizard()
        step2 = wizard.steps[1]
        
        data = step2.get_step_data()
        assert 'batch_size' in data
        assert isinstance(data['batch_size'], int)
        
        step2.batch_size_spinner.setValue(250)
        data = step2.get_step_data()
        assert data['batch_size'] == 250
        
        log_test('Settings Configuration', 'PASS')
        wizard.close()
    except Exception as e:
        log_test('Settings Configuration', 'FAIL', str(e))

    # Test 4: Progress Monitoring (FIXED)
    print('\n🧪 Test 4: Progress Monitoring')
    try:
        wizard = ImportWizard()
        step3 = wizard.steps[2]
        
        # Initial value can be -1 or 0 for QProgressBar
        initial = step3.main_progress.value()
        assert initial in [-1, 0]
        
        step3.update_progress(50, 'Test')
        assert step3.main_progress.value() == 50
        
        log_test('Progress Monitoring', 'PASS')
        wizard.close()
    except Exception as e:
        log_test('Progress Monitoring', 'FAIL', str(e))

    # Test 5: Backend Integration
    print('\n🧪 Test 5: Backend Integration')
    try:
        from email_importer import EmailImporter
        from bulk_processor import BulkProcessor
        from phase4_integration import Phase4IntelligentSystem
        
        EmailImporter()
        BulkProcessor()
        Phase4IntelligentSystem()
        
        log_test('Backend Integration', 'PASS')
    except Exception as e:
        log_test('Backend Integration', 'FAIL', str(e))

    # Test 6: Navigation Flow
    print('\n🧪 Test 6: Navigation Flow')
    try:
        wizard = ImportWizard()
        assert wizard.current_step == 0
        
        with tempfile.NamedTemporaryFile(suffix='.pst', delete=False) as f:
            f.write(b'TEST')
            temp_file = f.name
        
        step1 = wizard.steps[0]
        step1.selected_file_path = temp_file
        
        wizard.next_step()
        assert wizard.current_step == 1
        
        wizard.next_step()
        assert wizard.current_step == 2
        
        wizard.previous_step()
        assert wizard.current_step == 1
        
        log_test('Navigation Flow', 'PASS')
        wizard.close()
        os.unlink(temp_file)
    except Exception as e:
        log_test('Navigation Flow', 'FAIL', str(e))

    # Summary
    print('\n' + '=' * 60)
    print('📊 Test Summary')
    print('=' * 60)
    passed = sum(1 for _, status, _ in test_results if status == 'PASS')
    failed = sum(1 for _, status, _ in test_results if status == 'FAIL')
    total = passed + failed
    print(f'✅ Passed: {passed}/{total}')
    print(f'❌ Failed: {failed}/{total}')
    print(f'📈 Success Rate: {(passed/total*100):.1f}%')

    if failed == 0:
        print('\n🎉 ALL TESTS PASSED! Phase 5.2 is fully functional.')
        print('📦 Verified Components:')
        print('   • Import Wizard Framework')
        print('   • File Selection & Validation')
        print('   • Settings Configuration')
        print('   • Progress Monitoring')
        print('   • Backend Integration')
        print('   • Navigation Flow')
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 