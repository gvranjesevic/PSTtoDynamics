#!/usr/bin/env python3
"""Investigate why April 2025 emails aren't showing in timeline"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 INVESTIGATING MISSING TIMELINE EMAILS")
print("="*45)

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

# Get both RingCentral contacts
print("\n🔍 Getting RingCentral contacts...")
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')&$select=contactid,fullname,emailaddress1&$orderby=fullname", 
    headers=headers
)

contacts = contact_response.json()['value']
service_contact = None
notify_contact = None

for contact in contacts:
    if contact['emailaddress1'] == 'service@ringcentral.com':
        service_contact = contact
    elif contact['emailaddress1'] == 'notify@ringcentral.com':
        notify_contact = contact

print(f"✅ Service contact: {service_contact['fullname']} ({service_contact['contactid']})")
print(f"✅ Notify contact: {notify_contact['fullname']} ({notify_contact['contactid']})")

# Check 1: Are April emails in the system at all?
print(f"\n🔍 CHECK 1: Searching for ANY April 2025 emails...")
april_search_response = requests.get(
    f"{crm_base_url}/emails?$filter=actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$select=activityid,subject,_regardingobjectid_value,actualstart&$orderby=actualstart asc",
    headers=headers
)

if april_search_response.status_code == 200:
    april_emails = april_search_response.json().get('value', [])
    print(f"📧 Found {len(april_emails)} April 2025 emails in entire system")
    
    if len(april_emails) > 0:
        print(f"\n📝 First 5 April emails found:")
        for i, email in enumerate(april_emails[:5]):
            subject = email.get('subject', 'No Subject')[:50]
            contact_id = email.get('_regardingobjectid_value', 'No Contact')
            date = email.get('actualstart', 'No Date')
            print(f"   {i+1}. {subject}")
            print(f"      Contact: {contact_id}")
            print(f"      Date: {date}")
            
            # Check which contact this is linked to
            if contact_id == service_contact['contactid']:
                print(f"      ✅ Linked to service@ringcentral.com")
            elif contact_id == notify_contact['contactid']:
                print(f"      ⚠️  Linked to notify@ringcentral.com")
            else:
                print(f"      ❌ Linked to unknown contact")
    else:
        print(f"❌ NO April 2025 emails found in entire system!")
else:
    print(f"❌ Error searching for April emails: {april_search_response.status_code}")

# Check 2: Specifically check service@ringcentral.com contact emails
print(f"\n🔍 CHECK 2: Emails linked to service@ringcentral.com contact...")
service_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {service_contact['contactid']}&$select=activityid,subject,actualstart&$orderby=actualstart desc&$top=10",
    headers=headers
)

if service_emails_response.status_code == 200:
    service_emails = service_emails_response.json().get('value', [])
    print(f"📧 Found {len(service_emails)} total emails for service@ringcentral.com")
    
    if len(service_emails) > 0:
        print(f"\n📝 Most recent 10 emails for service@ringcentral.com:")
        for i, email in enumerate(service_emails):
            subject = email.get('subject', 'No Subject')[:50]
            date = email.get('actualstart', 'No Date')
            print(f"   {i+1}. {date}: {subject}")
    else:
        print(f"❌ NO emails found for service@ringcentral.com contact!")
else:
    print(f"❌ Error getting service contact emails: {service_emails_response.status_code}")

# Check 3: Check notify@ringcentral.com contact for comparison
print(f"\n🔍 CHECK 3: Emails linked to notify@ringcentral.com contact (for comparison)...")
notify_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact['contactid']}&$select=activityid,subject,actualstart&$orderby=actualstart desc&$top=5",
    headers=headers
)

if notify_emails_response.status_code == 200:
    notify_emails = notify_emails_response.json().get('value', [])
    print(f"📧 Found {len(notify_emails)} total emails for notify@ringcentral.com")
    
    if len(notify_emails) > 0:
        print(f"\n📝 Most recent 5 emails for notify@ringcentral.com:")
        for i, email in enumerate(notify_emails):
            subject = email.get('subject', 'No Subject')[:50]
            date = email.get('actualstart', 'No Date')
            print(f"   {i+1}. {date}: {subject}")

# Check 4: Search by subject pattern
print(f"\n🔍 CHECK 4: Searching by subject pattern...")
subject_search_response = requests.get(
    f"{crm_base_url}/emails?$filter=contains(subject,'New Text Message') and actualstart ge 2025-04-01T00:00:00Z&$select=activityid,subject,_regardingobjectid_value,actualstart&$top=10",
    headers=headers
)

if subject_search_response.status_code == 200:
    subject_emails = subject_search_response.json().get('value', [])
    print(f"📧 Found {len(subject_emails)} 'New Text Message' emails from April+")
    
    for i, email in enumerate(subject_emails):
        subject = email.get('subject', 'No Subject')[:50]
        contact_id = email.get('_regardingobjectid_value', 'No Contact')
        date = email.get('actualstart', 'No Date')
        print(f"   {i+1}. {date}: {subject}")
        print(f"      Contact: {contact_id}")

# Check 5: Check for emails with specific creation date
print(f"\n🔍 CHECK 5: Checking emails created recently...")
recent_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=createdon ge 2025-06-11T00:00:00Z&$select=activityid,subject,createdon,actualstart,_regardingobjectid_value&$orderby=createdon desc&$top=20",
    headers=headers
)

if recent_emails_response.status_code == 200:
    recent_emails = recent_emails_response.json().get('value', [])
    print(f"📧 Found {len(recent_emails)} emails created since June 11, 2025")
    
    service_count = 0
    for email in recent_emails:
        if email.get('_regardingobjectid_value') == service_contact['contactid']:
            service_count += 1
    
    print(f"📧 Of those, {service_count} are linked to service@ringcentral.com")
    
    if service_count > 0:
        print(f"\n📝 Recently created emails for service@ringcentral.com:")
        for email in recent_emails:
            if email.get('_regardingobjectid_value') == service_contact['contactid']:
                subject = email.get('subject', 'No Subject')[:50]
                created = email.get('createdon', 'No Date')
                actual_start = email.get('actualstart', 'No Date')
                print(f"   Created: {created}")
                print(f"   Actual Start: {actual_start}")
                print(f"   Subject: {subject}")
                print()

print(f"\n💭 ANALYSIS:")
print("="*15)
print("If April emails are missing from timeline, possible causes:")
print("1. Emails imported but with wrong actualstart dates")
print("2. Emails linked to wrong contact")
print("3. Emails created but not visible due to status/state")
print("4. Timeline view filtering out the emails")
print("5. System synchronization delay")
print("\nPlease check the results above to identify the issue!") 