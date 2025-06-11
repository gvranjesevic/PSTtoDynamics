#!/usr/bin/env python3
"""Final complete solution: Create emails as received with all proper fields"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# Sample April 2025 emails
sample_april_emails = [
    {
        'subject': 'NEW TEST - New Text Message from (855) 777-3452 on 04/01/2025 9:19 AM',
        'actualstart': '2025-04-01T16:19:57Z',
        'body': '''CAUTION: This email originated from outside of the Dynamique organization and network. Do not click links or open attachments unless you recognize the sender and know the content is safe.

Text Message

Dear MVP Info, You have a new text message: From: (855) 777-3452 To: MVP Info Received: Tuesday, April 01, 2025 at 9:19 AM Message: Text message test April 1

To reply using the RingCentral app
. Thank you for using RingCentral! Work from anywhere with the RingCentral app. It's got everything you need to stay connected: team messaging, video meetings and phone - all in one app. Get started
By subscribing to and/or using RingCentral, you acknowledge agreement to our Terms of Use'''
    }
]

print("🚀 FINAL COMPLETE SOLUTION")
print("="*27)
print("Creating emails as RECEIVED with all fields correct from start")
print("="*58)

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

print(f"\n🧪 Testing COMPLETE solution with 1 test email...")

imported_count = 0
error_count = 0

for i, email_data in enumerate(sample_april_emails):
    print(f"\n📧 Processing email {i+1}/{len(sample_april_emails)}...")
    print(f"   Subject: {email_data['subject'][:60]}...")
    
    # Pre-format the body with proper HTML
    original_body = email_data['body']
    formatted_body = original_body.replace('\n\n', '<br><br>')
    formatted_body = formatted_body.replace('\n', '<br>')
    
    print(f"   🔧 Pre-formatted body with HTML breaks")
    
    try:
        # Create email with ALL fields correct (no statecode - will be set after)
        complete_email_data = {
            'subject': email_data['subject'],
            'description': formatted_body,
            'safedescription': formatted_body,
            'actualstart': email_data['actualstart'],
            'actualend': email_data['actualstart'],
            'regardingobjectid_contact@odata.bind': f"/contacts({contact_id})",
            'emailsender_contact@odata.bind': f"/contacts({contact_id})",  # EmailSender
            'directioncode': False,  # Incoming
            'sender': 'service@ringcentral.com',
            'torecipients': 'gvranjesevic@dynamique.com;',
            'submittedby': '"RingCentral" service@ringcentral.com',
            'senton': email_data['actualstart']
        }
        
        print(f"   📧 Creating with ALL fields...")
        create_response = requests.post(
            f"{crm_base_url}/emails",
            json=complete_email_data,
            headers=headers
        )
        
        if create_response.status_code not in [200, 201, 204]:
            error_count += 1
            print(f"   ❌ Error creating email: {create_response.status_code}")
            try:
                error_detail = create_response.json()
                print(f"      Details: {error_detail}")
            except:
                print(f"      Details: {create_response.text[:300]}")
            continue
        
        # Get the created email ID
        if create_response.status_code == 204:
            # Query for the most recent email
            recent_email_response = requests.get(
                f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$orderby=createdon desc&$top=1&$select=activityid",
                headers=headers
            )
            if recent_email_response.status_code == 200:
                recent_emails = recent_email_response.json().get('value', [])
                if recent_emails:
                    new_email_id = recent_emails[0]['activityid']
                else:
                    error_count += 1
                    print(f"   ❌ Could not find created email")
                    continue
            else:
                error_count += 1
                print(f"   ❌ Could not query for created email")
                continue
        else:
            created_email = create_response.json()
            new_email_id = created_email['activityid']
        
        print(f"   ✅ Created email: {new_email_id}")
        
        # STEP 2: Set the sender fields (must be done after creation)
        print(f"   🔧 Setting sender fields...")
        
        sender_update = {
            'sender': 'service@ringcentral.com',
            'emailsender_contact@odata.bind': f'/contacts({contact_id})',
            'torecipients': 'gvranjesevic@dynamique.com;',
            'submittedby': '"RingCentral" service@ringcentral.com'
        }
        
        sender_response = requests.patch(
            f"{crm_base_url}/emails({new_email_id})",
            json=sender_update,
            headers=headers
        )
        
        if sender_response.status_code not in [200, 204]:
            print(f"   ⚠️  Sender update failed: {sender_response.status_code}")
        else:
            print(f"   ✅ Sender fields updated!")
        
        # STEP 3: Set the correct status (completed + received)
        print(f"   📮 Setting RECEIVED status...")
        
        status_update = {
            'statecode': 1,   # Completed state
            'statuscode': 4   # Received status
        }
        
        status_response = requests.patch(
            f"{crm_base_url}/emails({new_email_id})",
            json=status_update,
            headers=headers
        )
        
        if status_response.status_code not in [200, 204]:
            error_count += 1
            print(f"   ❌ Status update failed: {status_response.status_code}")
            continue
        
        print(f"   ✅ Status updated to RECEIVED!")
        
        # Verify ALL fields are correct
        print(f"   🔍 Verifying all fields...")
        
        verify_response = requests.get(
            f"{crm_base_url}/emails({new_email_id})?$select=description,statuscode,statecode,sender,_emailsender_value,torecipients",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            desc = verify_data.get('description', '')
            status = verify_data.get('statuscode')
            state = verify_data.get('statecode')
            sender = verify_data.get('sender')
            emailsender = verify_data.get('_emailsender_value')
            torecipients = verify_data.get('torecipients')
            
            print(f"   📊 Verification:")
            print(f"      Status: state={state}, status={status}")
            print(f"      Sender: {sender}")
            print(f"      EmailSender: {emailsender}")
            print(f"      ToRecipients: {torecipients}")
            print(f"      HTML Formatting: {'✅' if '<br>' in desc else '❌'}")
            
            # Check success criteria
            success_checks = {
                'Correct Status': status == 4 and state == 1,
                'HTML Formatting': '<br>' in desc,
                'Sender Set': sender == 'service@ringcentral.com',
                'EmailSender Set': emailsender == contact_id,
                'ToRecipients Set': torecipients is not None
            }
            
            print(f"   🎯 Success Checks:")
            for check_name, passed in success_checks.items():
                status_icon = "✅" if passed else "❌"
                print(f"      {status_icon} {check_name}")
            
            if all(success_checks.values()):
                imported_count += 1
                print(f"   🎉 COMPLETE SUCCESS! All criteria met!")
            else:
                error_count += 1
                print(f"   ⚠️  Some criteria not met")
        else:
            error_count += 1
            print(f"   ❌ Could not verify email: {verify_response.status_code}")
            
    except Exception as e:
        error_count += 1
        print(f"   ❌ Exception: {str(e)}")

print(f"\n🎯 FINAL SOLUTION RESULTS:")
print("="*30)
print(f"✅ Successfully imported: {imported_count}")
print(f"❌ Errors: {error_count}")

if imported_count > 0:
    print(f"\n🎉 FINAL SOLUTION SUCCESS!")
    print(f"   📅 Please refresh Dynamics 365 timeline")
    print(f"   🔍 Check if the test email shows:")
    print(f"      ✅ Proper HTML line breaks (no underscores)")
    print(f"      ✅ 'Email from: service@ringcentral.com' (not Closed)")
    print(f"      ✅ Status: Closed")
    print(f"\n   🚀 If ALL criteria are met:")
    print(f"      - Apply this to all 71 April emails")
    print(f"      - Problem completely solved!")
else:
    print(f"\n❌ Final solution failed")
    print(f"   💡 Need alternative approach")

print(f"\n📧 Please check the timeline and report results!") 