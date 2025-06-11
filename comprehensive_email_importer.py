#!/usr/bin/env python3
"""
Comprehensive Email Importer for Dynamics 365
==============================================

This script reads ALL emails from a PST file, compares them with existing emails 
in Dynamics 365, and imports missing emails using the corrected Activity Party solution.

Features:
- Scans entire PST file for all emails
- Groups emails by sender address
- Checks existing contacts in Dynamics 365
- Identifies missing emails per contact
- Imports using corrected Activity Party relationships
- Initially configured for testing with one email address

Based on: SOLUTION_TO_EMAIL_FROM_PROBLEM.md
"""

import win32com.client
import requests
import msal
from datetime import datetime, timezone
import re
from collections import defaultdict
import time

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# PST File Configuration
PST_FILE_PATH = r"C:\Users\gvran\Desktop\Old PST Files\gvranjesevic@mvp4me.com.pst"

# Known System User ID
SYSTEM_USER_ID = "5794f83f-9b37-f011-8c4e-000d3a9c4367"

# TEST MODE: Initially only process this email address
TEST_EMAIL_ADDRESS = "service@ringcentral.com"
TEST_MODE = True  # Set to False to process ALL email addresses

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("🔐 Authenticating to Dynamics 365...")
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    
    if "access_token" not in result:
        print(f"❌ Authentication failed: {result}")
        return None
    
    print("✅ Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

def extract_email_address(email_string):
    """Extracts email address from various formats."""
    if not email_string:
        return None
    
    # Look for email in angle brackets first
    match = re.search(r'<([^>]+@[^>]+)>', email_string)
    if match:
        return match.group(1).lower().strip()
    
    # If no brackets, check if the whole string is an email
    if '@' in email_string and '.' in email_string:
        return email_string.lower().strip()
    
    return None

def scan_pst_file():
    """Scans the entire PST file and groups emails by sender address."""
    print(f"\n📁 Scanning PST file: {PST_FILE_PATH}")
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        pst = namespace.AddStore(PST_FILE_PATH)
        
        # Get the root folder of the PST
        for store in namespace.Stores:
            if PST_FILE_PATH.lower() in str(store.FilePath).lower():
                root_folder = store.GetRootFolder()
                break
        else:
            print("❌ Could not find PST file in Outlook stores")
            return {}
        
        emails_by_sender = defaultdict(list)
        total_emails = 0
        
        def scan_folder(folder, path=""):
            nonlocal total_emails
            try:
                items = folder.Items
                items.Sort("[ReceivedTime]", True)  # Sort by received time, newest first
                
                for item in items:
                    if item.Class == 43:  # Mail item
                        sender_email = extract_email_address(item.SenderEmailAddress)
                        if sender_email:
                            email_data = {
                                'subject': item.Subject or 'No Subject',
                                'body': item.Body or '',
                                'received_time': item.ReceivedTime,
                                'sent_time': item.SentOn,
                                'sender_name': item.SenderName or '',
                                'sender_email': sender_email,
                                'folder_path': path + folder.Name
                            }
                            emails_by_sender[sender_email].append(email_data)
                            total_emails += 1
                            
                            if total_emails % 100 == 0:
                                print(f"   📧 Processed {total_emails} emails so far...")
                
                # Recursively scan subfolders
                for subfolder in folder.Folders:
                    scan_folder(subfolder, path + folder.Name + "/")
                    
            except Exception as e:
                print(f"   ⚠️ Error scanning folder {folder.Name}: {e}")
        
        # Start scanning from root
        scan_folder(root_folder)
        
        print(f"✅ PST scan complete!")
        print(f"   📧 Total emails found: {total_emails}")
        print(f"   👥 Unique senders: {len(emails_by_sender)}")
        
        # Show top senders
        print(f"\n📊 Top email senders:")
        sorted_senders = sorted(emails_by_sender.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (sender, emails) in enumerate(sorted_senders[:10]):
            print(f"   {i+1:2d}. {sender:<40} ({len(emails):3d} emails)")
        
        return emails_by_sender
        
    except Exception as e:
        print(f"❌ Error scanning PST file: {e}")
        return {}

def get_dynamics_contacts(headers):
    """Retrieves all contacts from Dynamics 365 with email addresses."""
    print(f"\n👥 Retrieving Dynamics 365 contacts...")
    
    contacts = {}
    url = f"{crm_base_url}/contacts?$select=contactid,fullname,emailaddress1&$filter=emailaddress1 ne null"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contact_list = response.json().get('value', [])
        for contact in contact_list:
            email = contact.get('emailaddress1', '').lower().strip()
            if email:
                contacts[email] = {
                    'id': contact['contactid'],
                    'name': contact['fullname']
                }
        
        print(f"✅ Found {len(contacts)} contacts with email addresses")
        return contacts
    else:
        print(f"❌ Failed to retrieve contacts: {response.status_code}")
        return {}

def get_existing_emails_for_contact(headers, contact_id):
    """Gets all existing emails for a specific contact from Dynamics 365."""
    print(f"   🔍 Checking existing emails for contact...")
    
    url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=subject,senton,createdon&$orderby=senton desc"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        existing_emails = response.json().get('value', [])
        print(f"   📧 Found {len(existing_emails)} existing emails")
        return existing_emails
    else:
        print(f"   ❌ Failed to retrieve existing emails: {response.status_code}")
        return []

def is_email_duplicate(new_email, existing_emails):
    """Checks if an email already exists based on subject and sent time."""
    new_subject = new_email['subject'].strip()
    new_sent_time = new_email['sent_time']
    
    for existing in existing_emails:
        existing_subject = existing.get('subject', '').strip()
        
        # Check subject match
        if new_subject == existing_subject:
            # Check if sent times are close (within 1 hour)
            if existing.get('senton'):
                try:
                    existing_time = datetime.fromisoformat(existing['senton'].replace('Z', '+00:00'))
                    time_diff = abs((new_sent_time - existing_time).total_seconds())
                    if time_diff < 3600:  # Within 1 hour
                        return True
                except:
                    pass
    
    return False

def create_email_with_activity_party(headers, email_data, contact_id):
    """Creates an email using the corrected Activity Party approach."""
    
    # Convert email body to HTML with line breaks
    body_html = email_data['body'].replace('\n', '<br>').replace('\r', '')
    
    # Format datetime for API
    sent_time = email_data['sent_time'].strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Email payload with correct Activity Party structure
    email_payload = {
        "subject": email_data['subject'],
        "description": body_html,
        "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
        "directioncode": False,  # Incoming email
        "actualstart": sent_time,
        "actualend": sent_time,
        "senton": sent_time,
        
        # CRITICAL: Activity Party relationships
        "email_activity_parties": [
            {
                # Sender (From): Contact
                "partyid_contact@odata.bind": f"/contacts({contact_id})",
                "participationtypemask": 1  # From/Sender
            },
            {
                # Recipient (To): System User
                "partyid_systemuser@odata.bind": f"/systemusers({SYSTEM_USER_ID})",
                "participationtypemask": 2  # To/Recipient
            }
        ]
    }
    
    # Step 1: Create the email
    create_url = f"{crm_base_url}/emails"
    response = requests.post(create_url, json=email_payload, headers=headers)
    
    if response.status_code == 204:
        # Get email ID from response header
        location_header = response.headers.get('OData-EntityId', '')
        if location_header:
            email_id = location_header.split('(')[1].split(')')[0]
            
            # Step 2: Update status to Closed
            status_payload = {"statecode": 1, "statuscode": 4}
            update_url = f"{crm_base_url}/emails({email_id})"
            status_response = requests.patch(update_url, json=status_payload, headers=headers)
            
            if status_response.status_code in [200, 204]:
                return True, email_id
            else:
                print(f"   ⚠️ Created email but failed to update status: {status_response.status_code}")
                return True, email_id
        else:
            print(f"   ⚠️ Email created but couldn't get ID")
            return True, None
    else:
        print(f"   ❌ Failed to create email: {response.status_code} - {response.text}")
        return False, None

def process_emails_for_sender(headers, sender_email, pst_emails, contacts):
    """Processes all emails for a specific sender."""
    print(f"\n🎯 Processing emails for: {sender_email}")
    
    # Check if contact exists
    if sender_email not in contacts:
        print(f"   ❌ No contact found for {sender_email} - skipping")
        return 0, 0
    
    contact = contacts[sender_email]
    contact_id = contact['id']
    contact_name = contact['name']
    
    print(f"   ✅ Found contact: {contact_name} ({contact_id})")
    print(f"   📧 PST emails to process: {len(pst_emails)}")
    
    # Get existing emails for this contact
    existing_emails = get_existing_emails_for_contact(headers, contact_id)
    
    # Find emails that need to be imported
    emails_to_import = []
    for email in pst_emails:
        if not is_email_duplicate(email, existing_emails):
            emails_to_import.append(email)
    
    print(f"   📤 New emails to import: {len(emails_to_import)}")
    
    if len(emails_to_import) == 0:
        print(f"   ✅ All emails already imported - nothing to do!")
        return 0, len(pst_emails)
    
    # Import new emails
    imported_count = 0
    failed_count = 0
    
    for i, email in enumerate(emails_to_import):
        print(f"   📧 Importing {i+1}/{len(emails_to_import)}: {email['subject'][:50]}...")
        
        success, email_id = create_email_with_activity_party(headers, email, contact_id)
        if success:
            imported_count += 1
            print(f"      ✅ Success! Email ID: {email_id}")
        else:
            failed_count += 1
            print(f"      ❌ Failed to import")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    print(f"   📊 Import summary: {imported_count} success, {failed_count} failed")
    return imported_count, len(existing_emails)

def main():
    """Main function that orchestrates the entire import process."""
    print("🚀 Comprehensive Email Importer for Dynamics 365")
    print("=" * 60)
    print("Based on: SOLUTION_TO_EMAIL_FROM_PROBLEM.md")
    
    if TEST_MODE:
        print(f"🧪 TEST MODE: Only processing {TEST_EMAIL_ADDRESS}")
    else:
        print("🎯 FULL MODE: Processing all email addresses")
    
    print()
    
    # Step 1: Authenticate
    headers = get_auth_headers()
    if not headers:
        exit(1)
    
    # Step 2: Scan PST file
    emails_by_sender = scan_pst_file()
    if not emails_by_sender:
        print("❌ No emails found in PST file")
        exit(1)
    
    # Step 3: Get Dynamics contacts
    contacts = get_dynamics_contacts(headers)
    if not contacts:
        print("❌ No contacts found in Dynamics 365")
        exit(1)
    
    # Step 4: Process emails
    total_imported = 0
    total_existing = 0
    
    if TEST_MODE:
        # Only process the test email address
        if TEST_EMAIL_ADDRESS in emails_by_sender:
            imported, existing = process_emails_for_sender(
                headers, TEST_EMAIL_ADDRESS, 
                emails_by_sender[TEST_EMAIL_ADDRESS], 
                contacts
            )
            total_imported += imported
            total_existing += existing
        else:
            print(f"❌ Test email address {TEST_EMAIL_ADDRESS} not found in PST file")
    else:
        # Process all email addresses that have matching contacts
        for sender_email in emails_by_sender:
            if sender_email in contacts:
                imported, existing = process_emails_for_sender(
                    headers, sender_email, 
                    emails_by_sender[sender_email], 
                    contacts
                )
                total_imported += imported
                total_existing += existing
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 IMPORT COMPLETE!")
    print(f"   📧 Total emails imported: {total_imported}")
    print(f"   ✅ Total emails already existed: {total_existing}")
    print(f"   📊 Grand total: {total_imported + total_existing}")
    
    if TEST_MODE:
        print(f"\n🧪 Test completed for: {TEST_EMAIL_ADDRESS}")
        print("   To run for ALL email addresses, set TEST_MODE = False")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 