#!/usr/bin/env python3
"""Import missing April service@ringcentral.com emails"""

import win32com.client
import requests
import msal
from datetime import datetime
import time

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"

print("📧 IMPORTING MISSING APRIL SERVICE@RINGCENTRAL.COM EMAILS")
print("="*60)

# 1. Authenticate
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

# 2. Get RingCentral contact
print("🔍 Getting RingCentral contact...")
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')&$select=contactid,fullname,emailaddress1", 
    headers=headers
)

if contact_response.status_code != 200:
    print(f"❌ Error getting RingCentral contact: {contact_response.status_code}")
    exit(1)

contacts = contact_response.json().get('value', [])
if not contacts:
    print("❌ RingCentral contact not found")
    exit(1)

ringcentral_contact = contacts[0]
contact_id = ringcentral_contact['contactid']
print(f"✅ RingCentral contact: {ringcentral_contact['fullname']} ({contact_id})")

# 3. Open PST and get April emails
print("📁 Opening PST file...")
outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
namespace.AddStore(pst_path)

pst_store = None
for store in namespace.Stores:
    if pst_path.lower() in store.FilePath.lower():
        pst_store = store
        break

if not pst_store:
    print("❌ Could not find PST store")
    exit(1)

print("✅ PST file opened")

def get_april_service_ringcentral_emails(folder, emails):
    """Get April 2025 service@ringcentral.com emails"""
    try:
        for message in folder.Items:
            try:
                if message.Class == 43:  # olMail
                    sender = getattr(message, 'SenderEmailAddress', '') or ''
                    
                    # Check specifically for service@ringcentral.com
                    if 'service@ringcentral.com' in sender.lower():
                        received_time = getattr(message, 'ReceivedTime', None)
                        sent_time = getattr(message, 'SentOn', None)
                        email_date = sent_time or received_time
                        
                        # Check if it's April 2025
                        if email_date and email_date.strftime('%Y-%m') == '2025-04':
                            email_data = {
                                'subject': getattr(message, 'Subject', '') or 'No Subject',
                                'sender': sender,
                                'received_time': received_time,
                                'sent_time': sent_time,
                                'body': getattr(message, 'Body', '') or '',
                                'html_body': getattr(message, 'HTMLBody', '') or '',
                                'date_for_sort': email_date
                            }
                            emails.append(email_data)
            except:
                continue
        
        # Search subfolders
        try:
            for subfolder in folder.Folders:
                get_april_service_ringcentral_emails(subfolder, emails)
        except:
            pass
    except:
        pass

print("🔍 Extracting April 2025 service@ringcentral.com emails...")
april_emails = []
root_folder = pst_store.GetRootFolder()
get_april_service_ringcentral_emails(root_folder, april_emails)

print(f"📧 Found {len(april_emails)} April 2025 service@ringcentral.com emails")

if len(april_emails) == 0:
    print("❌ No April emails found to import")
    exit(1)

# Sort by date (oldest first for chronological import)
april_emails.sort(key=lambda x: x['date_for_sort'] or '', reverse=False)

print(f"\n📅 Sample April emails to import:")
for i, email in enumerate(april_emails[:5]):
    date_str = email['date_for_sort'].strftime('%Y-%m-%d %H:%M') if email['date_for_sort'] else 'No Date'
    subject = email['subject'][:50]
    print(f"   {i+1}. {date_str} - {subject}")

# Ask for confirmation
confirmation = input(f"\n🤔 Import {len(april_emails)} April service@ringcentral.com emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Import cancelled")
    exit(0)

# 4. Import emails
print(f"\n🚀 Starting import of {len(april_emails)} emails...")
imported_count = 0
error_count = 0
batch_size = 5

for i, email_data in enumerate(april_emails):
    try:
        # Prepare email activity data
        sent_time = email_data.get('sent_time') or email_data.get('received_time')
        subject = email_data.get('subject', 'No Subject')[:200]
        body = (email_data.get('body', '') or email_data.get('html_body', ''))[:2000]
        
        activity_data = {
            'subject': subject,
            'description': body,
            'directioncode': True,  # Outgoing
            'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({contact_id})"
        }
        
        # Add timing if available
        if sent_time:
            try:
                if hasattr(sent_time, 'isoformat'):
                    time_str = sent_time.isoformat()
                else:
                    time_str = str(sent_time)
                
                activity_data['actualend'] = time_str
                activity_data['actualstart'] = time_str
            except:
                pass
        
        # Create email activity
        response = requests.post(
            f"{crm_base_url}/emails",
            json=activity_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            imported_count += 1
            if i % 5 == 0:  # Progress update every 5 emails
                print(f"   📧 Imported {imported_count}/{len(april_emails)} emails...")
        else:
            error_count += 1
            if error_count <= 3:  # Show first few errors
                print(f"   ❌ Error importing email {i+1}: {response.status_code}")
        
        # Small delay between emails
        time.sleep(0.3)
        
        # Batch delay every 5 emails
        if (i + 1) % batch_size == 0:
            print(f"   ⏸️  Batch delay...")
            time.sleep(2)
            
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"   ❌ Exception importing email {i+1}: {str(e)}")

print(f"\n🎯 IMPORT RESULTS:")
print(f"   ✅ Successfully imported: {imported_count} emails")
print(f"   ❌ Errors: {error_count} emails")
print(f"   📊 Success rate: {(imported_count/len(april_emails)*100):.1f}%")

if imported_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📧 {imported_count} April emails imported to RingCentral timeline")
    print(f"   📅 Check Dynamics 365 - you should now see April service@ringcentral.com emails!")
    print(f"   🔍 Timeline should show emails from April 2025")

# Close PST
try:
    namespace.RemoveStore(pst_store.StoreID)
    print("✅ PST file closed")
except:
    pass 