#!/usr/bin/env python3
"""Automated fix for ALL RingCentral emails - both formatting and status"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🚀 AUTO-FIXING ALL RINGCENTRAL EMAILS")
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

# Get all emails in batches
print(f"🔍 Getting emails in batches...")
all_emails = []
skip = 0
batch_size = 100

while True:
    batch_response = requests.get(
        f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,description,safedescription,statuscode,directioncode&$skip={skip}&$top={batch_size}",
        headers=headers
    )
    
    if batch_response.status_code != 200:
        print(f"❌ Error getting batch: {batch_response.status_code}")
        break
    
    batch_emails = batch_response.json().get('value', [])
    if not batch_emails:
        break
    
    all_emails.extend(batch_emails)
    skip += batch_size
    print(f"   📧 Retrieved {len(all_emails)} emails so far...")

print(f"📧 Total emails found: {len(all_emails)}")

# Process and fix emails
print(f"🔧 Processing emails for issues...")

fixed_format = 0
fixed_status = 0
errors = 0

for i, email in enumerate(all_emails):
    email_id = email['activityid']
    update_data = {}
    
    # Check and fix formatting
    description = email.get('description', '')
    safedescription = email.get('safedescription', '')
    
    if '________________________________' in description:
        update_data['description'] = description.replace('________________________________', '<br><br>')
    
    if '________________________________' in safedescription:
        update_data['safedescription'] = safedescription.replace('________________________________', '<br><br>')
    
    # Check and fix status/direction
    statuscode = email.get('statuscode')
    directioncode = email.get('directioncode')
    
    if statuscode != 4:  # Should be 4 = Received
        update_data['statuscode'] = 4
    
    if directioncode != False:  # Should be False = Incoming
        update_data['directioncode'] = False
    
    # Apply updates if needed
    if update_data:
        try:
            response = requests.patch(
                f"{crm_base_url}/emails({email_id})",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                if 'description' in update_data or 'safedescription' in update_data:
                    fixed_format += 1
                if 'statuscode' in update_data or 'directioncode' in update_data:
                    fixed_status += 1
                    
                if (i + 1) % 50 == 0:
                    print(f"   ✅ Processed {i + 1}/{len(all_emails)} emails...")
            else:
                errors += 1
                if errors <= 5:
                    print(f"   ❌ Error on email {i+1}: {response.status_code}")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"   ❌ Exception on email {i+1}: {str(e)}")

print(f"\n🎯 FINAL RESULTS:")
print("="*20)
print(f"✅ Emails processed: {len(all_emails)}")
print(f"🔧 Formatting fixes applied: {fixed_format}")
print(f"📮 Status/direction fixes applied: {fixed_status}")
print(f"❌ Errors: {errors}")

if fixed_format > 0 or fixed_status > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   🔧 Underscores replaced with HTML line breaks")
    print(f"   📮 Email status/direction corrected for proper display")
    print(f"   📅 Refresh Dynamics 365 to see improvements!")
    print(f"\n   💡 This should fix:")
    print(f"      - Underscore formatting issues")
    print(f"      - Email from: display problems")
    print(f"      - All RingCentral emails should look correct now!")
else:
    print(f"\n✅ All emails were already correctly formatted!")

print(f"\n📧 Please check your timeline - both issues should be resolved!") 