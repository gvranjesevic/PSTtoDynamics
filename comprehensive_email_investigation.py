#!/usr/bin/env python3
"""Comprehensive investigation of ALL fields to find what controls Email from display"""

import requests
import msal
import json

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 COMPREHENSIVE EMAIL FIELD INVESTIGATION")
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

# Get both contacts
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

# Get our problematic email (full details)
print("\n🔍 Getting our problematic April email (ALL fields)...")
our_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {service_contact['contactid']} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$top=1",
    headers=headers
)

our_email_id = our_email_response.json()['value'][0]['activityid']

# Get complete details
our_complete = requests.get(f"{crm_base_url}/emails({our_email_id})", headers=headers).json()

# Get working original email (full details)
print("🔍 Getting working original email (ALL fields)...")
original_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact['contactid']}&$top=1",
    headers=headers
)

original_email_id = original_email_response.json()['value'][0]['activityid']

# Get complete details
original_complete = requests.get(f"{crm_base_url}/emails({original_email_id})", headers=headers).json()

print(f"📧 Our email: {our_complete.get('subject', 'No Subject')[:50]}...")
print(f"📧 Working email: {original_complete.get('subject', 'No Subject')[:50]}...")

# Find ALL differences
print(f"\n📊 FINDING ALL DIFFERENCES...")
all_fields = set(our_complete.keys()) | set(original_complete.keys())
differences = []

for field in sorted(all_fields):
    our_val = our_complete.get(field)
    orig_val = original_complete.get(field)
    
    if our_val != orig_val:
        differences.append((field, our_val, orig_val))

print(f"📊 Found {len(differences)} different fields")

# Categorize differences by importance
email_related = []
address_related = []
sender_related = []
status_related = []
system_fields = []
other_fields = []

for field, our_val, orig_val in differences:
    field_lower = field.lower()
    
    # Skip obvious system fields
    if any(skip in field_lower for skip in ['createdon', 'modifiedon', 'etag', 'versionnumber']):
        system_fields.append((field, our_val, orig_val))
    elif any(keyword in field_lower for keyword in ['email', 'mail']):
        email_related.append((field, our_val, orig_val))
    elif any(keyword in field_lower for keyword in ['address', 'addr']):
        address_related.append((field, our_val, orig_val))
    elif any(keyword in field_lower for keyword in ['send', 'from', 'submit']):
        sender_related.append((field, our_val, orig_val))
    elif any(keyword in field_lower for keyword in ['status', 'state', 'code']):
        status_related.append((field, our_val, orig_val))
    else:
        other_fields.append((field, our_val, orig_val))

# Display results by category
def display_category(title, fields, max_show=10):
    if fields:
        print(f"\n🎯 {title} ({len(fields)} fields):")
        print("-" * (len(title) + 15))
        
        for i, (field, our_val, orig_val) in enumerate(fields[:max_show]):
            # Truncate long values
            our_display = str(our_val)[:100] + "..." if len(str(our_val)) > 100 else str(our_val)
            orig_display = str(orig_val)[:100] + "..." if len(str(orig_val)) > 100 else str(orig_val)
            
            print(f"\n🔍 {field}:")
            print(f"   Our:      {our_display}")
            print(f"   Working:  {orig_display}")
            
            # Check if this looks like an important field
            if field_lower := field.lower():
                if any(keyword in field_lower for keyword in ['from', 'sender']) and orig_val and not our_val:
                    print(f"   ⚠️  CRITICAL: Working email has value, ours is empty!")
                elif 'email' in field_lower and '@' in str(orig_val) and '@' not in str(our_val):
                    print(f"   ⚠️  CRITICAL: Working email has email address, ours doesn't!")

        if len(fields) > max_show:
            print(f"\n   ... and {len(fields) - max_show} more fields")

# Show most important categories first
display_category("SENDER-RELATED FIELDS", sender_related)
display_category("EMAIL-RELATED FIELDS", email_related)
display_category("ADDRESS-RELATED FIELDS", address_related)
display_category("STATUS-RELATED FIELDS", status_related)
display_category("OTHER SIGNIFICANT FIELDS", other_fields, 8)

# Look for fields that might control "Email from" specifically
print(f"\n🎯 FIELDS THAT MIGHT CONTROL 'EMAIL FROM' DISPLAY:")
print("-" * 50)

critical_fields = []
for field, our_val, orig_val in differences:
    field_lower = field.lower()
    
    # Fields that are likely to control display
    if any(keyword in field_lower for keyword in ['from', 'sender', 'submittedby']):
        critical_fields.append((field, our_val, orig_val))
    # Fields where working email has an email address but ours doesn't
    elif orig_val and '@' in str(orig_val) and (not our_val or '@' not in str(our_val)):
        critical_fields.append((field, our_val, orig_val))

if critical_fields:
    for field, our_val, orig_val in critical_fields:
        print(f"\n🚨 {field}:")
        print(f"   Our:      {our_val}")
        print(f"   Working:  {orig_val}")
        print(f"   Action:   Should try setting this field!")
else:
    print("   No obvious critical fields found...")

# Suggest next experiments
print(f"\n💡 SUGGESTED EXPERIMENTS:")
print("="*25)

experiments = []
for field, our_val, orig_val in critical_fields[:5]:  # Top 5
    if orig_val and not our_val:
        experiments.append(f"Set {field} = '{orig_val}'")
    elif our_val != orig_val:
        experiments.append(f"Change {field} from '{our_val}' to '{orig_val}'")

if experiments:
    for i, exp in enumerate(experiments, 1):
        print(f"{i}. {exp}")
        
    choice = input(f"\n🤔 Which experiment should we try? (1-{len(experiments)} or 'all'): ").strip()
    
    if choice.lower() == 'all':
        print(f"\n🔧 Trying ALL experiments on our test email...")
        
        update_data = {}
        for field, our_val, orig_val in critical_fields[:5]:
            if orig_val is not None:  # Don't set null values
                update_data[field] = orig_val
        
        if update_data:
            print(f"📝 Updating fields: {list(update_data.keys())}")
            response = requests.patch(
                f"{crm_base_url}/emails({our_email_id})",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Successfully updated {len(update_data)} fields!")
                print(f"📅 Please refresh Dynamics to check 'Email from' display!")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Details: {response.text[:300]}")
    elif choice.isdigit() and 1 <= int(choice) <= len(experiments):
        idx = int(choice) - 1
        field, our_val, orig_val = critical_fields[idx]
        
        print(f"\n🔧 Testing: {experiments[idx]}")
        update_data = {field: orig_val}
        
        response = requests.patch(
            f"{crm_base_url}/emails({our_email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ Successfully updated {field}!")
            print(f"📅 Please refresh Dynamics to check 'Email from' display!")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Details: {response.text[:300]}")
else:
    print("No obvious experiments to try...")
    print("The issue might be:")
    print("- A read-only calculated field")
    print("- System caching")
    print("- A field we haven't identified yet") 