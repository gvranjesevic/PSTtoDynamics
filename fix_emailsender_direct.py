#!/usr/bin/env python3
"""Try different approaches to fix emailsender field"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 DIRECT EMAILSENDER FIX")
print("="*25)

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

# Get our test email
print(f"\n📧 Getting test email...")

test_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and createdon ge 2025-06-11T00:00:00Z&$select=activityid,subject,_emailsender_value&$top=1",
    headers=headers
)

if test_emails_response.status_code != 200:
    print(f"❌ Error: {test_emails_response.status_code}")
    exit(1)

test_emails = test_emails_response.json().get('value', [])
if not test_emails:
    print(f"❌ No test emails found")
    exit(1)

test_email = test_emails[0]
test_email_id = test_email['activityid']
current_emailsender = test_email.get('_emailsender_value')

print(f"📧 Test email: {test_email['subject'][:50]}")
print(f"📧 ID: {test_email_id}")
print(f"📧 Current _emailsender_value: {current_emailsender}")

# Try multiple approaches to set emailsender
approaches = [
    {
        'name': 'Direct _emailsender_value',
        'data': {'_emailsender_value': contact_id}
    },
    {
        'name': 'OData bind with @odata.bind',
        'data': {'emailsender@odata.bind': f'/contacts({contact_id})'}
    },
    {
        'name': 'emailsender as lookup value',
        'data': {'emailsender': f'/contacts({contact_id})'}
    },
    {
        'name': 'Combined sender + emailsender',
        'data': {
            'sender': 'service@ringcentral.com',
            'emailsender_contact@odata.bind': f'/contacts({contact_id})'
        }
    }
]

print(f"\n🧪 Trying {len(approaches)} different approaches...")

for i, approach in enumerate(approaches):
    print(f"\n🔬 Approach {i+1}: {approach['name']}")
    
    response = requests.patch(
        f"{crm_base_url}/emails({test_email_id})",
        json=approach['data'],
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Update successful!")
        
        # Check the result
        verify_response = requests.get(
            f"{crm_base_url}/emails({test_email_id})?$select=_emailsender_value,sender",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            new_emailsender = verify_data.get('_emailsender_value')
            sender = verify_data.get('sender')
            
            print(f"   📊 Result:")
            print(f"      _emailsender_value: {new_emailsender}")
            print(f"      sender: {sender}")
            
            if new_emailsender == contact_id:
                print(f"   🎉 SUCCESS! EmailSender now set to contact ID!")
                break
            else:
                print(f"   ⚠️  Still not set correctly")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        try:
            error_detail = response.json()
            print(f"      Error: {error_detail}")
        except:
            print(f"      Error: {response.text[:100]}")

# Final verification
print(f"\n🔍 Final verification...")
final_response = requests.get(
    f"{crm_base_url}/emails({test_email_id})?$select=_emailsender_value,sender,submittedby",
    headers=headers
)

if final_response.status_code == 200:
    final_data = final_response.json()
    final_emailsender = final_data.get('_emailsender_value')
    final_sender = final_data.get('sender')
    final_submittedby = final_data.get('submittedby')
    
    print(f"📊 Final state:")
    print(f"   _emailsender_value: {final_emailsender}")
    print(f"   sender: {final_sender}")
    print(f"   submittedby: {final_submittedby}")
    
    if final_emailsender == contact_id:
        print(f"\n🎉 SUCCESS! Email should now show 'Email from: service@ringcentral.com'")
    else:
        print(f"\n⚠️  EmailSender still not set correctly")
        print(f"   💡 The 'Email from:' may still show 'Closed'")
        print(f"   🔧 May need to recreate emails with proper initial settings")

print(f"\n📅 Please refresh timeline and check 'Email from:' display!")
print(f"   Expected: 'Email from: service@ringcentral.com'")
print(f"   Current issue: Shows 'Email from: Closed'") 