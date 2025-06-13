import re
with open('config.py', 'r') as f: content = f.read()
content = content.replace("USERNAME = os.getenv(\"DYNAMICS_USERNAME\", \"gvranjesevic@dynamique.com\")", "USERNAME = os.getenv(\"DYNAMICS_USERNAME\")")
content = content.replace("TENANT_DOMAIN = os.getenv(\"DYNAMICS_TENANT_DOMAIN\", \"dynamique.com\")", "TENANT_DOMAIN = os.getenv(\"DYNAMICS_TENANT_DOMAIN\")")
content = content.replace("CLIENT_ID = os.getenv(\"DYNAMICS_CLIENT_ID\", \"51f81489-12ee-4a9e-aaae-a2591f45987d\")", "CLIENT_ID = os.getenv(\"DYNAMICS_CLIENT_ID\")")
content = content.replace("SYSTEM_USER_ID = os.getenv(\"SYSTEM_USER_ID\", \"5794f83f-9b37-f011-8c4e-000d3a9c4367\")", "SYSTEM_USER_ID = os.getenv(\"SYSTEM_USER_ID\")")
with open('config.py', 'w') as f: f.write(content)
print('✅ Fixed config.py hardcoded defaults')
