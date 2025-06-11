#!/usr/bin/env python3
"""Fix emailsender using navigation property to fix Email from display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING EMAILSENDER USING NAVIGATION PROPERTY")
print("="*50)

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

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ RingCentral contact: {contact['fullname']} ({contact_id})")

# Get one April email to test with
print("\n🔍 Getting test April email...")
email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$top=1&$select=activityid,subject,_emailsender_value",
    headers=headers
)

test_email = email_response.json()['value'][0]
test_email_id = test_email['activityid']

print(f"📧 Test email: {test_email.get('subject', 'No Subject')[:50]}...")
print(f"📧 Current _emailsender_value: {test_email.get('_emailsender_value', 'None')}")

# Method 1: Try setting emailsender using navigation property
print(f"\n🔧 METHOD 1: Setting emailsender using navigation property...")

update_data = {
    "emailsender_contact@odata.bind": f"/contacts({contact_id})"
}

response = requests.patch(
    f"{crm_base_url}/emails({test_email_id})",
    json=update_data,
    headers=headers
)

if response.status_code in [200, 204]:
    print(f"✅ SUCCESS! Updated emailsender_contact navigation property")
    print(f"📅 Please refresh Dynamics to check 'Email from' display!")
    
    # Verify the update
    verify_response = requests.get(
        f"{crm_base_url}/emails({test_email_id})?$select=_emailsender_value",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        new_value = verify_response.json().get('_emailsender_value')
        print(f"✅ Verification: _emailsender_value is now: {new_value}")
        
        if new_value == contact_id:
            print(f"🎉 PERFECT! Field was set correctly!")
            
            # Ask if we should fix all emails
            confirmation = input(f"\n🤔 This worked! Fix all 71 April emails? (yes/no): ").strip().lower()
            if confirmation in ['yes', 'y']:
                print(f"\n🔧 Updating all 71 April emails...")
                
                # Get all April emails
                all_april_response = requests.get(
                    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$select=activityid",
                    headers=headers
                )
                
                all_emails = all_april_response.json().get('value', [])
                print(f"📧 Found {len(all_emails)} emails to fix")
                
                fixed_count = 0
                error_count = 0
                
                for i, email in enumerate(all_emails):
                    email_id = email['activityid']
                    
                    try:
                        response = requests.patch(
                            f"{crm_base_url}/emails({email_id})",
                            json={"emailsender_contact@odata.bind": f"/contacts({contact_id})"},
                            headers=headers
                        )
                        
                        if response.status_code in [200, 204]:
                            fixed_count += 1
                            if (i + 1) % 10 == 0:
                                print(f"   ✅ Fixed {i + 1}/{len(all_emails)} emails...")
                        else:
                            error_count += 1
                            if error_count <= 3:
                                print(f"   ❌ Error on email {i+1}: {response.status_code}")
                                
                    except Exception as e:
                        error_count += 1
                        if error_count <= 3:
                            print(f"   ❌ Exception on email {i+1}: {str(e)}")
                
                print(f"\n🎯 FINAL RESULTS:")
                print(f"   ✅ Successfully fixed: {fixed_count} emails")
                print(f"   ❌ Errors: {error_count} emails")
                
                if fixed_count > 0:
                    print(f"\n🎉 SUCCESS!")
                    print(f"   📧 All emails should now show 'Email from: RingCentral'")
                    print(f"   📅 Refresh Dynamics 365 to see the changes!")
        else:
            print(f"⚠️  Field was set but value doesn't match expected")
else:
    print(f"❌ METHOD 1 failed: {response.status_code}")
    print(f"   Details: {response.text[:300]}")
    
    # Method 2: Try alternative approach
    print(f"\n🔧 METHOD 2: Trying alternative navigation property...")
    
    update_data = {
        "emailsender_queue@odata.bind": f"/contacts({contact_id})"
    }
    
    response2 = requests.patch(
        f"{crm_base_url}/emails({test_email_id})",
        json=update_data,
        headers=headers
    )
    
    if response2.status_code in [200, 204]:
        print(f"✅ METHOD 2 worked!")
        print(f"📅 Please refresh Dynamics to check 'Email from' display!")
    else:
        print(f"❌ METHOD 2 also failed: {response2.status_code}")
        print(f"   Details: {response2.text[:300]}")
        
        print(f"\n💡 The issue might be:")
        print(f"   - This field is read-only/calculated")
        print(f"   - A different navigation property name is needed")
        print(f"   - The field needs to be set during email creation, not update")
        print(f"   - System caching that takes time to update") 