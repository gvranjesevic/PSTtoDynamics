#!/usr/bin/env python3
"""Debug contact matching for RingCentral"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 DEBUGGING CONTACT MATCHING FOR RINGCENTRAL")
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

# Get all contacts with RingCentral in name or email
print("\n🔍 Getting all RingCentral-related contacts...")
response = requests.get(
    f"{crm_base_url}/contacts?$filter=contains(fullname,'RingCentral') or contains(emailaddress1,'ringcentral')&$select=contactid,fullname,emailaddress1,emailaddress2,emailaddress3", 
    headers=headers
)

if response.status_code == 200:
    contacts = response.json().get('value', [])
    print(f"📧 Found {len(contacts)} RingCentral contacts:")
    
    for i, contact in enumerate(contacts):
        print(f"\n   Contact {i+1}:")
        print(f"     🆔 ID: {contact.get('contactid', 'N/A')}")
        print(f"     👤 Name: {contact.get('fullname', 'N/A')}")
        print(f"     📧 Email1: {contact.get('emailaddress1', 'N/A')}")
        print(f"     📧 Email2: {contact.get('emailaddress2', 'N/A') or 'None'}")
        print(f"     📧 Email3: {contact.get('emailaddress3', 'N/A') or 'None'}")
    
    # Test contact matching logic
    print(f"\n🧪 TESTING CONTACT MATCHING LOGIC:")
    print("-" * 30)
    
    for contact in contacts:
        contact_email = contact.get('emailaddress1', '')
        print(f"\n📧 Testing contact: {contact.get('fullname', 'Unknown')}")
        print(f"   Contact email: '{contact_email}'")
        
        # Simulate the search logic
        test_senders = [
            'service@ringcentral.com',
            'SERVICE@RINGCENTRAL.COM',
            'noreply@ringcentral.com',
            'notifications@ringcentral.com'
        ]
        
        for sender in test_senders:
            match_result = contact_email.lower() in sender.lower() if contact_email else False
            print(f"   Test: '{contact_email}' in '{sender}' = {match_result}")
        
        # Also test reverse matching (more likely to work)
        print(f"   Reverse tests:")
        for sender in test_senders:
            reverse_match = sender.lower() in contact_email.lower() if contact_email else False
            domain_match = 'ringcentral.com' in contact_email.lower() if contact_email else False
            print(f"   '{sender}' in '{contact_email}' = {reverse_match}")
            print(f"   'ringcentral.com' in '{contact_email}' = {domain_match}")
            
        # Test substring matching
        print(f"   Domain matching:")
        if contact_email:
            has_ringcentral = 'ringcentral' in contact_email.lower()
            print(f"   Contains 'ringcentral' = {has_ringcentral}")

else:
    print(f"❌ Error getting contacts: {response.status_code}")

print(f"\n💡 ANALYSIS:")
print(f"   The timeline restoration system uses 'contact_email' to search PST emails")
print(f"   If the contact_email value is wrong, it won't find matching emails")
print(f"   The search logic: 'contact_email.lower() in sender.lower()'")
print(f"   For service@ringcentral.com emails, the contact needs the right email value") 