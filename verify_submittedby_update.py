#!/usr/bin/env python3
"""Verify submittedby updates and investigate other fields that might control Email from display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 VERIFYING SUBMITTEDBY UPDATES & INVESTIGATING EMAIL FROM DISPLAY")
print("="*70)

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

# Get both RingCentral contacts
print("\n🔍 Getting RingCentral contacts...")
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')&$select=contactid,fullname,emailaddress1&$orderby=fullname", 
    headers=headers
)

contacts = contact_response.json()['value']
service_contact = None
notify_contact = None

for contact in contacts:
    if contact['emailaddress1'] == 'service@ringcentral.com':
        service_contact = contact
    elif contact['emailaddress1'] == 'notify@ringcentral.com':
        notify_contact = contact

print(f"✅ Service contact: {service_contact['fullname']} ({service_contact['contactid']})")
print(f"✅ Notify contact: {notify_contact['fullname']} ({notify_contact['contactid']})")

# Get a sample updated April email to verify
print("\n🔍 Getting updated April email to verify...")
april_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {service_contact['contactid']} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$top=1&$select=activityid,subject,submittedby,directioncode,sender,_emailsender_value",
    headers=headers
)

april_email = april_email_response.json()['value'][0]
print(f"📧 April email: {april_email.get('subject', 'No Subject')[:50]}...")

# Get a working original email for comparison
print("🔍 Getting original working email...")
original_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact['contactid']}&$top=1&$select=activityid,subject,submittedby,directioncode,sender,_emailsender_value",
    headers=headers
)

original_email = original_email_response.json()['value'][0]
print(f"📧 Original email: {original_email.get('subject', 'No Subject')[:50]}...")

# Compare key fields
print(f"\n📊 FIELD COMPARISON:")
print("="*30)

fields_to_check = ['submittedby', 'directioncode', 'sender', '_emailsender_value']

for field in fields_to_check:
    april_val = april_email.get(field, 'None')
    original_val = original_email.get(field, 'None')
    
    status = "✅ MATCH" if april_val == original_val else "❌ DIFFERENT"
    
    print(f"\n🔍 {field}:")
    print(f"   April email:  {april_val}")
    print(f"   Original:     {original_val}")
    print(f"   Status:       {status}")

# Check if directioncode is the issue
if april_email.get('directioncode') != original_email.get('directioncode'):
    print(f"\n💡 POTENTIAL ISSUE FOUND:")
    print(f"   The directioncode field is different!")
    print(f"   April: {april_email.get('directioncode')} | Original: {original_email.get('directioncode')}")
    print(f"   This might be controlling the Email from display.")
    
    # Check if we can update directioncode
    confirmation = input(f"\n🤔 Try fixing directioncode field? (yes/no): ").strip().lower()
    if confirmation in ['yes', 'y']:
        print(f"\n🔧 Updating directioncode for sample email...")
        
        update_data = {
            'directioncode': original_email.get('directioncode')
        }
        
        response = requests.patch(
            f"{crm_base_url}/emails({april_email['activityid']})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ Successfully updated directioncode to: {original_email.get('directioncode')}")
            print(f"📅 Please refresh Dynamics and check if 'Email from' now shows correctly!")
            print(f"💡 If this works, we can update all 71 emails.")
        else:
            print(f"❌ Error updating directioncode: {response.status_code}")
            print(f"   Details: {response.text[:200]}")

# Also check if submittedby was actually updated
print(f"\n🔍 SUBMITTEDBY VERIFICATION:")
if april_email.get('submittedby') and 'service@ringcentral.com' in str(april_email.get('submittedby')):
    print(f"✅ submittedby field was successfully updated!")
    print(f"   Value: {april_email.get('submittedby')}")
else:
    print(f"❌ submittedby field update may have failed!")
    print(f"   Current value: {april_email.get('submittedby')}")

print(f"\n💡 INVESTIGATION SUMMARY:")
print(f"   📧 Total differences found: {len([f for f in fields_to_check if april_email.get(f) != original_email.get(f)])}")
print(f"   🔍 The field controlling 'Email from:' display might be:")
print(f"      - directioncode (if different)")
print(f"      - A combination of fields")
print(f"      - A calculated field based on other values")
print(f"      - System caching that needs time to refresh") 