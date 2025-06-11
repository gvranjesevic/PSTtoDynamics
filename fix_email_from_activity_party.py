#!/usr/bin/env python3
"""
Fix "Email from:" display by creating a proper Activity Party record for the 'from' field.
"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🎯 FIXING 'EMAIL FROM:' WITH ACTIVITY PARTY")
print("="*42)

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

# Get the service@ringcentral.com contact ID
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname",
    headers=headers
)
contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Target Contact: {contact['fullname']} ({contact_id})")

# Get our newest test email to fix
print("\n📧 Finding newest test email...")
test_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=contains(subject, 'NEW TEST')&$select=activityid,subject&$orderby=createdon desc&$top=1",
    headers=headers
)
if test_emails_response.status_code != 200 or not test_emails_response.json().get('value'):
    print("❌ Could not find a 'NEW TEST' email to fix.")
    exit(1)

test_email = test_emails_response.json()['value'][0]
test_email_id = test_email['activityid']
print(f"   📧 Found test email: {test_email['subject']}")
print(f"   📧 ID: {test_email_id}")

# Construct the Activity Party payload for the 'from' field
# This is the key step that differs from all previous attempts.
# The 'from' field is a navigation property. The error message suggests 'email_sender' is wrong.
# The correct schema name is likely 'Email_Sender'.
from_activity_party_payload = {
    "Email_Sender": [
        {
            "partyid_contact@odata.bind": f"/contacts({contact_id})",
            "addressused": "service@ringcentral.com"
        }
    ]
}

print("\n🔧 Applying Activity Party payload to the 'from' field (using 'Email_Sender')...")
print(f"   🔗 Linking Contact ID {contact_id} to the email's 'from' field.")

update_response = requests.patch(
    f"{crm_base_url}/emails({test_email_id})",
    json=from_activity_party_payload,
    headers=headers
)

if update_response.status_code in [200, 204]:
    print("   ✅ SUCCESS: Activity Party payload accepted!")

    # Verify the results
    print("\n🔍 Verifying fields after update...")
    verify_response = requests.get(
        f"{crm_base_url}/emails({test_email_id})?$expand=email_sender($select=partyid,addressused)&$select=_emailsender_value,sender,from",
        headers=headers
    )

    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        new_emailsender_val = verify_data.get('_emailsender_value')
        from_parties = verify_data.get('email_sender', [])

        print("   📊 Post-Update Field Values:")
        print(f"      _emailsender_value: {new_emailsender_val}")

        if from_parties:
            from_party = from_parties[0]
            party_id = from_party.get('_partyid_value')
            address_used = from_party.get('addressused')
            print(f"      'from' field partyid: {party_id}")
            print(f"      'from' field addressused: {address_used}")

            if party_id == contact_id:
                print("\n🎉 ROOT CAUSE FOUND AND FIXED!")
                print("   The 'from' field must be populated with an Activity Party record.")
                print("   This successfully sets the sender relationship.")
            else:
                print("\n⚠️  Something went wrong. The partyid does not match.")
        else:
            print("\n⚠️  The 'from' field is still empty after the update.")
    else:
        print("   ❌ Verification failed.")
else:
    print(f"   ❌ FAILED: Dynamics API rejected the payload (Status: {update_response.status_code})")
    try:
        error_details = update_response.json()
        print(f"      Error: {error_details.get('error', {}).get('message')}")
    except:
        print(f"      Raw Error: {update_response.text}")


print("\n💡 CONCLUSION:")
print("   This approach is the most likely to succeed as it uses the correct data structure for email participants.")
print("\n📅 Please refresh the timeline and check if the 'Email from:' display is finally correct!") 