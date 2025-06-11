#!/usr/bin/env python3
"""Check RingCentral email dates in PST vs CRM"""

import win32com.client
import requests
import msal
from datetime import datetime
from collections import defaultdict

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77" 
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"

print("🔍 RINGCENTRAL EMAIL DATE ANALYSIS")
print("="*60)

# 1. Check PST emails for RingCentral
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

def search_folder_for_ringcentral(folder, emails):
    """Search folder for RingCentral emails"""
    try:
        for message in folder.Items:
            try:
                if message.Class == 43:  # olMail
                    sender = getattr(message, 'SenderEmailAddress', '') or ''
                    recipients = []
                    
                    try:
                        for recipient in message.Recipients:
                            rec_email = getattr(recipient, 'Address', '') or ''
                            recipients.append(rec_email)
                    except:
                        pass
                    
                    # Check if RingCentral is involved
                    ringcentral_involved = False
                    if 'ringcentral.com' in sender.lower():
                        ringcentral_involved = True
                    
                    for rec in recipients:
                        if 'ringcentral.com' in rec.lower():
                            ringcentral_involved = True
                            break
                    
                    if ringcentral_involved:
                        received_time = getattr(message, 'ReceivedTime', None)
                        sent_time = getattr(message, 'SentOn', None)
                        creation_time = getattr(message, 'CreationTime', None)
                        last_mod_time = getattr(message, 'LastModificationTime', None)
                        
                        email_data = {
                            'subject': getattr(message, 'Subject', '') or 'No Subject',
                            'sender': sender,
                            'recipients': recipients,
                            'received_time': received_time,
                            'sent_time': sent_time,
                            'creation_time': creation_time,
                            'last_mod_time': last_mod_time,
                            'date_for_sort': sent_time or received_time or creation_time
                        }
                        emails.append(email_data)
            except:
                continue
        
        # Search subfolders
        try:
            for subfolder in folder.Folders:
                search_folder_for_ringcentral(subfolder, emails)
        except:
            pass
    except:
        pass

print("🔍 Searching for RingCentral emails in PST...")
ringcentral_emails = []
root_folder = pst_store.GetRootFolder()
search_folder_for_ringcentral(root_folder, ringcentral_emails)

print(f"📧 Found {len(ringcentral_emails)} RingCentral emails in PST")

# Sort by date
ringcentral_emails.sort(key=lambda x: x['date_for_sort'] or '', reverse=True)

# Group by month/year for analysis
date_groups = defaultdict(int)
earliest_date = None
latest_date = None

print("\n📅 RingCentral Email Dates in PST:")
print("-" * 40)

for i, email in enumerate(ringcentral_emails[:50]):  # Show first 50
    email_date = email['date_for_sort']
    if email_date:
        date_str = email_date.strftime('%Y-%m-%d %H:%M')
        month_key = email_date.strftime('%Y-%m')
        date_groups[month_key] += 1
        
        if not earliest_date or email_date < earliest_date:
            earliest_date = email_date
        if not latest_date or email_date > latest_date:
            latest_date = email_date
    else:
        date_str = 'No Date'
    
    print(f"{i+1:2d}. {date_str} - {email['subject'][:50]}")

print(f"\n📊 Date Range Summary:")
if earliest_date and latest_date:
    print(f"   📅 Earliest: {earliest_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   📅 Latest: {latest_date.strftime('%Y-%m-%d %H:%M')}")

print(f"\n📊 Emails by Month:")
for month in sorted(date_groups.keys()):
    print(f"   {month}: {date_groups[month]} emails")

# Check if there are emails before 2025-05-06
from datetime import timezone
cutoff_date = datetime(2025, 5, 6, tzinfo=timezone.utc)
emails_before_cutoff = []
for email in ringcentral_emails:
    email_date = email['date_for_sort']
    if email_date:
        # Make timezone-aware if needed
        if email_date.tzinfo is None:
            email_date = email_date.replace(tzinfo=timezone.utc)
        if email_date < cutoff_date:
            emails_before_cutoff.append(email)

print(f"\n🔍 Emails BEFORE 2025-05-06:")
print(f"   📧 Count: {len(emails_before_cutoff)}")

if emails_before_cutoff:
    print("   📅 Sample dates:")
    for email in emails_before_cutoff[:10]:
        date_str = email['date_for_sort'].strftime('%Y-%m-%d %H:%M')
        print(f"     • {date_str} - {email['subject'][:40]}")

# 2. Now check what's actually in CRM
print(f"\n🔐 Checking CRM for RingCentral emails...")

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

# Find RingCentral contact
print("🔍 Finding RingCentral contact in CRM...")
response = requests.get(f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')", headers=headers)

if response.status_code == 200:
    contacts = response.json().get('value', [])
    if contacts:
        ringcentral_contact = contacts[0]
        contact_id = ringcentral_contact['contactid']
        contact_name = ringcentral_contact.get('fullname', 'Unknown')
        print(f"✅ Found contact: {contact_name} ({contact_id})")
        
        # Get emails for this contact
        print("📧 Getting emails from CRM...")
        email_response = requests.get(
            f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$orderby=actualstart desc&$top=50&$select=subject,actualstart,actualend,description",
            headers=headers
        )
        
        if email_response.status_code == 200:
            crm_emails = email_response.json().get('value', [])
            print(f"📧 Found {len(crm_emails)} emails in CRM")
            
            if crm_emails:
                print("\n📅 CRM Email Dates:")
                print("-" * 30)
                crm_earliest = None
                crm_latest = None
                
                for i, email in enumerate(crm_emails[:15]):
                    actual_start = email.get('actualstart')
                    if actual_start:
                        # Parse ISO date
                        try:
                            date_obj = datetime.fromisoformat(actual_start.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                            
                            if not crm_earliest or date_obj < crm_earliest:
                                crm_earliest = date_obj
                            if not crm_latest or date_obj > crm_latest:
                                crm_latest = date_obj
                        except:
                            date_str = actual_start
                    else:
                        date_str = 'No Date'
                    
                    subject = email.get('subject', 'No Subject')[:40]
                    print(f"{i+1:2d}. {date_str} - {subject}")
                
                if crm_earliest and crm_latest:
                    print(f"\n📊 CRM Date Range:")
                    print(f"   📅 Earliest: {crm_earliest.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   📅 Latest: {crm_latest.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("❌ No emails found in CRM")
        else:
            print(f"❌ Error getting CRM emails: {email_response.status_code}")
    else:
        print("❌ RingCentral contact not found in CRM")
else:
    print(f"❌ Error searching contacts: {response.status_code}")

print(f"\n🎯 CONCLUSION:")
print(f"   📧 PST has {len(ringcentral_emails)} RingCentral emails")
print(f"   📧 Emails before 2025-05-06: {len(emails_before_cutoff)}")
if earliest_date:
    print(f"   📅 PST earliest date: {earliest_date.strftime('%Y-%m-%d')}")
print(f"   🔍 Check if these older emails were imported with correct dates!")

# Close PST
try:
    namespace.RemoveStore(pst_store.StoreID)
except:
    pass 