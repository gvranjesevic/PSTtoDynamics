#!/usr/bin/env python3
"""
Clean up all test emails created during the debugging process.
This script identifies and deletes emails we created while preserving original CRM emails.
"""

import requests
import msal
from datetime import datetime, timezone

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("\n🔐 Authenticating...")
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    if "access_token" not in result:
        print(f"❌ Auth failed: {result}")
        return None
    print("✅ Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

def get_contact_id(headers, email_address):
    """Gets the contact ID for a given email address."""
    url = f"{crm_base_url}/contacts?$filter=emailaddress1 eq '{email_address}'&$select=contactid,fullname"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json().get('value'):
        contact = response.json()['value'][0]
        print(f"✅ Found Contact: {contact['fullname']} ({contact['contactid']})")
        return contact['contactid']
    return None

def find_test_emails(headers, contact_id):
    """Finds all test emails we created during debugging."""
    print("\n🔍 Searching for test emails to delete...")
    
    # Get all emails for the RingCentral contact
    url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,createdon,createdby,modifiedon&$orderby=createdon desc"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to retrieve emails: {response.text}")
        return []
    
    all_emails = response.json().get('value', [])
    print(f"📧 Found {len(all_emails)} total emails for RingCentral contact")
    
    # Define patterns for test emails we created
    test_patterns = [
        "NEW TEST",
        "FINAL TEST", 
        "MINIMAL VIABLE TEST",
        "Restored: RingCentral Voicemail from April",
        "April Email Test",
        "APRIL 2025 TEST",
        "April 2025 RingCentral Voicemail"
    ]
    
    # Find emails created today (our test emails)
    today = datetime.now(timezone.utc).date()
    
    test_emails = []
    legitimate_emails = []
    
    for email in all_emails:
        subject = email.get('subject', '')
        created_date = datetime.fromisoformat(email['createdon'].replace('Z', '+00:00')).date()
        
        # Check if this is a test email based on subject patterns or creation date
        is_test_email = False
        
        # Check subject patterns
        for pattern in test_patterns:
            if pattern in subject:
                is_test_email = True
                break
        
        # Check if created today (likely our test emails)
        if created_date == today:
            is_test_email = True
        
        if is_test_email:
            test_emails.append(email)
            print(f"   🎯 Test Email: {subject[:60]}... (Created: {email['createdon']})")
        else:
            legitimate_emails.append(email)
            print(f"   ✅ Legitimate: {subject[:60]}... (Created: {email['createdon']})")
    
    print(f"\n📊 Summary:")
    print(f"   🎯 Test emails to delete: {len(test_emails)}")
    print(f"   ✅ Legitimate emails to keep: {len(legitimate_emails)}")
    
    return test_emails

def delete_test_emails(headers, test_emails):
    """Deletes the identified test emails."""
    if not test_emails:
        print("\n✅ No test emails found to delete.")
        return
    
    print(f"\n🗑️ Deleting {len(test_emails)} test emails...")
    deleted_count = 0
    error_count = 0
    
    for i, email in enumerate(test_emails):
        email_id = email['activityid']
        subject = email.get('subject', 'No Subject')[:50]
        
        print(f"   Deleting {i+1}/{len(test_emails)}: {subject}...")
        
        delete_url = f"{crm_base_url}/emails({email_id})"
        response = requests.delete(delete_url, headers=headers)
        
        if response.status_code == 204:
            deleted_count += 1
            print(f"   ✅ Deleted successfully")
        else:
            error_count += 1
            print(f"   ❌ Failed to delete: {response.status_code} - {response.text}")
    
    print(f"\n📊 Cleanup Results:")
    print(f"   ✅ Successfully deleted: {deleted_count}")
    print(f"   ❌ Failed to delete: {error_count}")

if __name__ == "__main__":
    print("🧹 RingCentral Timeline Cleanup Tool")
    print("===================================")
    
    headers = get_auth_headers()
    if not headers:
        exit(1)
    
    contact_id = get_contact_id(headers, 'service@ringcentral.com')
    if not contact_id:
        print("❌ Could not find RingCentral contact.")
        exit(1)
    
    test_emails = find_test_emails(headers, contact_id)
    
    if test_emails:
        print(f"\n⚠️ WARNING: This will permanently delete {len(test_emails)} test emails.")
        print("   This action cannot be undone!")
        
        confirmation = input("\n🤔 Are you sure you want to proceed? (yes/no): ").lower()
        
        if confirmation == 'yes':
            delete_test_emails(headers, test_emails)
            print(f"\n🎉 Cleanup complete! The RingCentral timeline should now be much cleaner.")
        else:
            print("\n❌ Cleanup cancelled by user.")
    else:
        print("\n✅ No test emails found. Timeline is already clean!") 