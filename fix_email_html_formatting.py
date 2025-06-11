#!/usr/bin/env python3
"""Fix formatting of imported service@ringcentral.com emails using HTML formatting"""

import requests
import msal
import re

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING EMAIL HTML FORMATTING")
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

# Get emails that need HTML formatting - focus on April 2025 emails
print("\n🔍 Getting April 2025 emails that need HTML formatting...")
april_start = "2025-04-01T00:00:00Z"
april_end = "2025-04-30T23:59:59Z"

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge {april_start} and actualstart le {april_end}&$select=activityid,subject,description,actualstart&$orderby=actualstart asc&$top=100",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    exit(1)

emails_to_fix = email_response.json().get('value', [])
print(f"📧 Found {len(emails_to_fix)} April emails to check for formatting")

if len(emails_to_fix) == 0:
    print("✅ No April emails found!")
    exit(0)

# Show sample before fixing
print(f"\n📝 Sample emails to fix:")
for i, email in enumerate(emails_to_fix[:3]):
    actual_start = email.get('actualstart', '')[:19]
    subject = email.get('subject', 'No Subject')[:40]
    description = email.get('description', '')[:150]
    print(f"   {i+1}. {actual_start} - {subject}")
    print(f"      Preview: {description}...")

def clean_email_html(text):
    """Clean email text by adding proper HTML formatting"""
    if not text:
        return text
    
    # First clean up any existing line breaks and extra spaces
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Look for patterns that should have line breaks and add HTML breaks
    
    # Pattern 1: "Text Message Dear MVP Info" should be "Text Message<br><br>Dear MVP Info"
    text = re.sub(r'Text Message\s+Dear\s+', 'Text Message<br><br>Dear ', text)
    
    # Pattern 2: After caution message, before "Dear"
    text = re.sub(r'safe\.\s*Text Message\s*Dear\s+', 'safe.<br><br>Text Message<br><br>Dear ', text)
    
    # Pattern 3: After "From:" add line break
    text = re.sub(r'From:\s*([^T]+)\s*To:\s*', r'From: \1<br>To: ', text)
    
    # Pattern 4: After "Received:" add line break  
    text = re.sub(r'Received:\s*([^M]+)\s*Message:\s*', r'Received: \1<br><br>Message: ', text)
    
    # Pattern 5: After "Message:" add line break
    text = re.sub(r'Message:\s*(.+?)\s*To reply using', r'Message: \1<br><br>To reply using', text)
    
    # Pattern 6: After "Thank you for using RingCentral!" add line break
    text = re.sub(r'RingCentral!\s*By subscribing', 'RingCentral!<br><br>By subscribing', text)
    
    # Pattern 7: Split long URLs onto new lines
    text = re.sub(r'(<https?://[^\s>]+)', r'<br>\1', text)
    
    return text.strip()

# Ask for confirmation
confirmation = input(f"\n🤔 Fix HTML formatting for {len(emails_to_fix)} April emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ HTML formatting fix cancelled")
    exit(0)

# Fix the formatting
print(f"\n🔧 Starting HTML formatting fixes...")
fixed_count = 0
error_count = 0

for i, email in enumerate(emails_to_fix):
    email_id = email['activityid']
    original_description = email.get('description', '')
    
    # Clean the description with HTML formatting
    cleaned_description = clean_email_html(original_description)
    
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
            if i % 10 == 0 and i > 0:  # Progress every 10 emails
                print(f"   ✅ Fixed {fixed_count} emails so far...")
        else:
            error_count += 1
            if error_count <= 3:
                print(f"   ❌ Error fixing email {i+1}: {response.status_code}")
    else:
        # No changes needed
        print(f"📝 Email {i+1} already properly formatted")

print(f"\n🎯 HTML FORMATTING RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📧 {fixed_count} emails now have proper HTML formatting")
    print(f"   📅 Refresh Dynamics 365 to see improved readability")
    print(f"   🔍 Text should now have proper line breaks using HTML <br> tags")
    
    # Show a sample of what was fixed
    if emails_to_fix:
        sample_email = emails_to_fix[0]
        original_desc = sample_email.get('description', '')[:200]
        cleaned_desc = clean_email_html(original_desc)[:200]
        
        print(f"\n📝 Example HTML fix:")
        print(f"   Before: {original_desc}...")
        print(f"   After:  {cleaned_desc}...")
else:
    print(f"\n⚠️  No emails were updated.")
    print(f"   💡 The formatting might already be correct.") 