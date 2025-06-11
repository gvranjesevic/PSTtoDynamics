#!/usr/bin/env python3
"""Search for existing April emails and link them to RingCentral"""

import requests
import msal
from datetime import datetime

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 SEARCHING FOR EXISTING APRIL EMAILS TO LINK")
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

# Get RingCentral contact
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

# Search for April 2025 emails that might be unlinked
print("\n🔍 Searching for April 2025 emails in CRM...")

# Look for emails with RingCentral-like subjects from April 2025
april_start = "2025-04-01T00:00:00Z"
april_end = "2025-04-30T23:59:59Z"

# Search patterns for RingCentral emails
search_queries = [
    f"$filter=createdon ge {april_start} and createdon le {april_end} and contains(subject,'Text Message')",
    f"$filter=createdon ge {april_start} and createdon le {april_end} and contains(subject,'Voice Message')", 
    f"$filter=createdon ge {april_start} and createdon le {april_end} and contains(subject,'RingCentral')",
    f"$filter=actualstart ge {april_start} and actualstart le {april_end} and contains(subject,'Text Message')"
]

all_april_emails = []

for i, query in enumerate(search_queries):
    print(f"   📧 Search {i+1}/4...")
    response = requests.get(
        f"{crm_base_url}/emails?{query}&$select=activityid,subject,createdon,actualstart,_regardingobjectid_value&$top=200",
        headers=headers
    )
    
    if response.status_code == 200:
        emails = response.json().get('value', [])
        for email in emails:
            # Avoid duplicates
            if not any(e['activityid'] == email['activityid'] for e in all_april_emails):
                all_april_emails.append(email)

print(f"📧 Found {len(all_april_emails)} total April emails in CRM")

# Categorize emails
linked_to_ringcentral = []
unlinked_emails = []
linked_to_others = []

for email in all_april_emails:
    regarding_id = email.get('_regardingobjectid_value')
    
    if regarding_id == contact_id:
        linked_to_ringcentral.append(email)
    elif regarding_id is None:
        unlinked_emails.append(email)
    else:
        linked_to_others.append(email)

print(f"\n📊 April Email Categorization:")
print(f"   ✅ Already linked to RingCentral: {len(linked_to_ringcentral)}")
print(f"   ❌ Unlinked: {len(unlinked_emails)}")
print(f"   🔀 Linked to other contacts: {len(linked_to_others)}")

# Focus on unlinked RingCentral emails
ringcentral_unlinked = []
for email in unlinked_emails:
    subject = email.get('subject', '').lower()
    if 'text message' in subject or 'voice message' in subject or 'ringcentral' in subject:
        ringcentral_unlinked.append(email)

print(f"\n🎯 Unlinked RingCentral-like emails: {len(ringcentral_unlinked)}")

if ringcentral_unlinked:
    print("📅 Sample unlinked RingCentral emails:")
    for i, email in enumerate(ringcentral_unlinked[:5]):
        created = email.get('createdon', '')[:19]
        actual = email.get('actualstart', '')[:19] if email.get('actualstart') else 'No Date'
        subject = email.get('subject', 'No Subject')[:50]
        print(f"   {i+1}. Created: {created} | Actual: {actual} | {subject}")

# Check emails linked to wrong contacts
wrong_contact_ringcentral = []
for email in linked_to_others:
    subject = email.get('subject', '').lower()
    if 'text message' in subject or 'voice message' in subject:
        wrong_contact_ringcentral.append(email)

print(f"\n🔀 RingCentral emails linked to wrong contacts: {len(wrong_contact_ringcentral)}")

if wrong_contact_ringcentral:
    print("📅 Sample mislinked RingCentral emails:")
    for i, email in enumerate(wrong_contact_ringcentral[:5]):
        created = email.get('createdon', '')[:19]
        subject = email.get('subject', 'No Subject')[:50]
        regarding_id = email.get('_regardingobjectid_value', '')[:8]
        print(f"   {i+1}. {created} | Linked to: {regarding_id}... | {subject}")

# Total emails to fix
total_to_fix = len(ringcentral_unlinked) + len(wrong_contact_ringcentral)

if total_to_fix == 0:
    print("\n✅ No April emails need linking!")
    print("💡 The 71 April emails from PST might not have been imported yet.")
    print("   - Try re-running the timeline restoration system")
    print("   - Or check if contact matching logic needs improvement")
    exit(0)

print(f"\n🎯 Total April emails to link to RingCentral: {total_to_fix}")

# Ask for confirmation
confirmation = input(f"\n🤔 Link {total_to_fix} April emails to RingCentral? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Linking cancelled")
    exit(0)

# Fix the links
print(f"\n🔧 Starting to link emails...")
fixed_count = 0
error_count = 0

# Fix unlinked emails
for email in ringcentral_unlinked:
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    print(f"🔧 Linking: {subject}...")
    
    fix_data = {
        'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({contact_id})"
    }
    
    response = requests.patch(
        f"{crm_base_url}/emails({email_id})",
        json=fix_data,
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Linked!")
        fixed_count += 1
    else:
        print(f"   ❌ Error: {response.status_code}")
        error_count += 1

# Fix mislinked emails
for email in wrong_contact_ringcentral:
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    print(f"🔧 Re-linking: {subject}...")
    
    fix_data = {
        'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({contact_id})"
    }
    
    response = requests.patch(
        f"{crm_base_url}/emails({email_id})",
        json=fix_data,
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Re-linked!")
        fixed_count += 1
    else:
        print(f"   ❌ Error: {response.status_code}")
        error_count += 1

print(f"\n🎯 LINKING RESULTS:")
print(f"   ✅ Successfully linked: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📧 {fixed_count} April emails now linked to RingCentral")
    print(f"   📅 Check Dynamics 365 RingCentral timeline for April emails!")
else:
    print(f"\n⚠️  No emails were linked.")
    print(f"   💡 The April emails might need to be imported from PST first.") 