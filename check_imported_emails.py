#!/usr/bin/env python3
"""Check what emails were actually imported to CRM"""

import requests
import msal
from datetime import datetime, timedelta

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 CHECKING IMPORTED EMAILS")
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

# Check for recently created emails (last 24 hours)
print("\n📧 Checking recently created emails...")
yesterday = datetime.now() - timedelta(hours=24)
yesterday_iso = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')

response = requests.get(
    f"{crm_base_url}/emails?$filter=createdon ge {yesterday_iso}&$orderby=createdon desc&$top=200&$select=subject,createdon,_regardingobjectid_value,actualstart,actualend",
    headers=headers
)

if response.status_code == 200:
    recent_emails = response.json().get('value', [])
    print(f"📧 Found {len(recent_emails)} recently created emails")
    
    if recent_emails:
        print("\n📅 Recent Emails (last 24 hours):")
        print("-" * 60)
        
        ringcentral_count = 0
        unlinked_count = 0
        
        for i, email in enumerate(recent_emails[:20]):
            created_date = email.get('createdon', '')
            subject = email.get('subject', 'No Subject')[:40]
            regarding_id = email.get('_regardingobjectid_value')
            actual_start = email.get('actualstart', '')
            
            # Count RingCentral emails
            if 'ringcentral' in subject.lower() or 'text message' in subject.lower():
                ringcentral_count += 1
                marker = "🔔"
            else:
                marker = "📧"
                
            # Count unlinked emails
            if not regarding_id:
                unlinked_count += 1
                link_status = "❌ UNLINKED"
            else:
                link_status = f"✅ Linked to {regarding_id[:8]}..."
            
            print(f"{marker} {created_date[:19]} - {subject} | {link_status}")
        
        print(f"\n📊 Summary:")
        print(f"   🔔 RingCentral-like emails: {ringcentral_count}")
        print(f"   ❌ Unlinked emails: {unlinked_count}")
        print(f"   ✅ Linked emails: {len(recent_emails[:20]) - unlinked_count}")
        
        # Check RingCentral contact specifically
        print(f"\n🔍 Checking RingCentral contact...")
        contact_response = requests.get(
            f"{crm_base_url}/contacts?$filter=contains(emailaddress1,'ringcentral.com')&$select=contactid,fullname,emailaddress1", 
            headers=headers
        )
        
        if contact_response.status_code == 200:
            contacts = contact_response.json().get('value', [])
            if contacts:
                contact = contacts[0]
                contact_id = contact['contactid']
                print(f"✅ RingCentral contact: {contact['fullname']} ({contact_id})")
                
                # Check emails specifically linked to this contact
                linked_response = requests.get(
                    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$orderby=createdon desc&$top=50&$select=subject,createdon,actualstart", 
                    headers=headers
                )
                
                if linked_response.status_code == 200:
                    linked_emails = linked_response.json().get('value', [])
                    print(f"📧 Emails linked to RingCentral: {len(linked_emails)}")
                    
                    if linked_emails:
                        print("\n📅 RingCentral Timeline:")
                        for i, email in enumerate(linked_emails[:10]):
                            created = email.get('createdon', '')[:19]
                            actual = email.get('actualstart', '')[:19] if email.get('actualstart') else 'No Date'
                            subject = email.get('subject', 'No Subject')[:30]
                            print(f"   {i+1:2d}. Created: {created} | Actual: {actual} | {subject}")
                else:
                    print(f"❌ Error checking linked emails: {linked_response.status_code}")
    
    # Check for unlinked emails that might be our imports
    print(f"\n🔍 Checking unlinked emails...")
    unlinked_response = requests.get(
        f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq null and createdon ge {yesterday_iso}&$orderby=createdon desc&$top=50&$select=subject,createdon,actualstart",
        headers=headers
    )
    
    if unlinked_response.status_code == 200:
        unlinked_emails = unlinked_response.json().get('value', [])
        print(f"📧 Found {len(unlinked_emails)} unlinked emails")
        
        if unlinked_emails:
            ringcentral_unlinked = 0
            print("\n❌ Unlinked Emails:")
            for i, email in enumerate(unlinked_emails[:15]):
                subject = email.get('subject', 'No Subject')[:40]
                created = email.get('createdon', '')[:19]
                
                if 'ringcentral' in subject.lower() or 'text message' in subject.lower():
                    ringcentral_unlinked += 1
                    marker = "🔔"
                else:
                    marker = "📧"
                
                print(f"   {marker} {created} - {subject}")
            
            print(f"\n📊 Unlinked RingCentral emails: {ringcentral_unlinked}")
    
else:
    print(f"❌ Error getting recent emails: {response.status_code}")

print(f"\n🎯 DIAGNOSIS:")
print(f"   ✅ We can see recently imported emails")
print(f"   🔍 Need to check if relationship linking worked properly")
print(f"   💡 Emails might be created but not linked to contacts") 