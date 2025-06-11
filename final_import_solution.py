#!/usr/bin/env python3
"""
Final Correct Solution: Import emails by creating them with a proper 'from'
Activity Party and then updating their status.
"""

import requests
import msal
import win32com.client
import time

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
pst_file_path = r"C:\Users\gvran\Desktop\Old PST Files\gvranjesevic@mvp4me.com.pst"

# --- Main Script ---

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("\n🔐 Authenticating with Dynamics 365...")
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
        print(f"❌ Authentication failed: {result.get('error_description')}")
        return None
    print("✅ Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

def get_contact_id(headers, email_address):
    """Finds and returns the contact ID for a given email address."""
    url = f"{crm_base_url}/contacts?$filter=emailaddress1 eq '{email_address}'&$select=contactid,fullname"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contacts = response.json().get('value', [])
        if contacts:
            contact = contacts[0]
            print(f"✅ Found Contact: {contact['fullname']} ({contact['contactid']})")
            return contact['contactid']
    print(f"❌ Could not find contact with email: {email_address}")
    return None

def get_april_emails_from_pst():
    """Extracts service@ringcentral.com emails from April 2025 from the PST file."""
    print("\n📂 Reading PST file for April 2025 RingCentral emails...")
    # THIS FUNCTION IS DISABLED DUE TO INTERMITTENT COM ERRORS
    print("   -> SKIPPING PST read due to errors. Using backup data.")
    return []

def get_april_emails_from_backup():
    """Returns a backup list of known-good sample emails."""
    print("\n📦 Using backup sample data instead of PST file...")
    return [
        {
            'subject': 'FINAL TEST 1 - New Text Message from (855) 777-3452',
            'body': 'CAUTION: This email originated from outside...\n\nText Message\n\nDear MVP Info, You have a new text message...',
            'received_time': '2025-04-01T16:19:57Z'
        },
        {
            'subject': 'FINAL TEST 2 - New Text Message from (630) 639-2362',
            'body': 'CAUTION: This email originated from outside...\n\nText Message\n\nDear MVP Info, You have a new text message...',
            'received_time': '2025-04-02T15:20:19Z'
        }
    ]

def import_emails(headers, contact_id, emails_to_import):
    """Imports the list of emails into Dynamics 365."""
    print(f"\n🚀 Starting import of {len(emails_to_import)} emails...")
    imported_count = 0
    error_count = 0

    for i, email_data in enumerate(emails_to_import):
        print(f"\n--- Processing email {i+1}/{len(emails_to_import)} ---")
        print(f"   Subject: {email_data['subject'][:60]}")

        # 1. Prepare email body and creation payload
        formatted_body = email_data['body'].replace('\n', '<br>')
        
        # This is the payload with the correct 'from' Activity Party
        create_payload = {
            'subject': email_data['subject'],
            'description': formatted_body,
            'regardingobjectid_contact@odata.bind': f"/contacts({contact_id})",
            'directioncode': False, # Incoming
            # Set the 'from' field using a single Activity Party object
            "Email_Sender": {
                "partyid_contact@odata.bind": f"/contacts({contact_id})"
            },
            # To field uses an array
            "email_recipients": [
                {
                    "partyid_contact@odata.bind": f"/contacts({contact_id})",
                }
            ],
            'actualstart': email_data['received_time'],
            'actualend': email_data['received_time'],
            'senton': email_data['received_time'],
        }

        # 2. Create the email record
        print("   1. Creating email record with correct 'from' party...")
        create_url = f"{crm_base_url}/emails"
        create_response = requests.post(create_url, headers=headers, json=create_payload)

        if create_response.status_code != 201:
            print(f"   ❌ FAILED to create email. Status: {create_response.status_code}")
            print(f"      Error: {create_response.text}")
            error_count += 1
            continue
        
        email_id = create_response.json()['activityid']
        print(f"   ✅ Email created successfully! (ID: {email_id})")

        # 3. Update the status to 'Closed'
        print("   2. Updating status to 'Closed'...")
        status_payload = { "statecode": 1, "statuscode": 4 } # 1=Completed, 4=Received
        update_url = f"{crm_base_url}/emails({email_id})"
        update_response = requests.patch(update_url, headers=headers, json=status_payload)

        if update_response.status_code == 204:
            print("   ✅ Status updated successfully!")
            imported_count += 1
        else:
            print(f"   ❌ FAILED to update status. Status: {update_response.status_code}")
            print(f"      Error: {update_response.text}")
            error_count += 1
        
        time.sleep(1) # Be kind to the API

    print("\n\n--- IMPORT COMPLETE ---")
    print(f"✅ Successfully imported: {imported_count}")
    print(f"❌ Errors: {error_count}")


if __name__ == "__main__":
    print("🎬 Final Import Script Initialized")
    print("================================")
    
    auth_headers = get_auth_headers()
    if not auth_headers:
        exit(1)

    ringcentral_contact_id = get_contact_id(auth_headers, 'service@ringcentral.com')
    if not ringcentral_contact_id:
        exit(1)

    # Use the backup data function instead of the failing PST function
    april_emails = get_april_emails_from_backup() 
    
    if not april_emails:
        print("\nNo emails to import. Exiting.")
        exit(0)
        
    confirmation = input(f"\n🤔 Found {len(april_emails)} TEST emails. Proceed with import? (yes/no): ").lower()
    if confirmation == 'yes':
        import_emails(auth_headers, ringcentral_contact_id, april_emails)
        print("\n🎉 All done! Please check the Dynamics 365 timeline.")
    else:
        print("\n❌ Import cancelled by user.") 