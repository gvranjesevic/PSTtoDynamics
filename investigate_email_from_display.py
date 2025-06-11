#!/usr/bin/env python3
"""Investigate what field controls the 'Email from:' display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 INVESTIGATING 'EMAIL FROM:' DISPLAY")
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

# 1. Get working RingCentral emails (original ones that show properly)
print(f"\n📊 WORKING EMAILS (original RingCentral emails)...")
working_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and statecode eq 1 and statuscode eq 3&$select=activityid,subject,sender,_emailsender_value,emailsender,torecipients,submittedby,senton,createdon,from&$orderby=actualstart desc&$top=3",
    headers=headers
)

working_emails = []
if working_emails_response.status_code == 200:
    working_emails = working_emails_response.json().get('value', [])
    print(f"   Found {len(working_emails)} working emails")
    
    for i, email in enumerate(working_emails):
        subject = email.get('subject', 'No Subject')[:40]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        torecipients = email.get('torecipients')
        submittedby = email.get('submittedby')
        senton = email.get('senton')
        created = email.get('createdon', '')[:19]
        from_field = email.get('from')
        
        print(f"\n   📧 WORKING #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")
        print(f"      torecipients: {torecipients}")
        print(f"      submittedby: {submittedby}")
        print(f"      senton: {senton}")
        print(f"      from: {from_field}")

# 2. Get our test emails
print(f"\n📧 OUR TEST EMAILS (showing 'Closed' in Email from)...")
test_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and statecode eq 1 and statuscode eq 4&$select=activityid,subject,sender,_emailsender_value,emailsender,torecipients,submittedby,senton,createdon,from&$orderby=createdon desc&$top=3",
    headers=headers
)

test_emails = []
if test_emails_response.status_code == 200:
    test_emails = test_emails_response.json().get('value', [])
    print(f"   Found {len(test_emails)} test emails")
    
    for i, email in enumerate(test_emails):
        subject = email.get('subject', 'No Subject')[:40]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        torecipients = email.get('torecipients')
        submittedby = email.get('submittedby')
        senton = email.get('senton')
        created = email.get('createdon', '')[:19]
        from_field = email.get('from')
        
        print(f"\n   📧 TEST #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")
        print(f"      torecipients: {torecipients}")
        print(f"      submittedby: {submittedby}")
        print(f"      senton: {senton}")
        print(f"      from: {from_field}")

# 3. Compare the differences
print(f"\n🔍 COMPARING DIFFERENCES...")
if working_emails and test_emails:
    working = working_emails[0]
    test = test_emails[0]
    
    fields_to_compare = ['sender', '_emailsender_value', 'torecipients', 'submittedby', 'senton', 'from']
    
    print(f"\n   📊 Field Comparison:")
    print(f"      Field                | Working Email        | Test Email          | Match")
    print(f"      ---------------------|---------------------|---------------------|------")
    
    for field in fields_to_compare:
        working_val = working.get(field, 'None')
        test_val = test.get(field, 'None')
        match = "✅" if working_val == test_val else "❌"
        
        working_display = str(working_val)[:18] if working_val else 'None'
        test_display = str(test_val)[:18] if test_val else 'None'
        
        print(f"      {field:<20} | {working_display:<19} | {test_display:<19} | {match}")

# 4. Try to fix the key missing fields
if test_emails and working_emails:
    print(f"\n🔧 ATTEMPTING TO FIX MISSING FIELDS...")
    
    test_email_id = test_emails[0]['activityid']
    working_email = working_emails[0]
    
    # Build update based on what's different
    update_data = {}
    
    # Check what fields the working email has that our test doesn't
    if working_email.get('_emailsender_value') and not test_emails[0].get('_emailsender_value'):
        print(f"   📋 Working email has emailsender_value: {working_email.get('_emailsender_value')}")
        # This should be the contact ID
        update_data['emailsender_contact@odata.bind'] = f'/contacts({contact_id})'
    
    if working_email.get('submittedby') and not test_emails[0].get('submittedby'):
        print(f"   📋 Working email has submittedby: {working_email.get('submittedby')}")
        update_data['submittedby'] = working_email.get('submittedby')
    
    if working_email.get('from') and not test_emails[0].get('from'):
        print(f"   📋 Working email has from: {working_email.get('from')}")
        update_data['from'] = working_email.get('from')
    
    if update_data:
        print(f"\n   🔧 Applying missing fields to test email...")
        
        response = requests.patch(
            f"{crm_base_url}/emails({test_email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"   ✅ Updated missing fields successfully!")
            
            # Verify
            verify_response = requests.get(
                f"{crm_base_url}/emails({test_email_id})?$select=sender,_emailsender_value,submittedby,from",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"   📊 After update:")
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
        print(f"   💡 No obvious missing fields found")

print(f"\n💡 SUMMARY:")
print(f"   📊 Compared working vs test emails")
print(f"   🔍 Identified field differences")
print(f"   🔧 Applied missing fields if found")
print(f"\n📅 Please refresh timeline and check if 'Email from:' is now fixed!")
print(f"   Expected: 'Email from: service@ringcentral.com'")
print(f"   Current:  'Email from: Closed'") 