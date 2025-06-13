#!/usr/bin/env python3
from PyQt6.QtWidgets import QApplication
from gui.widgets.import_wizard import ImportWizard
import sys

app = QApplication(sys.argv)
wizard = ImportWizard()

# Debug Test 1: File selection validation
step1 = wizard.steps[0]
valid, error = step1.validate_step()
print(f'File validation result: valid={valid}, error="{error}"')
print(f'Expected: "select a PST file" in error message')
print(f'Actual check result: {"select a PST file" in error.lower()}')

# Debug Test 2: Progress bar initial value
step3 = wizard.steps[2]
print(f'\nProgress bar details:')
print(f'Initial progress value: {step3.main_progress.value()}')
print(f'Progress bar minimum: {step3.main_progress.minimum()}')
print(f'Progress bar maximum: {step3.main_progress.maximum()}')

wizard.close()
print('\nDebug complete.') 