# Refactor sync_engine.py to remove duplicate data access logic
with open('sync/sync_engine.py', 'r', encoding='utf-8') as f: content = f.read()
import re
# Remove the PSTDataSource and DynamicsDataSource classes
pattern = r'# Placeholder data source classes.*'
content = re.sub(pattern, '', content, flags=re.DOTALL)
with open('sync/sync_engine.py', 'w', encoding='utf-8') as f: f.write(content)
print('✅ Refactored sync_engine.py to remove duplicate data access logic')
