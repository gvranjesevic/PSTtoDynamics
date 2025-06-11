#!/usr/bin/env python3
"""Fix only status and direction fields to see if Email from display improves"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING STATUS/DIRECTION ONLY")
print("="*35)
print("Avoiding description updates due to draft status restriction")
print("="*35)

# Authenticate
print("\n🔐 Authenticating...")
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

# Get recent emails for testing
print(f"🔍 Getting test emails...")

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,statuscode,directioncode,actualstart&$orderby=actualstart desc&$top=5",
    headers=headers
)

emails = email_response.json().get('value', [])
print(f"📧 Found {len(emails)} test emails")

fixed_count = 0
error_count = 0

for i, email in enumerate(emails):
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:50]
    statuscode = email.get('statuscode')
    directioncode = email.get('directioncode')
    
    print(f"\n📧 Email {i+1}: {subject}")
    print(f"   Current: status={statuscode}, direction={directioncode}")
    
    # Only update status/direction, NOT description
    update_data = {}
    
    if statuscode != 4:
        update_data['statuscode'] = 4  # Received
    
    if directioncode != False:
        update_data['directioncode'] = False  # Incoming
    
    if update_data:
        print(f"   🔧 Updating: {update_data}")
        try:
            response = requests.patch(
                f"{crm_base_url}/emails({email_id})",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                fixed_count += 1
                print(f"   ✅ Successfully updated!")
            else:
                error_count += 1
                print(f"   ❌ Error: {response.status_code}")
                if error_count <= 2:
                    print(f"      Details: {response.text[:200]}")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Exception: {str(e)}")
    else:
        print(f"   ✅ Already correct")

print(f"\n🎯 RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count}")
print(f"   ❌ Errors: {error_count}")

if fixed_count > 0:
    print(f"\n🎉 STATUS/DIRECTION UPDATED!")
    print(f"   📅 Please refresh Dynamics 365 timeline")
    print(f"   🔍 Check if 'Email from:' display has improved")
    print(f"   💡 The emails should now show as properly received")
    
    # Ask if user wants to apply to all emails
    print(f"\n🤔 If this improved the 'Email from' display,")
    print(f"   we can apply this fix to ALL RingCentral emails")
else:
    print(f"\n❌ No status updates were possible")

print(f"\n💭 REGARDING FORMATTING:")
print("="*25)
print("🔒 Description formatting cannot be fixed due to Dynamics restriction")
print("📧 'Cannot update description unless email is in draft status'") 
print("✨ This is a system security feature to prevent email tampering")
print("🎯 Focus should be on 'Email from:' display improvement") 