import os
import re

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        bare_count = len(re.findall(r'^\s*except\s*:\s*$', content, re.MULTILINE))
        
        if bare_count > 0:
            content = re.sub(
                r'(\s+)except\s*:\s*$',
                r'\1except (Exception, AttributeError, TypeError, ValueError):',
                content,
                flags=re.MULTILINE
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'Fixed {bare_count} bare exceptions in {filepath}')
            return bare_count
    except Exception as e:
        print(f'Error processing {filepath}: {e}')
    return 0

files_to_fix = ['pst_reader.py', 'smart_optimizer.py', 'dynamics_data.py', 'contact_creator.py']
total_fixed = 0
for file in files_to_fix:
    if os.path.exists(file):
        total_fixed += fix_file(file)

print(f'Total bare exceptions fixed: {total_fixed}') 