#!/usr/bin/env python3
"""Identify and delete only the emails we imported, preserving original Dynamics emails"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🗑️  IDENTIFYING AND DELETING IMPORTED EMAILS")
print("="*50)
print("Target: Emails we created on June 11, 2025")
print("Preserve: Original Dynamics emails")
print("="*50)

# Authenticate
print("\n🔐 Authenticating...")
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

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Find emails created on June 11, 2025 (our import date)
print(f"\n🔍 Finding emails created on June 11, 2025...")
june_11_start = "2025-06-11T00:00:00Z"
june_11_end = "2025-06-11T23:59:59Z"

imported_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and createdon ge {june_11_start} and createdon le {june_11_end}&$select=activityid,subject,createdon,actualstart&$orderby=actualstart asc",
    headers=headers
)

if imported_emails_response.status_code != 200:
    print(f"❌ Error getting imported emails: {imported_emails_response.status_code}")
    exit(1)

imported_emails = imported_emails_response.json().get('value', [])
print(f"📧 Found {len(imported_emails)} emails created on June 11, 2025")

if len(imported_emails) == 0:
    print("✅ No imported emails found to delete!")
    exit(0)

# Analyze what we found
april_emails = []
other_emails = []

for email in imported_emails:
    actual_start = email.get('actualstart', '')
    if actual_start and '2025-04-' in actual_start:
        april_emails.append(email)
    else:
        other_emails.append(email)

print(f"\n📊 ANALYSIS:")
print(f"   📧 Total emails created June 11: {len(imported_emails)}")
print(f"   📅 April 2025 emails (our imports): {len(april_emails)}")
print(f"   📅 Non-April emails: {len(other_emails)}")

# Show samples
if len(april_emails) > 0:
    print(f"\n📝 Sample April emails to delete:")
    for i, email in enumerate(april_emails[:5]):
        subject = email.get('subject', 'No Subject')[:50]
        actual_start = email.get('actualstart', 'No Date')
        created = email.get('createdon', 'No Date')
        print(f"   {i+1}. {actual_start}: {subject}")
        print(f"      Created: {created}")

if len(other_emails) > 0:
    print(f"\n⚠️  Non-April emails found (will NOT delete):")
    for i, email in enumerate(other_emails[:3]):
        subject = email.get('subject', 'No Subject')[:50]
        actual_start = email.get('actualstart', 'No Date')
        print(f"   {i+1}. {actual_start}: {subject}")

# Get confirmation
if len(april_emails) == 0:
    print("✅ No April emails found to delete!")
    exit(0)

print(f"\n🤔 DELETION PLAN:")
print(f"   🗑️  DELETE: {len(april_emails)} April 2025 emails (our imports)")
print(f"   ✅ PRESERVE: {len(other_emails)} non-April emails")
print(f"   💡 This will clear our imported emails for re-import")

confirmation = input(f"\n🚨 Proceed with deleting {len(april_emails)} imported April emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Deletion cancelled")
    exit(0)

# Delete the April emails
print(f"\n🗑️  Deleting {len(april_emails)} April emails...")

deleted_count = 0
error_count = 0

for i, email in enumerate(april_emails):
    email_id = email['activityid']
    subject = email.get('subject', 'No Subject')[:30]
    
    try:
        response = requests.delete(
            f"{crm_base_url}/emails({email_id})",
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            deleted_count += 1
            if (i + 1) % 10 == 0:
                print(f"   🗑️  Deleted {i + 1}/{len(april_emails)} emails...")
        else:
            error_count += 1
            if error_count <= 3:
                print(f"   ❌ Error deleting {subject}: {response.status_code}")
                
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"   ❌ Exception deleting {subject}: {str(e)}")

print(f"\n🎯 DELETION RESULTS:")
print(f"   🗑️  Successfully deleted: {deleted_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if deleted_count > 0:
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"   📧 {deleted_count} imported April emails removed")
    print(f"   ✅ Original Dynamics emails preserved")
    print(f"   🚀 Ready for fresh re-import with proper formatting!")
    print(f"\n💡 Next steps:")
    print(f"   1. Re-import April emails as DRAFT status")
    print(f"   2. Fix formatting while in draft")
    print(f"   3. Change to received status")
    print(f"   4. This should resolve both formatting and 'Email from' issues")
else:
    print(f"\n⚠️  No emails were deleted")
    print(f"   💡 Either they were already deleted or there were permission issues")

print(f"\n📅 Please refresh Dynamics 365 to confirm the cleanup!") 