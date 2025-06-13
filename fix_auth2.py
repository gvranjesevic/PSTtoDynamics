# Remove deprecated get_access_token function with proper encoding
with open('auth.py', 'r', encoding='utf-8') as f: content = f.read()
import re
# Remove everything from @handle_exception get_access_token onwards
pattern = r'@handle_exception\s*\ndef get_access_token.*'
content = re.sub(pattern, '', content, flags=re.DOTALL)
with open('auth.py', 'w', encoding='utf-8') as f: f.write(content)
print('✅ Removed deprecated get_access_token function from auth.py')
