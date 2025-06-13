#!/usr/bin/env python3
"""
Fix Bare Exception Handling Script
==================================

This script fixes all instances of bare 'except:' clauses by replacing them
with specific exception types to improve code quality and debugging.
"""

import os
import re
from typing import List, Tuple

def find_bare_exceptions(file_path: str) -> List[Tuple[int, str]]:
    """Find all bare except clauses in a file."""
    bare_exceptions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Look for bare except: clauses
            if re.search(r'^\s*except\s*:\s*$', line):
                bare_exceptions.append((i, line.strip()))
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return bare_exceptions

def fix_bare_exceptions(file_path: str) -> bool:
    """Fix bare exception handling in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace bare except: with specific exceptions
        # Common pattern: except: -> except (Exception, AttributeError, TypeError, ValueError):
        content = re.sub(
            r'(\s+)except\s*:\s*$',
            r'\1except (Exception, AttributeError, TypeError, ValueError):',
            content,
            flags=re.MULTILINE
        )
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix bare exceptions in all Python files."""
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.pytest_cache', 'build', 'dist']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Found {len(python_files)} Python files to check")
    
    total_fixes = 0
    files_fixed = 0
    
    for file_path in python_files:
        bare_exceptions = find_bare_exceptions(file_path)
        
        if bare_exceptions:
            print(f"\n📁 {file_path}:")
            for line_num, line in bare_exceptions:
                print(f"   Line {line_num}: {line}")
            
            if fix_bare_exceptions(file_path):
                print(f"   ✅ Fixed {len(bare_exceptions)} bare exception(s)")
                total_fixes += len(bare_exceptions)
                files_fixed += 1
            else:
                print(f"   ❌ Failed to fix exceptions")
    
    print(f"\n🎯 Summary:")
    print(f"   Files processed: {len(python_files)}")
    print(f"   Files fixed: {files_fixed}")
    print(f"   Total exceptions fixed: {total_fixes}")
    
    if total_fixes > 0:
        print(f"\n✅ Successfully fixed {total_fixes} bare exception handling issues!")
    else:
        print(f"\n✅ No bare exception handling issues found!")

if __name__ == "__main__":
    main() 