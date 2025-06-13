import os
import re

def fix_logging_in_file(filepath):
    """Replace print statements with proper logging."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count print statements
        print_count = len(re.findall(r'print\s*\(', content))
        
        if print_count > 0:
            # Add logging import if not present
            if 'import logging' not in content:
                # Find the first import statement and add logging import after it
                import_match = re.search(r'^(import .+)$', content, re.MULTILINE)
                if import_match:
                    content = content.replace(import_match.group(1), 
                                            import_match.group(1) + '\nimport logging')
                else:
                    # Add at the beginning if no imports found
                    content = 'import logging\n' + content
            
            # Add logger initialization if not present
            if 'logger = logging.getLogger(__name__)' not in content:
                # Add after imports
                lines = content.split('\n')
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_idx = i + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                lines.insert(insert_idx, '\nlogger = logging.getLogger(__name__)')
                content = '\n'.join(lines)
            
            # Replace common print patterns with logging
            # Success messages (✅)
            content = re.sub(r'print\s*\(\s*f?"✅([^"]*)"', r'logger.info("✅\1"', content)
            content = re.sub(r'print\s*\(\s*"✅([^"]*)"', r'logger.info("✅\1"', content)
            
            # Error messages (❌)
            content = re.sub(r'print\s*\(\s*f?"❌([^"]*)"', r'logger.error("❌\1"', content)
            content = re.sub(r'print\s*\(\s*"❌([^"]*)"', r'logger.error("❌\1"', content)
            
            # Warning messages (⚠️)
            content = re.sub(r'print\s*\(\s*f?"⚠️([^"]*)"', r'logger.warning("⚠️\1"', content)
            content = re.sub(r'print\s*\(\s*"⚠️([^"]*)"', r'logger.warning("⚠️\1"', content)
            
            # Info messages (📊, 📧, 📁, etc.)
            info_emojis = ['📊', '📧', '📁', '📂', '🔍', '📈', '👥', '🚀', '🔐', '📍']
            for emoji in info_emojis:
                content = re.sub(rf'print\s*\(\s*f?"{emoji}([^"]*)"', rf'logger.info("{emoji}\1"', content)
                content = re.sub(rf'print\s*\(\s*"{emoji}([^"]*)"', rf'logger.info("{emoji}\1"', content)
            
            # Generic print statements to debug level
            content = re.sub(r'print\s*\(\s*f?"([^"]*)"', r'logger.debug("\1"', content)
            content = re.sub(r'print\s*\(\s*"([^"]*)"', r'logger.debug("\1"', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'Fixed {print_count} print statements in {filepath}')
            return print_count
    except Exception as e:
        print(f'Error processing {filepath}: {e}')
    return 0

# Process key files with many print statements
files_to_fix = [
    'pst_reader.py',
    'smart_optimizer.py',
    'predictive_analytics.py',
    'phase4_integration.py',
    'Phase3_Analytics/timeline_analyzer.py',
    'Phase3_Analytics/sender_analytics.py'
]

total_fixed = 0
for file in files_to_fix:
    if os.path.exists(file):
        total_fixed += fix_logging_in_file(file)

print(f'Total print statements converted to logging: {total_fixed}') 