#!/usr/bin/env python3
"""Find existing working RingCentral emails and copy their exact pattern"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 FINDING WORKING RINGCENTRAL EMAIL PATTERN")
print("="*43)

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

# Search for emails NOT created today (these would be original working ones)
print(f"\n🔍 Searching for original (non-test) RingCentral emails...")

# Look for emails created before today
original_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and createdon lt 2025-06-11T00:00:00Z&$select=activityid,subject,sender,_emailsender_value,torecipients,submittedby,from,statuscode,statecode,createdon&$orderby=createdon desc&$top=10",
    headers=headers
)

if original_emails_response.status_code != 200:
    print(f"❌ Error getting original emails: {original_emails_response.status_code}")
    exit(1)

original_emails = original_emails_response.json().get('value', [])
print(f"📧 Found {len(original_emails)} original emails")

working_email = None
if original_emails:
    print(f"\n📊 ORIGINAL EMAILS (should show proper 'Email from:'):")
    for i, email in enumerate(original_emails):
        subject = email.get('subject', 'No Subject')[:50]
        emailsender = email.get('_emailsender_value')
        sender = email.get('sender')
        status = email.get('statuscode')
        state = email.get('statecode')
        created = email.get('createdon', '')[:19]
        
        print(f"\n   📧 Original #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      Status: state={state}, status={status}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")
        
        # Look for one with emailsender set
        if emailsender and emailsender == contact_id and not working_email:
            working_email = email
            print(f"      🎯 This looks like a WORKING email!")

if working_email:
    print(f"\n🎉 FOUND WORKING EMAIL PATTERN!")
    print(f"📧 Working email: {working_email.get('subject', '')[:50]}")
    print(f"🔑 Key fields:")
    print(f"   _emailsender_value: {working_email.get('_emailsender_value')}")
    print(f"   sender: {working_email.get('sender')}")
    print(f"   submittedby: {working_email.get('submittedby')}")
    print(f"   from: {working_email.get('from')}")
    print(f"   torecipients: {working_email.get('torecipients')}")
    print(f"   Status: state={working_email.get('statecode')}, status={working_email.get('statuscode')}")
    
    # Now apply this exact pattern to our newest test email
    print(f"\n🔧 APPLYING WORKING PATTERN TO NEWEST TEST EMAIL...")
    
    # Get our newest test email
    newest_test_response = requests.get(
        f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and createdon ge 2025-06-11T00:00:00Z&$select=activityid,subject&$orderby=createdon desc&$top=1",
        headers=headers
    )
    
    if newest_test_response.status_code == 200:
        newest_tests = newest_test_response.json().get('value', [])
        if newest_tests:
            test_email_id = newest_tests[0]['activityid']
            test_subject = newest_tests[0].get('subject', '')[:30]
            
            print(f"   📧 Target test email: {test_subject}")
            print(f"   📧 ID: {test_email_id}")
            
            # Copy ALL the working email's field values
            update_data = {}
            
            # Copy each field from working email
            fields_to_copy = ['sender', 'submittedby', 'from', 'torecipients']
            for field in fields_to_copy:
                working_value = working_email.get(field)
                if working_value:
                    update_data[field] = working_value
                    print(f"   📋 Will copy {field}: {working_value}")
            
            # Most importantly, try to set the emailsender relationship
            if working_email.get('_emailsender_value') == contact_id:
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
                    print(f"   ✅ Successfully applied working pattern!")
                    
                    # Verify the result
                    verify_response = requests.get(
                        f"{crm_base_url}/emails({test_email_id})?$select=sender,_emailsender_value,submittedby,from,torecipients",
                        headers=headers
                    )
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        new_emailsender = verify_data.get('_emailsender_value')
                        
                        print(f"   📊 After applying working pattern:")
                        print(f"      sender: {verify_data.get('sender')}")
                        print(f"      _emailsender_value: {new_emailsender}")
                        print(f"      submittedby: {verify_data.get('submittedby')}")
                        print(f"      from: {verify_data.get('from')}")
                        print(f"      torecipients: {verify_data.get('torecipients')}")
                        
                        if new_emailsender == contact_id:
                            print(f"\n   🎉 SUCCESS! EmailSender now matches working pattern!")
                        else:
                            print(f"\n   ⚠️  EmailSender still not set correctly")
                else:
                    print(f"   ❌ Update failed: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"      Error: {error_detail}")
                    except:
                        print(f"      Error: {response.text[:200]}")
            else:
                print(f"   💡 No fields to copy from working email")
        else:
            print(f"   ❌ No test emails found to update")
    else:
        print(f"   ❌ Could not get test emails: {newest_test_response.status_code}")
        
else:
    print(f"\n⚠️  NO WORKING EMAIL PATTERN FOUND")
    print(f"   💡 All original emails also have _emailsender_value: None")
    print(f"   🤔 This suggests the issue might be:")
    print(f"      1. Dynamics 365 display logic changed")
    print(f"      2. Different field controls 'Email from:' display")
    print(f"      3. Need different approach to set emailsender")
    
    # Show what we have in original emails
    if original_emails:
        print(f"\n   📋 Original email field summary:")
        for i, email in enumerate(original_emails[:3]):
            subject = email.get('subject', '')[:30]
            emailsender = email.get('_emailsender_value')
            sender = email.get('sender')
            
            print(f"      #{i+1} {subject}: emailsender={emailsender}, sender={sender}")

print(f"\n💡 NEXT STEPS:")
if working_email:
    print(f"   📅 Refresh timeline and check 'Email from:' display")
    print(f"   🎯 Should now show 'Email from: service@ringcentral.com'")
else:
    print(f"   🔧 May need alternative approach")
    print(f"   💡 Consider different field or method")

print(f"\n📧 Please check the timeline results!") 