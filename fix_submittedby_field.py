#!/usr/bin/env python3
"""Fix the submittedby field that controls Email from display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING SUBMITTEDBY FIELD FOR EMAIL FROM DISPLAY")
print("="*55)

# Authenticate
print("🔐 Authenticating...")
app = msal.PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_domain}"
)

result = app.acquire_token_by_username_password(
    username=username,
    password=password,
    scopes=["https://dynglobal.crm.dynamics.com/.default"]
)

if "access_token" not in result:
    print(f"❌ Auth failed: {result}")
    exit(1)

access_token = result["access_token"]
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}

print("✅ Authentication successful!")

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get April 2025 emails to fix
print("\n🔍 Getting April 2025 emails to fix...")
april_start = "2025-04-01T00:00:00Z"
april_end = "2025-04-30T23:59:59Z"

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge {april_start} and actualstart le {april_end}&$select=activityid,subject,submittedby&$orderby=actualstart asc",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    exit(1)

emails_to_fix = email_response.json().get('value', [])
print(f"📧 Found {len(emails_to_fix)} April emails")

if len(emails_to_fix) == 0:
    print("✅ No emails found!")
    exit(0)

# Check which ones need the submittedby field fixed
emails_needing_fix = []

for email in emails_to_fix:
    current_submittedby = email.get('submittedby')
    if not current_submittedby or 'service@ringcentral.com' not in current_submittedby:
        emails_needing_fix.append(email)

print(f"📧 Emails needing submittedby fix: {len(emails_needing_fix)}")

if len(emails_needing_fix) == 0:
    print("✅ All emails already have correct submittedby field!")
    exit(0)

# Show samples
print(f"\n📝 Sample emails needing submittedby fix:")
for i, email in enumerate(emails_needing_fix[:3]):
    subject = email.get('subject', 'No Subject')[:50]
    current_submittedby = email.get('submittedby', 'None')
    print(f"   {i+1}. {subject}")
    print(f"      Current submittedby: {current_submittedby}")

# Ask for confirmation
confirmation = input(f"\n🤔 Fix submittedby field for {len(emails_needing_fix)} emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Fix cancelled")
    exit(0)

# Fix the emails
print(f"\n🔧 Starting submittedby field fixes...")
fixed_count = 0
error_count = 0

for i, email in enumerate(emails_needing_fix):
    email_id = email['activityid']
    
    try:
        print(f"🔧 Fixing email {i+1}/{len(emails_needing_fix)}...")
        
        # Set the submittedby field to match the original format
        update_data = {
            'submittedby': '"RingCentral" service@ringcentral.com'
        }
        
        response = requests.patch(
            f"{crm_base_url}/emails({email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            fixed_count += 1
            print(f"   ✅ Set submittedby: \"RingCentral\" service@ringcentral.com")
            if i % 10 == 0 and i > 0:
                print(f"   📊 Fixed {fixed_count} emails so far...")
        else:
            error_count += 1
            if error_count <= 3:
                print(f"   ❌ Error fixing email {i+1}: {response.status_code}")
                if error_count == 1:
                    print(f"       Details: {response.text[:200]}")
        
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"   ❌ Exception fixing email {i+1}: {str(e)}")

print(f"\n🎯 SUBMITTEDBY FIX RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📧 {fixed_count} emails now have proper submittedby field")
    print(f"   📅 Refresh Dynamics 365 to see the changes:")
    print(f"   📧 'Email from: RingCentral' should now appear!")
    print(f"   🔍 The submittedby field controls the 'Email from:' display")
    print(f"\n   🎯 Your emails should now show 'Email from: RingCentral' instead of 'Email from: Closed'!")
else:
    print(f"\n⚠️  No emails were updated.")
    print(f"   💡 There may have been API restrictions on updating the submittedby field.") 