#!/usr/bin/env python3
"""Detailed analysis for service@ringcentral.com emails"""

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

print("🔍 SERVICE@RINGCENTRAL.COM DETAILED ANALYSIS")
print("="*60)

# 1. Analyze PST emails specifically for service@ringcentral.com
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

def search_folder_for_service_ringcentral(folder, emails):
    """Search folder specifically for service@ringcentral.com emails"""
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
                    
                    # Check specifically for service@ringcentral.com
                    service_ringcentral_involved = False
                    
                    if 'service@ringcentral.com' in sender.lower():
                        service_ringcentral_involved = True
                    
                    for rec in recipients:
                        if 'service@ringcentral.com' in rec.lower():
                            service_ringcentral_involved = True
                            break
                    
                    if service_ringcentral_involved:
                        received_time = getattr(message, 'ReceivedTime', None)
                        sent_time = getattr(message, 'SentOn', None)
                        creation_time = getattr(message, 'CreationTime', None)
                        
                        email_data = {
                            'subject': getattr(message, 'Subject', '') or 'No Subject',
                            'sender': sender,
                            'recipients': recipients,
                            'received_time': received_time,
                            'sent_time': sent_time,
                            'creation_time': creation_time,
                            'date_for_sort': sent_time or received_time or creation_time,
                            'body': getattr(message, 'Body', '')[:200] or ''  # First 200 chars
                        }
                        emails.append(email_data)
            except:
                continue
        
        # Search subfolders
        try:
            for subfolder in folder.Folders:
                search_folder_for_service_ringcentral(subfolder, emails)
        except:
            pass
    except:
        pass

print("🔍 Searching specifically for service@ringcentral.com emails...")
service_emails = []
root_folder = pst_store.GetRootFolder()
search_folder_for_service_ringcentral(root_folder, service_emails)

print(f"📧 Found {len(service_emails)} service@ringcentral.com emails in PST")

if len(service_emails) == 0:
    print("❌ No service@ringcentral.com emails found in PST!")
    print("🔍 Let's check for other RingCentral patterns...")
    exit(1)

# Sort by date
service_emails.sort(key=lambda x: x['date_for_sort'] or '', reverse=True)

# Group by month for analysis
monthly_counts = defaultdict(int)
emails_by_month = defaultdict(list)

print("\n📅 Service@RingCentral.com Emails by Month:")
print("-" * 50)

for email in service_emails:
    email_date = email['date_for_sort']
    if email_date:
        month_key = email_date.strftime('%Y-%m')
        monthly_counts[month_key] += 1
        emails_by_month[month_key].append(email)

# Show monthly breakdown
for month in sorted(monthly_counts.keys()):
    count = monthly_counts[month]
    print(f"   {month}: {count} emails")

# Focus on April 2025 (4th month)
april_emails = emails_by_month.get('2025-04', [])
print(f"\n🎯 APRIL 2025 EMAILS: {len(april_emails)}")

if april_emails:
    print("📅 April 2025 service@ringcentral.com emails:")
    for i, email in enumerate(april_emails[:10]):
        date_str = email['date_for_sort'].strftime('%Y-%m-%d %H:%M') if email['date_for_sort'] else 'No Date'
        subject = email['subject'][:60]
        print(f"   {i+1:2d}. {date_str} - {subject}")
        if i == 0:  # Show first email body sample
            print(f"       Body sample: {email['body'][:100]}...")

# 2. Check what's in CRM for service@ringcentral.com
print(f"\n🔐 Checking CRM for service@ringcentral.com emails...")

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

# Get RingCentral contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')&$select=contactid,fullname,emailaddress1", 
    headers=headers
)

if contact_response.status_code == 200:
    contacts = contact_response.json().get('value', [])
    if contacts:
        contact = contacts[0]
        contact_id = contact['contactid']
        print(f"✅ RingCentral contact: {contact['fullname']} ({contact_id})")
        
        # Get all emails for RingCentral contact
        email_response = requests.get(
            f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$orderby=actualstart desc&$select=subject,actualstart,actualend,description",
            headers=headers
        )
        
        if email_response.status_code == 200:
            crm_emails = email_response.json().get('value', [])
            print(f"📧 Total emails in CRM for RingCentral: {len(crm_emails)}")
            
            # Check for April emails in CRM
            april_crm_emails = []
            crm_monthly_counts = defaultdict(int)
            
            for email in crm_emails:
                actual_start = email.get('actualstart')
                if actual_start:
                    try:
                        date_obj = datetime.fromisoformat(actual_start.replace('Z', '+00:00'))
                        month_key = date_obj.strftime('%Y-%m')
                        crm_monthly_counts[month_key] += 1
                        
                        if month_key == '2025-04':
                            april_crm_emails.append(email)
                    except:
                        pass
            
            print(f"\n📊 CRM Emails by Month:")
            for month in sorted(crm_monthly_counts.keys()):
                count = crm_monthly_counts[month]
                print(f"   {month}: {count} emails")
            
            print(f"\n🎯 APRIL 2025 IN CRM: {len(april_crm_emails)} emails")
            
            if april_crm_emails:
                print("📅 April 2025 emails in CRM:")
                for i, email in enumerate(april_crm_emails[:5]):
                    actual_start = email.get('actualstart', '')[:19]
                    subject = email.get('subject', 'No Subject')[:50]
                    print(f"   {i+1}. {actual_start} - {subject}")

# 3. Check for unlinked emails that might be April service@ringcentral.com
print(f"\n🔍 Checking for unlinked service@ringcentral.com emails...")

# Search for emails with service@ringcentral subjects
unlinked_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq null and (contains(subject,'service@ringcentral') or contains(subject,'RingCentral') or contains(subject,'Text Message'))&$select=activityid,subject,createdon,actualstart&$orderby=createdon desc&$top=100",
    headers=headers
)

if unlinked_response.status_code == 200:
    unlinked_emails = unlinked_response.json().get('value', [])
    print(f"📧 Found {len(unlinked_emails)} potentially unlinked RingCentral emails")
    
    april_unlinked = []
    for email in unlinked_emails:
        actual_start = email.get('actualstart')
        if actual_start:
            try:
                date_obj = datetime.fromisoformat(actual_start.replace('Z', '+00:00'))
                if date_obj.strftime('%Y-%m') == '2025-04':
                    april_unlinked.append(email)
            except:
                pass
    
    print(f"🎯 April unlinked emails: {len(april_unlinked)}")
    
    if april_unlinked:
        print("📅 April unlinked emails:")
        for i, email in enumerate(april_unlinked[:5]):
            actual_start = email.get('actualstart', '')[:19] 
            subject = email.get('subject', 'No Subject')[:50]
            print(f"   {i+1}. {actual_start} - {subject}")

print(f"\n🎯 ANALYSIS SUMMARY:")
print(f"   📧 PST April service@ringcentral.com emails: {len(april_emails)}")
print(f"   📧 CRM April RingCentral emails: {len(april_crm_emails) if 'april_crm_emails' in locals() else 0}")
print(f"   📧 April unlinked emails: {len(april_unlinked) if 'april_unlinked' in locals() else 0}")

if len(april_emails) > 0:
    missing_count = len(april_emails) - len(april_crm_emails) if 'april_crm_emails' in locals() else len(april_emails)
    print(f"   ⚠️  Missing from timeline: {missing_count} emails")
    
    if missing_count > 0:
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Check if April emails were imported but not linked")
        print(f"   2. Re-import missing April service@ringcentral.com emails")
        print(f"   3. Fix contact matching logic")

# Close PST
try:
    namespace.RemoveStore(pst_store.StoreID)
except:
    pass 