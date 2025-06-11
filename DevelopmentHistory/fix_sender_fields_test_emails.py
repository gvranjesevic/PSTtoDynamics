#!/usr/bin/env python3
"""Fix sender fields for the 3 test emails to get proper 'Email from:' display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING SENDER FIELDS FOR TEST EMAILS")
print("="*40)

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

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Find the 3 test emails we just created (most recent ones with proper status)
print(f"\n🔍 Finding the 3 test emails we just created...")

test_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and statecode eq 1 and statuscode eq 4&$select=activityid,subject,sender,_emailsender_value,torecipients,createdon&$orderby=createdon desc&$top=3",
    headers=headers
)

if test_emails_response.status_code != 200:
    print(f"❌ Error getting test emails: {test_emails_response.status_code}")
    exit(1)

test_emails = test_emails_response.json().get('value', [])
print(f"📧 Found {len(test_emails)} test emails with correct status")

if len(test_emails) == 0:
    print("❌ No test emails found with completed status!")
    exit(1)

# Show current state
print(f"\n📊 Current state of test emails:")
for i, email in enumerate(test_emails):
    subject = email.get('subject', 'No Subject')[:50]
    sender = email.get('sender') or 'None'
    emailsender = email.get('_emailsender_value') or 'None'
    torecipients = email.get('torecipients') or 'None'
    created = email.get('createdon', '')[:19]
    
    print(f"   {i+1}. {subject}")
    print(f"      Created: {created}")
    print(f"      Sender: {sender}")
    print(f"      EmailSender: {emailsender}")
    print(f"      ToRecipients: {torecipients}")

# Fix the sender fields
print(f"\n🔧 Fixing sender fields for {len(test_emails)} test emails...")

fixed_count = 0
error_count = 0

for i, email in enumerate(test_emails):
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    print(f"\n📧 Fixing email {i+1}/{len(test_emails)}: {subject}...")
    
    try:
        # Update sender fields to match what working RingCentral emails have
        update_data = {
            'sender': 'service@ringcentral.com',
            'emailsender_contact@odata.bind': f'/contacts({contact_id})',
            'torecipients': 'gvranjesevic@dynamique.com;'
        }
        
        response = requests.patch(
            f"{crm_base_url}/emails({email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            fixed_count += 1
            print(f"   ✅ Sender fields updated successfully!")
            
            # Verify the update
            verify_response = requests.get(
                f"{crm_base_url}/emails({email_id})?$select=sender,_emailsender_value,torecipients",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                new_sender = verify_data.get('sender')
                new_emailsender = verify_data.get('_emailsender_value')
                new_torecipients = verify_data.get('torecipients')
                
                print(f"   📊 Updated fields:")
                print(f"      Sender: {new_sender}")
                print(f"      EmailSender: {new_emailsender}")
                print(f"      ToRecipients: {new_torecipients}")
                
        else:
            error_count += 1
            print(f"   ❌ Error updating: {response.status_code}")
            if error_count <= 2:
                try:
                    error_detail = response.json()
                    print(f"      Details: {error_detail}")
                except:
                    print(f"      Details: {response.text[:200]}")
                    
    except Exception as e:
        error_count += 1
        print(f"   ❌ Exception: {str(e)}")

print(f"\n🎯 SENDER FIELD FIX RESULTS:")
print("="*30)
print(f"✅ Successfully fixed: {fixed_count}")
print(f"❌ Errors: {error_count}")

if fixed_count > 0:
    print(f"\n🎉 SENDER FIELDS UPDATED!")
    print(f"   📧 {fixed_count} test emails updated")
    print(f"   📅 Please refresh Dynamics 365 timeline")
    print(f"   🔍 Check if 'Email from:' now shows:")
    print(f"      ✅ 'Email from: service@ringcentral.com'")
    print(f"      ✅ Instead of 'Email from: Closed'")
    print(f"\n   💡 If this works, we have the complete solution:")
    print(f"      1. ✅ Draft-first strategy for formatting")
    print(f"      2. ✅ Proper status codes for 'Closed' status")
    print(f"      3. ✅ Sender field updates for proper display")
    print(f"      🚀 Ready for full 71 April emails import!")
else:
    print(f"\n❌ No sender fields were updated")
    print(f"   💡 Check the errors above for troubleshooting")

print(f"\n📧 Please check the timeline and confirm the fix!") 