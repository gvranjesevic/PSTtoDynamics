#!/usr/bin/env python3
"""Fix formatting of imported service@ringcentral.com emails"""

import requests
import msal
import re

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING EMAIL FORMATTING")
print("="*40)

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

# Get the service@ringcentral.com contact
print("🔍 Getting service@ringcentral.com contact...")
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

if contact_response.status_code != 200:
    print(f"❌ Error getting contact: {contact_response.status_code}")
    exit(1)

contacts = contact_response.json().get('value', [])
if not contacts:
    print("❌ service@ringcentral.com contact not found")
    exit(1)

contact = contacts[0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get emails for this contact that might have formatting issues
print("\n🔍 Getting emails with formatting issues...")
email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and contains(description,'___')&$select=activityid,subject,description,createdon&$orderby=createdon desc&$top=100",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    exit(1)

emails_to_fix = email_response.json().get('value', [])
print(f"📧 Found {len(emails_to_fix)} emails with formatting issues")

if len(emails_to_fix) == 0:
    print("✅ No emails need formatting fixes!")
    exit(0)

# Show sample before fixing
print(f"\n📝 Sample emails to fix:")
for i, email in enumerate(emails_to_fix[:3]):
    created = email.get('createdon', '')[:19]
    subject = email.get('subject', 'No Subject')[:40]
    description = email.get('description', '')[:100]
    print(f"   {i+1}. {created} - {subject}")
    print(f"      Preview: {description}...")

# Ask for confirmation
confirmation = input(f"\n🤔 Fix formatting for {len(emails_to_fix)} emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Formatting fix cancelled")
    exit(0)

# Fix the formatting
print(f"\n🔧 Starting formatting fixes...")
fixed_count = 0
error_count = 0

def clean_email_text(text):
    """Clean email text by replacing underscores with proper formatting"""
    if not text:
        return text
    
    # Replace long sequences of underscores with double line breaks
    text = re.sub(r'_{10,}', '\n\n', text)
    
    # Replace medium sequences of underscores with single line breaks  
    text = re.sub(r'_{5,9}', '\n', text)
    
    # Replace shorter sequences with space
    text = re.sub(r'_{2,4}', ' ', text)
    
    # Clean up multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up spaces around newlines
    text = re.sub(r' *\n *', '\n', text)
    
    return text.strip()

for i, email in enumerate(emails_to_fix):
    email_id = email['activityid']
    original_description = email.get('description', '')
    
    # Clean the description
    cleaned_description = clean_email_text(original_description)
    
    if cleaned_description != original_description:
        print(f"🔧 Fixing email {i+1}/{len(emails_to_fix)}...")
        
        # Update the email
        update_data = {
            'description': cleaned_description
        }
        
        response = requests.patch(
            f"{crm_base_url}/emails({email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            fixed_count += 1
            if i % 10 == 0:  # Progress every 10 emails
                print(f"   ✅ Fixed {fixed_count} emails so far...")
        else:
            error_count += 1
            if error_count <= 3:
                print(f"   ❌ Error fixing email {i+1}: {response.status_code}")
    else:
        # No changes needed
        pass

print(f"\n🎯 FORMATTING RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📧 {fixed_count} emails now have proper formatting")
    print(f"   📅 Refresh Dynamics 365 to see improved readability")
    print(f"   🔍 Underscores should now be replaced with line breaks")
    
    # Show a sample of what was fixed
    if emails_to_fix:
        sample_email = emails_to_fix[0]
        original_desc = sample_email.get('description', '')[:200]
        cleaned_desc = clean_email_text(original_desc)[:200]
        
        print(f"\n📝 Example fix:")
        print(f"   Before: {original_desc}...")
        print(f"   After:  {cleaned_desc}...")
else:
    print(f"\n⚠️  No emails were updated.")
    print(f"   💡 The formatting might already be correct.") 