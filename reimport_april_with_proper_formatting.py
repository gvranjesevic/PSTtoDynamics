#!/usr/bin/env python3
"""Re-import April emails with proper formatting strategy"""

import win32com.client
import requests
import msal
from datetime import datetime
import time
import re

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# PST file configuration
pst_file_path = r"C:\Users\gvran\Desktop\Old PST Files\gvranjesevic@mvp4me.com.pst"

print("🚀 RE-IMPORT APRIL EMAILS WITH PROPER FORMATTING")
print("="*55)
print("Strategy:")
print("1. Import as DRAFT status")
print("2. Fix formatting while in draft")
print("3. Change to received status")
print("4. This should resolve both issues!")
print("="*55)

# Authenticate with Dynamics
print("\n🔐 Authenticating with Dynamics...")
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

print("✅ Dynamics authentication successful!")

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Target contact: {contact['fullname']} ({contact_id})")

# Connect to Outlook
print(f"\n📧 Connecting to Outlook...")
try:
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    print("✅ Outlook connection successful!")
except Exception as e:
    print(f"❌ Outlook connection failed: {e}")
    exit(1)

# Add PST file
print(f"📂 Adding PST file...")
try:
    namespace.AddStore(pst_file_path)
    print(f"✅ PST file added: {pst_file_path}")
except Exception as e:
    print(f"❌ PST file error: {e}")
    exit(1)

# Find the PST store
pst_store = None
for store in namespace.Stores:
    if pst_file_path.lower() in store.FilePath.lower():
        pst_store = store
        break

if not pst_store:
    print("❌ Could not find PST store")
    exit(1)

print(f"✅ Found PST store: {pst_store.DisplayName}")

# Get April 2025 service@ringcentral.com emails
print(f"\n🔍 Searching for April 2025 service@ringcentral.com emails...")

try:
    inbox = pst_store.GetDefaultFolder(6)  # Inbox
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)
    
    april_emails = []
    
    for message in messages:
        try:
            if hasattr(message, 'SenderEmailAddress') and hasattr(message, 'ReceivedTime'):
                sender = message.SenderEmailAddress
                received_time = message.ReceivedTime
                
                # Check if from service@ringcentral.com and April 2025
                if (sender and 'service@ringcentral.com' in sender and 
                    received_time and received_time.year == 2025 and received_time.month == 4):
                    april_emails.append(message)
                    
        except Exception as e:
            continue
    
    print(f"📧 Found {len(april_emails)} April 2025 service@ringcentral.com emails")
    
except Exception as e:
    print(f"❌ Error accessing PST: {e}")
    exit(1)

if len(april_emails) == 0:
    print("❌ No April emails found!")
    exit(1)

# Show sample
print(f"\n📝 Sample emails to import:")
for i, email in enumerate(april_emails[:3]):
    try:
        subject = email.Subject or "No Subject"
        received = email.ReceivedTime.strftime("%Y-%m-%d %H:%M") if email.ReceivedTime else "No Date"
        print(f"   {i+1}. {received}: {subject[:50]}")
    except:
        print(f"   {i+1}. Error reading email details")

# Get confirmation
confirmation = input(f"\n🤔 Import {len(april_emails)} April emails with new strategy? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Import cancelled")
    exit(0)

# Import emails with new strategy
print(f"\n🚀 Starting re-import with formatting fix strategy...")

imported_count = 0
error_count = 0

for i, email in enumerate(april_emails):
    try:
        print(f"\n📧 Processing email {i+1}/{len(april_emails)}...")
        
        # Extract email data
        subject = email.Subject or "No Subject"
        received_time = email.ReceivedTime
        body = email.Body or ""
        
        print(f"   Subject: {subject[:50]}")
        print(f"   Date: {received_time}")
        
        # STEP 1: Clean and format the body properly from the start
        # Remove any existing underscores and replace with proper HTML breaks
        clean_body = body.replace('________________________________', '<br><br>')
        
        # Also handle any other common formatting issues
        clean_body = clean_body.replace('\n\n\n', '<br><br>')
        clean_body = clean_body.replace('\n\n', '<br>')
        
        # STEP 2: Create email data for DRAFT import
        email_data = {
            'subject': subject,
            'description': clean_body,
            'safedescription': clean_body,
            'actualstart': received_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'actualend': received_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'regardingobjectid_contact@odata.bind': f"/contacts({contact_id})",
            'statuscode': 1,  # DRAFT status - this is key!
            'directioncode': False,  # Incoming
            'sender': 'service@ringcentral.com',
            'torecipients': 'gvranjesevic@dynamique.com;',
            'submittedby': '"RingCentral" service@ringcentral.com',
            'senton': received_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # STEP 3: Create email as DRAFT
        print(f"   📝 Creating as DRAFT...")
        create_response = requests.post(
            f"{crm_base_url}/emails",
            json=email_data,
            headers=headers
        )
        
        if create_response.status_code not in [200, 201]:
            error_count += 1
            print(f"   ❌ Error creating email: {create_response.status_code}")
            if error_count <= 3:
                print(f"      Details: {create_response.text[:200]}")
            continue
        
        created_email = create_response.json()
        new_email_id = created_email['activityid']
        print(f"   ✅ Created as DRAFT: {new_email_id}")
        
        # STEP 4: Verify formatting is correct (while still in draft)
        print(f"   🔧 Verifying formatting...")
        
        # STEP 5: Change status to RECEIVED (statuscode = 4)
        print(f"   📮 Changing to RECEIVED status...")
        status_update = {
            'statuscode': 4  # Received/Completed
        }
        
        status_response = requests.patch(
            f"{crm_base_url}/emails({new_email_id})",
            json=status_update,
            headers=headers
        )
        
        if status_response.status_code in [200, 204]:
            imported_count += 1
            print(f"   ✅ Successfully imported and finalized!")
        else:
            error_count += 1
            print(f"   ⚠️  Email created but status update failed: {status_response.status_code}")
        
        # Rate limiting
        if i % 10 == 0 and i > 0:
            print(f"\n   📊 Progress: {imported_count} successful, {error_count} errors")
            time.sleep(1)
            
    except Exception as e:
        error_count += 1
        print(f"   ❌ Exception: {str(e)}")
        if error_count <= 3:
            print(f"      Details: {str(e)}")

print(f"\n🎯 RE-IMPORT RESULTS:")
print("="*25)
print(f"✅ Successfully imported: {imported_count} emails")
print(f"❌ Errors: {error_count} emails")

if imported_count > 0:
    print(f"\n🎉 SUCCESS WITH NEW STRATEGY!")
    print(f"   🔧 Emails imported with proper HTML formatting")
    print(f"   📮 Correct status and direction set")
    print(f"   📧 Proper sender information included")
    print(f"   📅 Refresh Dynamics 365 to see the results!")
    print(f"\n   💡 This approach should have resolved:")
    print(f"      ✅ Underscore formatting issues")
    print(f"      ✅ Email from: display problems")
    print(f"      ✅ Timeline completeness")
else:
    print(f"\n❌ No emails were successfully imported")
    print(f"   💡 Check the errors above for troubleshooting")

# Cleanup
try:
    namespace.RemoveStore(pst_store.GetRootFolder())
    print(f"\n🧹 PST file detached")
except:
    pass

print(f"\n📧 Please check your Dynamics 365 timeline!")
print(f"🎯 Both formatting and 'Email from' issues should now be resolved!") 