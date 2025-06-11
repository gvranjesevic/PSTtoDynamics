#!/usr/bin/env python3
"""Fix RingCentral email links"""

import requests
import msal
from datetime import datetime, timedelta

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING RINGCENTRAL EMAIL LINKS")
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

# Get RingCentral contact ID
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
correct_contact_id = ringcentral_contact['contactid']
print(f"✅ RingCentral contact: {ringcentral_contact['fullname']} ({correct_contact_id})")

# Check what contact ID the emails are wrongly linked to
wrong_contact_id = "6a219814-9841-f011-a79b-000d3a9b73c6"  # From the analysis
print(f"🔍 Checking what contact {wrong_contact_id[:8]}... is...")

wrong_contact_response = requests.get(
    f"{crm_base_url}/contacts({wrong_contact_id})?$select=fullname,emailaddress1",
    headers=headers
)

if wrong_contact_response.status_code == 200:
    wrong_contact = wrong_contact_response.json()
    print(f"❌ Emails wrongly linked to: {wrong_contact.get('fullname', 'Unknown')} ({wrong_contact.get('emailaddress1', 'No Email')})")
else:
    print(f"⚠️  Could not identify wrong contact: {wrong_contact_response.status_code}")

# Get all emails that should be linked to RingCentral but aren't
print(f"\n🔍 Finding mislinked RingCentral emails...")
yesterday = datetime.now() - timedelta(hours=48)  # Extend search to 48 hours
yesterday_iso = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')

# Find RingCentral emails linked to wrong contact
mislinked_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {wrong_contact_id} and createdon ge {yesterday_iso} and contains(subject,'Text Message')&$select=activityid,subject,createdon",
    headers=headers
)

mislinked_emails = []
if mislinked_response.status_code == 200:
    mislinked_emails = mislinked_response.json().get('value', [])
    print(f"📧 Found {len(mislinked_emails)} mislinked RingCentral emails")

# Find unlinked RingCentral emails
unlinked_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq null and createdon ge {yesterday_iso} and contains(subject,'Text Message')&$select=activityid,subject,createdon",
    headers=headers
)

unlinked_emails = []
if unlinked_response.status_code == 200:
    unlinked_emails = unlinked_response.json().get('value', [])
    print(f"📧 Found {len(unlinked_emails)} unlinked RingCentral emails")

total_to_fix = len(mislinked_emails) + len(unlinked_emails)
print(f"\n🎯 Total emails to fix: {total_to_fix}")

if total_to_fix == 0:
    print("✅ No emails need fixing!")
    exit(0)

# Ask for confirmation
confirmation = input(f"\n🤔 Fix {total_to_fix} RingCentral email links? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Fix cancelled")
    exit(0)

print(f"\n🔧 Starting email link fixes...")
fixed_count = 0
error_count = 0

# Fix mislinked emails
for email in mislinked_emails:
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    print(f"🔧 Fixing: {subject}...")
    
    # Update the regarding relationship
    fix_data = {
        'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({correct_contact_id})"
    }
    
    fix_response = requests.patch(
        f"{crm_base_url}/emails({email_id})",
        json=fix_data,
        headers=headers
    )
    
    if fix_response.status_code in [200, 204]:
        print(f"   ✅ Fixed!")
        fixed_count += 1
    else:
        print(f"   ❌ Error: {fix_response.status_code}")
        error_count += 1

# Fix unlinked emails
for email in unlinked_emails:
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    print(f"🔧 Linking: {subject}...")
    
    # Set the regarding relationship
    fix_data = {
        'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({correct_contact_id})"
    }
    
    fix_response = requests.patch(
        f"{crm_base_url}/emails({email_id})",
        json=fix_data,
        headers=headers
    )
    
    if fix_response.status_code in [200, 204]:
        print(f"   ✅ Linked!")
        fixed_count += 1
    else:
        print(f"   ❌ Error: {fix_response.status_code}")
        error_count += 1

print(f"\n🎯 FIX RESULTS:")
print(f"   ✅ Fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS! Check RingCentral timeline in Dynamics 365!")
    print(f"   📧 {fixed_count} emails should now appear in RingCentral's timeline")
    print(f"   📅 These should include historical emails from before 2025-05-06")
else:
    print(f"\n⚠️  No emails were fixed. Check for other issues.") 