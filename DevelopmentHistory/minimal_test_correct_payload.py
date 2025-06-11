#!/usr/bin/env python3
"""
Minimal Viable Script to test the creation of a single email
with the correct 'Email_Sender' payload (a single object).
"""

import requests
import msal

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

def get_auth_headers():
    app = msal.PublicClientApplication(client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    return {'Authorization': f'Bearer {result["access_token"]}', 'Accept': 'application/json', 'Content-Type': 'application/json'}

def get_contact_id(headers, email_address):
    url = f"{crm_base_url}/contacts?$filter=emailaddress1 eq '{email_address}'&$select=contactid"
    response = requests.get(url, headers=headers)
    return response.json()['value'][0]['contactid']

def create_single_email(headers, contact_id):
    print("🎬 Attempting to create a single test email...")
    
    # This is the corrected payload
    create_payload = {
        'subject': 'MINIMAL VIABLE TEST',
        'description': 'Testing the single object payload for Email_Sender.',
        'regardingobjectid_contact@odata.bind': f"/contacts({contact_id})",
        'directioncode': False,
        # Final Attempt: Use 'email_activity_parties' collection
        # This is a generic collection for all parties (from, to, cc, bcc)
        "email_activity_parties": [
            # From party
            {
                "partyid_contact@odata.bind": f"/contacts({contact_id})",
                "participationtypemask": 1 # 1 = From
            },
            # To party
            {
                "partyid_contact@odata.bind": f"/contacts({contact_id})",
                "participationtypemask": 2 # 2 = To
            }
        ]
    }

    create_url = f"{crm_base_url}/emails"
    response = requests.post(create_url, headers=headers, json=create_payload)

    if response.status_code == 201:
        email_id = response.json()['activityid']
        print(f"🎉 SUCCESS! Email created with ID: {email_id}")
        
        # Now update status
        status_payload = {"statecode": 1, "statuscode": 4}
        update_url = f"{crm_base_url}/emails({email_id})"
        status_response = requests.patch(update_url, headers=headers, json=status_payload)
        if status_response.status_code == 204:
            print("✅ Status successfully updated to 'Closed'.")
            print("✅ The 'Email from:' display should now be correct.")
        else:
            print("⚠️ Email created, but status update failed.")
            
    else:
        print(f"❌ FAILED to create email. Status: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    headers = get_auth_headers()
    contact_id = get_contact_id(headers, 'service@ringcentral.com')
    create_single_email(headers, contact_id) 