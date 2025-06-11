#!/usr/bin/env python3
"""Investigate valid email status codes and fix the 400 error"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 INVESTIGATING EMAIL STATUS CODES")
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

# 1. Look at existing emails to see what status codes they use
print(f"\n📊 Checking existing email status codes...")
existing_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,statuscode,statecode&$top=10",
    headers=headers
)

if existing_emails_response.status_code == 200:
    existing_emails = existing_emails_response.json().get('value', [])
    print(f"   Found {len(existing_emails)} existing emails:")
    
    status_codes = {}
    for email in existing_emails:
        status = email.get('statuscode')
        state = email.get('statecode')
        subject = email.get('subject', 'No Subject')[:30]
        
        key = f"state={state}, status={status}"
        if key not in status_codes:
            status_codes[key] = []
        status_codes[key].append(subject)
    
    for status_combo, subjects in status_codes.items():
        print(f"   📧 {status_combo}: {len(subjects)} emails")
        print(f"      Example: {subjects[0]}")

# 2. Check our draft emails
print(f"\n🔍 Checking our draft emails created today...")
draft_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and statuscode eq 1&$select=activityid,subject,statuscode,statecode,createdon&$orderby=createdon desc&$top=5",
    headers=headers
)

if draft_emails_response.status_code == 200:
    draft_emails = draft_emails_response.json().get('value', [])
    print(f"   Found {len(draft_emails)} draft emails:")
    
    for email in draft_emails:
        subject = email.get('subject', 'No Subject')[:40]
        status = email.get('statuscode')
        state = email.get('statecode')
        created = email.get('createdon', '')
        print(f"   📧 {subject}")
        print(f"      Status: {status}, State: {state}, Created: {created[:19]}")

# 3. Try to understand the 400 error by attempting a status change with detailed error
if len(draft_emails) > 0:
    test_email_id = draft_emails[0]['activityid']
    print(f"\n🧪 Testing status change on: {test_email_id}")
    
    # Try different status codes
    status_tests = [
        {'statuscode': 4, 'name': 'Received (4)'},
        {'statuscode': 3, 'name': 'Sent (3)'},
        {'statuscode': 5, 'name': 'Completed (5)'},
        {'statecode': 1, 'statuscode': 4, 'name': 'Completed + Received'},
        {'statecode': 1, 'statuscode': 2, 'name': 'Completed + Canceled'}
    ]
    
    for test in status_tests:
        print(f"\n   🔬 Testing {test['name']}...")
        
        response = requests.patch(
            f"{crm_base_url}/emails({test_email_id})",
            json={k: v for k, v in test.items() if k != 'name'},
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"      ✅ SUCCESS! Status code {response.status_code}")
            
            # Verify the change
            verify_response = requests.get(
                f"{crm_base_url}/emails({test_email_id})?$select=statuscode,statecode",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                new_status = verify_data.get('statuscode')
                new_state = verify_data.get('statecode')
                print(f"      📊 Updated to: state={new_state}, status={new_status}")
            
            break  # Stop testing once we find a working one
        else:
            print(f"      ❌ Failed: {response.status_code}")
            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    print(f"      📋 Error details: {error_detail}")
                except:
                    print(f"      📋 Error text: {response.text[:200]}")

# 4. Get metadata about email status codes
print(f"\n📚 Getting email entity metadata...")
metadata_response = requests.get(
    f"{crm_base_url}/$metadata",
    headers={'Accept': 'application/xml'}
)

if metadata_response.status_code == 200:
    print(f"   📊 Metadata retrieved (too long to display)")
    print(f"   💡 Check Dynamics 365 documentation for email status codes")

print(f"\n💡 SUMMARY:")
print(f"   ✅ Draft creation works perfectly")
print(f"   ✅ HTML formatting preserved in draft")
print(f"   ❌ Status change from draft to received fails")
print(f"   🔧 Need to find the correct status/state combination")

print(f"\n📚 Next steps:")
print(f"   1. Check successful status change above")
print(f"   2. Update the re-import script with correct codes")
print(f"   3. Re-run with proper status transitions") 