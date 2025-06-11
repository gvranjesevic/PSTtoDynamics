#!/usr/bin/env python3
"""Simple search for working RingCentral emails"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 SIMPLE WORKING EMAIL SEARCH")
print("="*31)

# Authenticate
app = msal.PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_domain}"
)

result = app.acquire_token_by_username_password(
    username=username,
    password=password,
    scopes=["https://dynglobal.crm.dynamics.com/.default"]
)

access_token = result["access_token"]
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}

# Get contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get ALL RingCentral emails to see the pattern
print(f"\n📧 Getting ALL RingCentral emails...")

all_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,_emailsender_value,sender,createdon&$orderby=actualstart desc&$top=20",
    headers=headers
)

if all_emails_response.status_code != 200:
    print(f"❌ Error: {all_emails_response.status_code}")
    exit(1)

all_emails = all_emails_response.json().get('value', [])
print(f"📧 Found {len(all_emails)} total emails")

# Analyze the emails
emails_with_emailsender = []
emails_without_emailsender = []

for email in all_emails:
    emailsender = email.get('_emailsender_value')
    if emailsender:
        emails_with_emailsender.append(email)
    else:
        emails_without_emailsender.append(email)

print(f"\n📊 EMAIL ANALYSIS:")
print(f"   ✅ Emails WITH _emailsender_value: {len(emails_with_emailsender)}")
print(f"   ❌ Emails WITHOUT _emailsender_value: {len(emails_without_emailsender)}")

if emails_with_emailsender:
    print(f"\n🎉 FOUND EMAILS WITH EMAILSENDER SET!")
    for i, email in enumerate(emails_with_emailsender[:3]):
        subject = email.get('subject', '')[:50]
        emailsender = email.get('_emailsender_value')
        sender = email.get('sender')
        created = email.get('createdon', '')[:19]
        
        print(f"\n   📧 Email #{i+1}: {subject}")
        print(f"      Created: {created}")
        print(f"      _emailsender_value: {emailsender}")
        print(f"      sender: {sender}")
        print(f"      ✅ This should show 'Email from: service@ringcentral.com'")

# If we found working emails, use the first one as template
if emails_with_emailsender:
    working_email = emails_with_emailsender[0]
    
    print(f"\n🔧 USING WORKING EMAIL AS TEMPLATE...")
    print(f"📧 Template: {working_email.get('subject', '')[:50]}")
    print(f"🔑 Template _emailsender_value: {working_email.get('_emailsender_value')}")
    
    # Get our newest test email to fix
    test_emails_response = requests.get(
        f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and subject like 'NEW TEST%'&$select=activityid,subject,_emailsender_value&$top=1",
        headers=headers
    )
    
    if test_emails_response.status_code == 200:
        test_emails = test_emails_response.json().get('value', [])
        if test_emails:
            test_email = test_emails[0]
            test_email_id = test_email['activityid']
            
            print(f"\n🎯 FIXING TEST EMAIL...")
            print(f"   📧 Test email: {test_email.get('subject', '')[:50]}")
            print(f"   📧 Current _emailsender_value: {test_email.get('_emailsender_value')}")
            
            # The key insight: if working emails have emailsender set to contact_id,
            # we need to figure out HOW they got that way
            
            if working_email.get('_emailsender_value') == contact_id:
                print(f"   💡 Working emails have _emailsender_value = contact_id")
                print(f"   🔧 Attempting to recreate this pattern...")
                
                # Try the relationship binding one more time, but differently
                approaches = [
                    {
                        'name': 'Standard emailsender_contact binding',
                        'data': {'emailsender_contact@odata.bind': f'/contacts({contact_id})'}
                    },
                    {
                        'name': 'Alternative binding format',
                        'data': {'emailsender@odata.bind': f'/contacts({contact_id})'}
                    }
                ]
                
                for approach in approaches:
                    print(f"\n   🧪 Trying: {approach['name']}")
                    
                    response = requests.patch(
                        f"{crm_base_url}/emails({test_email_id})",
                        json=approach['data'],
                        headers=headers
                    )
                    
                    if response.status_code in [200, 204]:
                        print(f"      ✅ Update successful!")
                        
                        # Check if it worked
                        verify_response = requests.get(
                            f"{crm_base_url}/emails({test_email_id})?$select=_emailsender_value",
                            headers=headers
                        )
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            new_emailsender = verify_data.get('_emailsender_value')
                            print(f"      📊 Result: _emailsender_value = {new_emailsender}")
                            
                            if new_emailsender == contact_id:
                                print(f"      🎉 SUCCESS! Now matches working pattern!")
                                break
                            else:
                                print(f"      ⚠️  Still not matching working pattern")
                    else:
                        print(f"      ❌ Failed: {response.status_code}")
        else:
            print(f"\n❌ No NEW TEST emails found")
    else:
        print(f"\n❌ Error getting test emails: {test_emails_response.status_code}")
        
else:
    print(f"\n⚠️  NO EMAILS WITH EMAILSENDER FOUND!")
    print(f"   💡 This means:")
    print(f"      1. ALL emails have _emailsender_value: None")
    print(f"      2. The 'Email from:' display uses a different field/logic")
    print(f"      3. May need to check a different contact or system")
    
    # Show what we do have
    if emails_without_emailsender:
        sample = emails_without_emailsender[0]
        print(f"\n   📋 Sample email fields:")
        print(f"      subject: {sample.get('subject', '')[:30]}")
        print(f"      sender: {sample.get('sender')}")
        print(f"      _emailsender_value: {sample.get('_emailsender_value')}")

print(f"\n💡 CONCLUSION:")
if emails_with_emailsender:
    print(f"   📅 Refresh timeline and check if 'Email from:' is now fixed")
    print(f"   🎯 Should show 'Email from: service@ringcentral.com'")
else:
    print(f"   🤔 All emails have same issue - may be system-wide")
    print(f"   💡 'Email from:' display may not depend on _emailsender_value")
    print(f"   🔧 May need different approach or field")

print(f"\n📧 Please check the timeline!") 