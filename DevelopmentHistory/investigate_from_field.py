#!/usr/bin/env python3
"""Deep investigation to find the exact field controlling Email from display"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 INVESTIGATING EMAIL FROM FIELD")
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

# Get both RingCentral contacts
print("\n🔍 Getting both RingCentral contacts...")
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

# Get one of our imported April emails
print("\n🔍 Getting our imported April email...")
our_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {service_contact['contactid']} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$top=1",
    headers=headers
)

our_email = our_email_response.json()['value'][0]
our_email_id = our_email['activityid']

# Get a working original email from notify contact
print("🔍 Getting original working email...")
original_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact['contactid']}&$top=1",
    headers=headers
)

original_email = original_email_response.json()['value'][0]
original_email_id = original_email['activityid']

# Get complete details for both emails
print("\n🔍 Getting complete email details...")

our_complete_response = requests.get(f"{crm_base_url}/emails({our_email_id})", headers=headers)
original_complete_response = requests.get(f"{crm_base_url}/emails({original_email_id})", headers=headers)

our_data = our_complete_response.json()
original_data = original_complete_response.json()

# Find all fields that are different
print(f"\n📊 FIELD-BY-FIELD COMPARISON:")
print("="*50)

all_fields = set(our_data.keys()) | set(original_data.keys())

sender_related_differences = []
all_differences = []

for field in sorted(all_fields):
    our_value = our_data.get(field, 'MISSING')
    original_value = original_data.get(field, 'MISSING')
    
    if our_value != original_value:
        all_differences.append((field, our_value, original_value))
        
        # Check if this could be sender-related
        if any(keyword in field.lower() for keyword in ['from', 'send', 'email', 'address']):
            sender_related_differences.append((field, our_value, original_value))

print(f"📧 SENDER-RELATED DIFFERENCES:")
print("-" * 35)
for field, our_val, orig_val in sender_related_differences:
    # Truncate long values
    our_display = str(our_val)[:100] + "..." if len(str(our_val)) > 100 else str(our_val)
    orig_display = str(orig_val)[:100] + "..." if len(str(orig_val)) > 100 else str(orig_val)
    
    print(f"\n🔍 {field}:")
    print(f"   Our email:  {our_display}")
    print(f"   Original:   {orig_display}")

print(f"\n📊 ALL SIGNIFICANT DIFFERENCES:")
print("-" * 35)

# Show only the most relevant differences (exclude timestamps and IDs)
relevant_differences = []
for field, our_val, orig_val in all_differences:
    # Skip system fields that wouldn't affect display
    if not any(skip in field.lower() for skip in ['createdon', 'modifiedon', 'activityid', 'etag', 'ownerid', '_value']):
        relevant_differences.append((field, our_val, orig_val))

for field, our_val, orig_val in relevant_differences[:15]:  # Show top 15
    our_display = str(our_val)[:80] + "..." if len(str(our_val)) > 80 else str(our_val)
    orig_display = str(orig_val)[:80] + "..." if len(str(orig_val)) > 80 else str(orig_val)
    
    print(f"\n🔍 {field}:")
    print(f"   Ours:     {our_display}")
    print(f"   Original: {orig_display}")

# Now let's try to find the specific field by checking common email from fields
print(f"\n🎯 TESTING SPECIFIC EMAIL FROM FIELDS:")
print("-" * 40)

email_from_fields = [
    'from',
    'sender', 
    'emailfrom',
    'fromaddress',
    'senderaddress',
    'senderemailaddress',
    'fromemail'
]

for field in email_from_fields:
    our_val = our_data.get(field, 'NOT_FOUND')
    orig_val = original_data.get(field, 'NOT_FOUND')
    print(f"{field}: Our='{our_val}' | Original='{orig_val}'")

print(f"\n💡 NEXT STEPS:")
print("="*15)
print("1. Look for fields where Original has an email address but Ours doesn't")
print("2. Try updating those specific fields")
print("3. The field controlling 'Email from:' display should be identifiable above")
print("4. Focus on fields that contain email addresses in the Original column") 