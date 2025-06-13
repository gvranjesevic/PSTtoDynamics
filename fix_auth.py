# Remove deprecated get_access_token function
with open('auth.py', 'r') as f: lines = f.readlines()
# Find the start of the deprecated function
start_idx = None
for i, line in enumerate(lines):
    if 'def get_access_token(' in line:
        start_idx = i
        break
if start_idx is not None:
    lines = lines[:start_idx]
with open('auth.py', 'w') as f: f.writelines(lines)
print('✅ Removed deprecated get_access_token function from auth.py')
