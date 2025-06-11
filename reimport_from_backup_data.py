#!/usr/bin/env python3
"""Re-import April emails using successful data with draft-first strategy"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# Sample April 2025 emails (representing the type we need to import)
sample_april_emails = [
    {
        'subject': 'New Text Message from (855) 777-3452 on 04/01/2025 9:19 AM',
        'actualstart': '2025-04-01T16:19:57Z',
        'body': '''CAUTION: This email originated from outside of the Dynamique organization and network. Do not click links or open attachments unless you recognize the sender and know the content is safe.

Text Message

Dear MVP Info, You have a new text message: From: (855) 777-3452 To: MVP Info Received: Tuesday, April 01, 2025 at 9:19 AM Message: Text message test April 1

To reply using the RingCentral app
. Thank you for using RingCentral! Work from anywhere with the RingCentral app. It's got everything you need to stay connected: team messaging, video meetings and phone - all in one app. Get started
By subscribing to and/or using RingCentral, you acknowledge agreement to our Terms of Use'''
    },
    {
        'subject': 'New Text Message from (630) 639-2362 on 04/02/2025 8:20 AM',
        'actualstart': '2025-04-02T15:20:19Z',
        'body': '''CAUTION: This email originated from outside of the Dynamique organization and network. Do not click links or open attachments unless you recognize the sender and know the content is safe.

Text Message

Dear MVP Info, You have a new text message: From: (630) 639-2362 To: MVP Info Received: Wednesday, April 02, 2025 at 8:20 AM Message: Good morning! Mett , Can we reschedule our appointment. For next week ! Or on this Friday I am available. Because due to weather my dog little uncomfortable. Thank you 🙏

To reply using the RingCentral app
. Thank you for using RingCentral! Work from anywhere with the RingCentral app. It's got everything you need to stay connected: team messaging, video meetings and phone - all in one app. Get started
By subscribing to and/or using RingCentral, you acknowledge agreement to our Terms of Use'''
    },
    {
        'subject': 'New Text Message from (888) 904-8461 on 04/30/2025 2:54 PM',
        'actualstart': '2025-04-30T21:54:53Z',
        'body': '''CAUTION: This email originated from outside of the Dynamique organization and network. Do not click links or open attachments unless you recognize the sender and know the content is safe.

Text Message

Dear MVP Info, You have a new text message: From: (888) 904-8461 On 04/30/2025 2:54 PM Message: Your Assurity Life Insurance passcode is: 122065

To reply using the RingCentral app
. Thank you for using RingCentral! Work from anywhere with the RingCentral app. It's got everything you need to stay connected: team messaging, video meetings and phone - all in one app. Get started
By subscribing to and/or using RingCentral, you acknowledge agreement to our Terms of Use'''
    }
]

print("🚀 RE-IMPORT WITH DRAFT-FIRST STRATEGY")
print("="*40)
print("Testing with sample emails to prove the concept")
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

# Get contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

print(f"\n🧪 Testing draft-first strategy with {len(sample_april_emails)} sample emails...")

imported_count = 0
error_count = 0

for i, email_data in enumerate(sample_april_emails):
    print(f"\n📧 Processing email {i+1}/{len(sample_april_emails)}...")
    print(f"   Subject: {email_data['subject'][:50]}...")
    
    # STEP 1: Pre-format the body with proper HTML
    original_body = email_data['body']
    
    # Replace common line separators with HTML breaks
    formatted_body = original_body.replace('\n\n', '<br><br>')
    formatted_body = formatted_body.replace('\n', '<br>')
    
    # Ensure we have proper paragraph breaks
    formatted_body = formatted_body.replace('Text Message<br><br>Dear', 'Text Message<br><br>Dear')
    formatted_body = formatted_body.replace('To reply using the RingCentral app<br>', '<br>To reply using the RingCentral app<br>')
    
    print(f"   🔧 Pre-formatted body with HTML breaks")
    
    try:
        # STEP 2: Create email as DRAFT with proper formatting AND emailsender
        draft_email_data = {
            'subject': email_data['subject'],
            'description': formatted_body,
            'safedescription': formatted_body,
            'actualstart': email_data['actualstart'],
            'actualend': email_data['actualstart'],
            'regardingobjectid_contact@odata.bind': f"/contacts({contact_id})",
            'emailsender_contact@odata.bind': f"/contacts({contact_id})",  # KEY FIX!
            'statuscode': 1,  # DRAFT - This is the key!
            'directioncode': False,  # Incoming
            'sender': 'service@ringcentral.com',
            'torecipients': 'gvranjesevic@dynamique.com;',
            'submittedby': '"RingCentral" service@ringcentral.com',
            'senton': email_data['actualstart']
        }
        
        print(f"   📝 Creating as DRAFT...")
        create_response = requests.post(
            f"{crm_base_url}/emails",
            json=draft_email_data,
            headers=headers
        )
        
        if create_response.status_code not in [200, 201, 204]:
            error_count += 1
            print(f"   ❌ Error creating DRAFT: {create_response.status_code}")
            if error_count <= 2:
                print(f"      Details: {create_response.text[:300]}")
            continue
        
        # Handle 204 No Content response (creation success but no body returned)
        if create_response.status_code == 204:
            # For 204, we need to get the created email ID from the Location header or by querying
            # Let's query for the most recently created email for this contact
            recent_email_response = requests.get(
                f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$orderby=createdon desc&$top=1&$select=activityid",
                headers=headers
            )
            if recent_email_response.status_code == 200:
                recent_emails = recent_email_response.json().get('value', [])
                if recent_emails:
                    new_email_id = recent_emails[0]['activityid']
                    print(f"   ✅ Created as DRAFT: {new_email_id}")
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
            print(f"   ✅ Created as DRAFT: {new_email_id}")
        
        # STEP 3: Verify the email is in draft and properly formatted
        print(f"   🔍 Verifying draft formatting...")
        
        verify_response = requests.get(
            f"{crm_base_url}/emails({new_email_id})?$select=description,statuscode",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            current_desc = verify_data.get('description', '')
            current_status = verify_data.get('statuscode')
            
            print(f"   📊 Status: {current_status} (should be 1=Draft)")
            
            # Check if our formatting is preserved
            if '<br>' in current_desc:
                print(f"   ✅ HTML formatting preserved in draft!")
            else:
                print(f"   ⚠️  Formatting may not be preserved")
        
        # STEP 4: Now change to RECEIVED status (CORRECTED!)
        print(f"   📮 Changing to RECEIVED status...")
        
        status_update = {
            'statecode': 1,   # Completed state
            'statuscode': 4   # Received status
        }
        
        status_response = requests.patch(
            f"{crm_base_url}/emails({new_email_id})",
            json=status_update,
            headers=headers
        )
        
        if status_response.status_code in [200, 204]:
            imported_count += 1
            print(f"   ✅ Successfully completed! Now status = 4 (Received)")
            
            # Final verification
            final_verify = requests.get(
                f"{crm_base_url}/emails({new_email_id})?$select=description,statuscode,directioncode",
                headers=headers
            )
            
            if final_verify.status_code == 200:
                final_data = final_verify.json()
                final_desc = final_data.get('description', '')
                final_status = final_data.get('statuscode')
                final_direction = final_data.get('directioncode')
                
                print(f"   📊 Final: Status={final_status}, Direction={final_direction}")
                
                if '<br>' in final_desc:
                    print(f"   🎉 HTML formatting SURVIVED the status change!")
                else:
                    print(f"   😞 Formatting was lost during status change")
        else:
            error_count += 1
            print(f"   ❌ Status update failed: {status_response.status_code}")
            print(f"      Email created but stuck in draft")
            
    except Exception as e:
        error_count += 1
        print(f"   ❌ Exception: {str(e)}")

print(f"\n🎯 DRAFT-FIRST STRATEGY RESULTS:")
print("="*35)
print(f"✅ Successfully imported: {imported_count}")
print(f"❌ Errors: {error_count}")

if imported_count > 0:
    print(f"\n🎉 DRAFT-FIRST STRATEGY TEST COMPLETE!")
    print(f"   📅 Please refresh Dynamics 365 timeline")
    print(f"   🔍 Check if the {imported_count} test emails show:")
    print(f"      ✅ Proper HTML line breaks (no underscores)")
    print(f"      ✅ Better 'Email from:' display")
    print(f"      ✅ Correct status (Received)")
    print(f"\n   💡 If successful, we can:")
    print(f"      - Apply this strategy to all 71 April emails")
    print(f"      - This should resolve both major issues!")
else:
    print(f"\n❌ Draft-first strategy failed")
    print(f"   💡 Need to investigate the errors above")

print(f"\n📧 Please check the timeline and report results!") 