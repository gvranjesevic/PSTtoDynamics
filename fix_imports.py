import os
import re

files_to_fix = [
    'Phase3_Analytics/phase3_integration.py',
    'Phase3_Analytics/timeline_analyzer.py', 
    'Phase3_Analytics/sender_analytics.py'
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace wildcard import
            content = re.sub(r'from config import \*', 'import config', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'Fixed wildcard import in {filepath}')
        except Exception as e:
            print(f'Error fixing {filepath}: {e}')

print('Wildcard import fixes completed') 