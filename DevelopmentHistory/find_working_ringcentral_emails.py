#!/usr/bin/env python3
"""Find working RingCentral emails to understand Email from display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 FINDING WORKING RINGCENTRAL EMAILS")
print("="*38)

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

# Search for ALL RingCentral emails regardless of status
print(f"\n🔍 Searching for ALL RingCentral emails...")

all_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,sender,_emailsender_value,torecipients,submittedby,from,statuscode,statecode,createdon,actualstart&$orderby=actualstart desc&$top=10",
    headers=headers
)

if all_emails_response.status_code != 200:
    print(f"❌ Error getting emails: {all_emails_response.status_code}")
    exit(1)

all_emails = all_emails_response.json().get('value', [])
print(f"📧 Found {len(all_emails)} total RingCentral emails")

# Categorize by status
status_groups = {}
for email in all_emails:
    status = email.get('statuscode')
    state = email.get('statecode')
    key = f"state={state}, status={status}"
    
    if key not in status_groups:
        status_groups[key] = []
    status_groups[key].append(email)

print(f"\n📊 Email Status Groups:")
for status_key, emails in status_groups.items():
    print(f"   {status_key}: {len(emails)} emails")

# Focus on emails that are NOT our recent test imports
print(f"\n📋 DETAILED ANALYSIS OF NON-TEST EMAILS:")

original_emails = []
our_test_emails = []

for email in all_emails:
    created = email.get('createdon', '')
    if '2025-06-11' in created:  # Our test emails
        our_test_emails.append(email)
    else:  # Original emails
        original_emails.append(email)

print(f"   📧 Original emails: {len(original_emails)}")
print(f"   🧪 Our test emails: {len(our_test_emails)}")

# Show detailed info for original emails
if original_emails:
    print(f"\n📊 ORIGINAL EMAILS (should show proper 'Email from:'):")
    for i, email in enumerate(original_emails[:5]):
        subject = email.get('subject', 'No Subject')[:40]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        torecipients = email.get('torecipients')
        submittedby = email.get('submittedby')
        from_field = email.get('from')
        status = email.get('statuscode')
        state = email.get('statecode')
        created = email.get('createdon', '')[:19]
        actualstart = email.get('actualstart', '')[:19]
        
        print(f"\n   📧 ORIGINAL #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      ActualStart: {actualstart}")
        print(f"      Status: state={state}, status={status}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")
        print(f"      torecipients: {torecipients}")
        print(f"      submittedby: {submittedby}")
        print(f"      from: {from_field}")

# Show our test emails for comparison
if our_test_emails:
    print(f"\n🧪 OUR TEST EMAILS (showing 'Closed' in Email from):")
    for i, email in enumerate(our_test_emails[:3]):
        subject = email.get('subject', 'No Subject')[:40]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        torecipients = email.get('torecipients')
        submittedby = email.get('submittedby')
        from_field = email.get('from')
        status = email.get('statuscode')
        state = email.get('statecode')
        created = email.get('createdon', '')[:19]
        
        print(f"\n   🧪 TEST #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      Status: state={state}, status={status}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")
        print(f"      torecipients: {torecipients}")
        print(f"      submittedby: {submittedby}")
        print(f"      from: {from_field}")

# Try to copy exact fields from original to test
if original_emails and our_test_emails:
    print(f"\n🔧 COPYING FIELDS FROM WORKING EMAIL TO TEST EMAIL...")
    
    original = original_emails[0]
    test_email = our_test_emails[0]
    test_email_id = test_email['activityid']
    
    # Copy all relevant fields from original to test
    update_data = {}
    
    fields_to_copy = ['sender', 'submittedby', 'from']
    for field in fields_to_copy:
        original_value = original.get(field)
        test_value = test_email.get(field)
        
        if original_value and original_value != test_value:
            update_data[field] = original_value
            print(f"   📋 Will copy {field}: '{original_value}'")
    
    # Also ensure emailsender relationship is set
    if original.get('_emailsender_value'):
        update_data['emailsender_contact@odata.bind'] = f'/contacts({contact_id})'
        print(f"   📋 Will set emailsender_contact relationship")
    
    if update_data:
        print(f"\n   🔧 Applying {len(update_data)} field updates...")
        
        response = requests.patch(
            f"{crm_base_url}/emails({test_email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"   ✅ Successfully copied fields from working email!")
            
            # Verify the update
            verify_response = requests.get(
                f"{crm_base_url}/emails({test_email_id})?$select=sender,_emailsender_value,submittedby,from",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"   📊 Updated test email now has:")
                print(f"      sender: {verify_data.get('sender')}")
                print(f"      _emailsender_value: {verify_data.get('_emailsender_value')}")
                print(f"      submittedby: {verify_data.get('submittedby')}")
                print(f"      from: {verify_data.get('from')}")
        else:
            print(f"   ❌ Update failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"      Error: {error_detail}")
            except:
                print(f"      Error: {response.text[:200]}")
    else:
        print(f"   💡 No field differences found to copy")

print(f"\n💡 KEY FINDINGS:")
print(f"   📧 Original emails: {len(original_emails)} found")
print(f"   🧪 Test emails: {len(our_test_emails)} found")
print(f"   🔧 Attempted to copy working email pattern")
print(f"\n📅 Please refresh timeline and check 'Email from:' display!")
print(f"   Expected: 'Email from: service@ringcentral.com'")
print(f"   Current:  'Email from: Closed'") 