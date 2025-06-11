#!/usr/bin/env python3
"""
Complete PST Email Importer for Dynamics 365 - FINAL VERSION
===========================================================

This script reads ALL emails from the PST file, matches them with existing contacts
in Dynamics 365, and imports missing emails using the corrected Activity Party solution.

Features:
- Scans the entire PST file for all emails
- Matches emails with existing Dynamics contacts by email address
- Checks for existing emails to avoid duplicates
- Uses corrected Activity Party approach for proper sender display
- TEST MODE: Initially processes only one email address for testing
- Comprehensive error handling and progress tracking

Uses the PST file at: PST\\gvranjesevic@dynamique.com.001.pst
"""

import win32com.client
import requests
import msal
from datetime import datetime, timezone
import re
from collections import defaultdict
import time
import os

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# PST File Configuration - Updated to actual location
PST_FILE_PATH = r"PST\gvranjesevic@dynamique.com.001.pst"

# Known System User ID
SYSTEM_USER_ID = "5794f83f-9b37-f011-8c4e-000d3a9c4367"

# TEST MODE Configuration
TEST_MODE = True  # Set to False to process ALL email addresses
TEST_EMAIL_ADDRESS = "service@ringcentral.com"  # Email address to test with

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("Authenticating to Dynamics 365...")
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    
    if "access_token" not in result:
        print(f"Authentication failed: {result}")
        return None
    
    print("Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0',
        'Prefer': 'return=representation'  # Force return of created/updated object
    }

def extract_email_address(email_string):
    """Extracts email address from various formats."""
    if not email_string:
        return None
    
    email_string = str(email_string)
    
    # Look for email in angle brackets first
    match = re.search(r'<([^>]+@[^>]+)>', email_string)
    if match:
        return match.group(1).lower().strip()
    
    # If no brackets, check if the whole string is an email
    if '@' in email_string and '.' in email_string:
        return email_string.lower().strip()
    
    return None

def scan_pst_file():
    """Scans the PST file and groups emails by sender address."""
    print(f"\nScanning PST file: {PST_FILE_PATH}")
    
    if not os.path.exists(PST_FILE_PATH):
        print(f"PST file not found: {PST_FILE_PATH}")
        return {}
    
    try:
        # Initialize Outlook application
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        print("   Opening PST file...")
        
        # Try to access PST file
        pst_store = None
        temp_store_added = False
        
        # First check if PST is already loaded
        for store in namespace.Stores:
            if PST_FILE_PATH.lower() in str(store.FilePath).lower():
                pst_store = store
                print("   PST already loaded in Outlook")
                break
        
        # If not loaded, try to add it temporarily
        if not pst_store:
            try:
                namespace.AddStore(PST_FILE_PATH)
                temp_store_added = True
                print("   PST temporarily added to Outlook")
                
                # Find the newly added store
                for store in namespace.Stores:
                    if PST_FILE_PATH.lower() in str(store.FilePath).lower():
                        pst_store = store
                        break
            except Exception as e:
                print(f"   Could not add PST to stores: {e}")
                return {}
        
        if not pst_store:
            print("   Could not access PST store")
            return {}
        
        # Get the root folder
        root_folder = pst_store.GetRootFolder()
        print(f"   Root folder: {root_folder.Name}")
        
        emails_by_sender = defaultdict(list)
        total_emails = 0
        
        def scan_folder_recursive(folder, depth=0):
            nonlocal total_emails
            indent = "   " + "  " * depth
            
            try:
                print(f"{indent}Scanning folder: {folder.Name}")
                items = folder.Items
                
                folder_emails = 0
                for item in items:
                    try:
                        if hasattr(item, 'Class') and item.Class == 43:  # Mail item
                            # Try multiple ways to get sender email
                            sender_email = None
                            
                            # Method 1: SenderEmailAddress
                            if hasattr(item, 'SenderEmailAddress') and item.SenderEmailAddress:
                                sender_email = extract_email_address(item.SenderEmailAddress)
                            
                            # Method 2: If sender email is Exchange format, try Reply Recipients
                            if not sender_email and hasattr(item, 'ReplyRecipients'):
                                try:
                                    for recipient in item.ReplyRecipients:
                                        if hasattr(recipient, 'Address'):
                                            sender_email = extract_email_address(recipient.Address)
                                            if sender_email:
                                                break
                                except:
                                    pass
                            
                            # Method 3: Try Sender property
                            if not sender_email and hasattr(item, 'Sender') and item.Sender:
                                try:
                                    if hasattr(item.Sender, 'Address'):
                                        sender_email = extract_email_address(item.Sender.Address)
                                except:
                                    pass
                            
                            if sender_email:
                                try:
                                    email_data = {
                                        'subject': item.Subject or 'No Subject',
                                        'body': item.Body or '',
                                        'received_time': item.ReceivedTime if hasattr(item, 'ReceivedTime') else item.CreationTime,
                                        'sent_time': item.SentOn if hasattr(item, 'SentOn') and item.SentOn else item.CreationTime,
                                        'sender_name': item.SenderName or '',
                                        'sender_email': sender_email,
                                        'folder_path': folder.Name
                                    }
                                    emails_by_sender[sender_email].append(email_data)
                                    total_emails += 1
                                    folder_emails += 1
                                    
                                    if total_emails % 50 == 0:
                                        print(f"   Processed {total_emails} emails so far...")
                                except Exception as e:
                                    print(f"{indent}  Error processing email: {e}")
                    except Exception as e:
                        print(f"{indent}  Error with item: {e}")
                
                print(f"{indent}  Found {folder_emails} emails in this folder")
                
                # Recursively scan subfolders
                try:
                    for subfolder in folder.Folders:
                        scan_folder_recursive(subfolder, depth + 1)
                except Exception as e:
                    print(f"{indent}  Error scanning subfolders: {e}")
                    
            except Exception as e:
                print(f"{indent}Error scanning folder {folder.Name}: {e}")
        
        # Start scanning from root
        scan_folder_recursive(root_folder)
        
        # Clean up if we added the store temporarily
        if temp_store_added:
            try:
                namespace.RemoveStore(pst_store.StoreID)
                print("   Cleaned up temporary PST store")
            except:
                pass
        
        print(f"PST scan complete!")
        print(f"   Total emails found: {total_emails}")
        print(f"   Unique senders: {len(emails_by_sender)}")
        
        # Show top senders
        print(f"\nTop email senders:")
        sorted_senders = sorted(emails_by_sender.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (sender, emails) in enumerate(sorted_senders[:10]):
            print(f"   {i+1:2d}. {sender:<40} ({len(emails):3d} emails)")
        
        return emails_by_sender
        
    except Exception as e:
        print(f"Error scanning PST file: {e}")
        return {}

def get_dynamics_contacts(headers):
    """Retrieves all contacts from Dynamics 365 with email addresses."""
    print(f"\nRetrieving Dynamics 365 contacts...")
    
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
        
        print(f"Found {len(contacts)} contacts with email addresses")
        return contacts
    else:
        print(f"Failed to retrieve contacts: {response.status_code}")
        return {}

def get_existing_emails_for_contact(headers, contact_id):
    """Gets all existing emails for a specific contact from Dynamics 365."""
    print(f"   Checking existing emails for contact...")
    
    url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=subject,senton,createdon&$orderby=senton desc"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        existing_emails = response.json().get('value', [])
        print(f"   Found {len(existing_emails)} existing emails")
        return existing_emails
    else:
        print(f"   Failed to retrieve existing emails: {response.status_code}")
        return []

def is_email_duplicate(new_email, existing_emails):
    """Checks if an email already exists based on subject and sent time."""
    new_subject = new_email['subject'].strip()
    new_sent_time = new_email['sent_time']
    
    for existing in existing_emails:
        existing_subject = existing.get('subject', '').strip()
        
        # Check subject match
        if new_subject == existing_subject:
            # Check if times are close (within 1 hour)
            existing_time = existing.get('senton')
            if existing_time:
                try:
                    existing_dt = datetime.fromisoformat(existing_time.replace('Z', '+00:00'))
                    new_dt = new_sent_time.replace(tzinfo=timezone.utc) if new_sent_time.tzinfo is None else new_sent_time
                    
                    time_diff = abs((existing_dt - new_dt).total_seconds())
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
        
        # CRITICAL: Activity Party relationships - This is the corrected solution!
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
    
    email_id = None
    if response.status_code in [200, 201]:
        # Success with data returned
        try:
            response_data = response.json()
            email_id = response_data.get('activityid')
            print(f"   Email created successfully (Status: {response.status_code}, ID: {email_id})")
        except:
            print(f"   Email created successfully (Status: {response.status_code}, no ID in response)")
    elif response.status_code == 204:
        # Success but no content returned
        print(f"   Email created successfully (Status: {response.status_code}, no ID returned)")
        return "success_no_id"
    else:
        print(f"   Failed to create email: {response.status_code}")
        print(f"      Error: {response.text}")
        return None
    
    # Step 2: Update status to Closed (only if we have email ID)
    if email_id:
        update_url = f"{crm_base_url}/emails({email_id})"
        update_payload = {
            "statecode": 1,  # Completed
            "statuscode": 3  # Closed
        }
        
        update_response = requests.patch(update_url, json=update_payload, headers=headers)
        
        # Both 200 (OK) and 204 (No Content) are success for PATCH
        if update_response.status_code in [200, 204]:
            print(f"   Email status updated to Closed (Status: {update_response.status_code})")
            return email_id
        else:
            print(f"   Email created but status update failed: {update_response.status_code}")
            print(f"      Update error: {update_response.text}")
            return email_id
    
    return "success_no_id"

def process_emails_for_sender(headers, sender_email, pst_emails, contacts):
    """Processes all emails for a specific sender."""
    
    if sender_email not in contacts:
        print(f"No contact found for {sender_email}, skipping {len(pst_emails)} emails")
        return {'imported': 0, 'skipped': len(pst_emails), 'errors': 0}
    
    contact = contacts[sender_email]
    contact_id = contact['id']
    contact_name = contact['name']
    
    print(f"\nProcessing emails for: {contact_name} ({sender_email})")
    print(f"   Total PST emails found: {len(pst_emails)}")
    
    # Get existing emails for this contact
    existing_emails = get_existing_emails_for_contact(headers, contact_id)
    
    # Filter out duplicates
    new_emails = []
    for email in pst_emails:
        if not is_email_duplicate(email, existing_emails):
            new_emails.append(email)
    
    skipped_count = len(pst_emails) - len(new_emails)
    if skipped_count > 0:
        print(f"   Skipping {skipped_count} duplicate emails")
    
    if not new_emails:
        print(f"   All emails already exist for this contact")
        return {'imported': 0, 'skipped': len(pst_emails), 'errors': 0}
    
    print(f"   Importing {len(new_emails)} new emails...")
    
    # Import new emails
    imported_count = 0
    error_count = 0
    
    for i, email_data in enumerate(new_emails):
        print(f"   Importing email {i+1}/{len(new_emails)}: {email_data['subject'][:50]}...")
        
        email_id = create_email_with_activity_party(headers, email_data, contact_id)
        
        if email_id:
            imported_count += 1
        else:
            error_count += 1
        
        # Small delay between emails
        time.sleep(1)
        
        # Batch delay every 5 emails
        if (i + 1) % 5 == 0 and (i + 1) < len(new_emails):
            print(f"   Batch delay (processed {i+1}/{len(new_emails)})...")
            time.sleep(3)
    
    print(f"   Contact processing complete:")
    print(f"      Imported: {imported_count}")
    print(f"      Skipped: {skipped_count}")
    print(f"      Errors: {error_count}")
    
    return {'imported': imported_count, 'skipped': skipped_count, 'errors': error_count}

def main():
    """Main execution function."""
    print("COMPLETE PST EMAIL IMPORTER")
    print("=" * 60)
    print(f"PST File: {PST_FILE_PATH}")
    
    if TEST_MODE:
        print(f"TEST MODE: Processing only {TEST_EMAIL_ADDRESS}")
    else:
        print("FULL MODE: Processing ALL email addresses")
    
    print()
    
    # Step 1: Authenticate
    headers = get_auth_headers()
    if not headers:
        return
    
    # Step 2: Scan PST file
    emails_by_sender = scan_pst_file()
    if not emails_by_sender:
        print("No emails found in PST file")
        return
    
    # Step 3: Get Dynamics contacts
    contacts = get_dynamics_contacts(headers)
    if not contacts:
        print("No contacts found in Dynamics 365")
        return
    
    # Step 4: Process emails
    print(f"\nStarting email processing...")
    
    if TEST_MODE:
        if TEST_EMAIL_ADDRESS in emails_by_sender:
            print(f"\nTesting with {TEST_EMAIL_ADDRESS}")
            pst_emails = emails_by_sender[TEST_EMAIL_ADDRESS]
            results = process_emails_for_sender(headers, TEST_EMAIL_ADDRESS, pst_emails, contacts)
            
            print(f"\nTEST RESULTS:")
            print(f"   Imported: {results['imported']}")
            print(f"   Skipped: {results['skipped']}")
            print(f"   Errors: {results['errors']}")
        else:
            print(f"Test email address {TEST_EMAIL_ADDRESS} not found in PST")
    else:
        # Process all email addresses
        total_results = {'imported': 0, 'skipped': 0, 'errors': 0}
        processed_contacts = 0
        
        for sender_email, pst_emails in emails_by_sender.items():
            if sender_email in contacts:
                results = process_emails_for_sender(headers, sender_email, pst_emails, contacts)
                
                total_results['imported'] += results['imported']
                total_results['skipped'] += results['skipped']
                total_results['errors'] += results['errors']
                processed_contacts += 1
                
                # Delay between contacts
                time.sleep(2)
        
        print(f"\nFINAL RESULTS:")
        print(f"   Processed contacts: {processed_contacts}")
        print(f"   Total imported: {total_results['imported']}")
        print(f"   Total skipped: {total_results['skipped']}")
        print(f"   Total errors: {total_results['errors']}")
    
    print(f"\nComplete PST Email Import finished!")

if __name__ == "__main__":
    main() 