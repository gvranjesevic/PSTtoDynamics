#!/usr/bin/env python3
"""Simple fix for recent RingCentral emails to test the approach"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING RECENT RINGCENTRAL EMAILS")
print("="*40)

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

# Get contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get recent emails (last 20)
print(f"🔍 Getting recent emails...")

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,description,safedescription,statuscode,directioncode,actualstart&$orderby=actualstart desc&$top=20",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    print(f"   Details: {email_response.text}")
    exit(1)

emails = email_response.json().get('value', [])
print(f"📧 Found {len(emails)} recent emails")

if len(emails) == 0:
    print("❌ No emails found!")
    exit(1)

# Analyze and fix
print(f"\n🔧 Analyzing and fixing emails...")

fixed_count = 0
error_count = 0

for i, email in enumerate(emails):
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:50]
    date = email.get('actualstart', 'No Date')
    
    print(f"\n📧 Email {i+1}: {subject}")
    print(f"   Date: {date}")
    
    update_data = {}
    
    # Check formatting
    description = email.get('description', '')
    safedescription = email.get('safedescription', '')
    
    if '________________________________' in description:
        print(f"   🔧 Fixing description formatting...")
        update_data['description'] = description.replace('________________________________', '<br><br>')
    
    if '________________________________' in safedescription:
        print(f"   🔧 Fixing safedescription formatting...")
        update_data['safedescription'] = safedescription.replace('________________________________', '<br><br>')
    
    # Check status/direction
    statuscode = email.get('statuscode')
    directioncode = email.get('directioncode')
    
    print(f"   Current status: {statuscode}, direction: {directioncode}")
    
    if statuscode != 4:
        print(f"   🔧 Fixing statuscode: {statuscode} → 4")
        update_data['statuscode'] = 4
    
    if directioncode != False:
        print(f"   🔧 Fixing directioncode: {directioncode} → False")
        update_data['directioncode'] = False
    
    # Apply fixes
    if update_data:
        print(f"   📝 Applying {len(update_data)} fixes...")
        try:
            response = requests.patch(
                f"{crm_base_url}/emails({email_id})",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                fixed_count += 1
                print(f"   ✅ Successfully fixed!")
            else:
                error_count += 1
                print(f"   ❌ Error: {response.status_code}")
                if error_count <= 2:
                    print(f"      Details: {response.text[:200]}")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Exception: {str(e)}")
    else:
        print(f"   ✅ No fixes needed")

print(f"\n🎯 RESULTS:")
print(f"   📧 Emails processed: {len(emails)}")
print(f"   ✅ Successfully fixed: {fixed_count}")
print(f"   ❌ Errors: {error_count}")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📅 Refresh Dynamics 365 to see the changes!")
    print(f"   🔍 Check if the recent emails now show:")
    print(f"      - Proper line breaks (no underscores)")
    print(f"      - Better 'Email from:' display")
else:
    print(f"\n✅ All recent emails were already correctly formatted!")

print(f"\n💡 If this works, we can extend it to all emails.") 