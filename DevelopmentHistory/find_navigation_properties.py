#!/usr/bin/env python3
"""Find the correct navigation property names for email sender"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 FINDING CORRECT NAVIGATION PROPERTIES")
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

# Get metadata for email entity
print("\n🔍 Getting email entity metadata...")
metadata_response = requests.get(
    f"{crm_base_url}/$metadata?$filter=EntityType/Name eq 'email'",
    headers=headers
)

# Try a different approach - check entity definition
print("🔍 Checking entity definition for emails...")
entitydef_response = requests.get(
    f"{crm_base_url}/EntityDefinitions?$filter=LogicalName eq 'email'&$expand=Attributes,ManyToOneRelationships",
    headers=headers
)

if entitydef_response.status_code == 200:
    entity_data = entitydef_response.json()
    
    if 'value' in entity_data and len(entity_data['value']) > 0:
        email_entity = entity_data['value'][0]
        
        print(f"📧 Email entity found!")
        
        # Look for sender-related relationships
        relationships = email_entity.get('ManyToOneRelationships', [])
        sender_relationships = []
        
        for rel in relationships:
            rel_name = rel.get('SchemaName', '').lower()
            if any(keyword in rel_name for keyword in ['sender', 'from', 'email']):
                sender_relationships.append(rel)
        
        print(f"\n🎯 SENDER-RELATED RELATIONSHIPS ({len(sender_relationships)}):")
        print("-" * 40)
        
        for rel in sender_relationships:
            schema_name = rel.get('SchemaName', 'Unknown')
            target_entity = rel.get('ReferencedEntity', 'Unknown')
            lookup_field = rel.get('ReferencingAttribute', 'Unknown')
            nav_property = rel.get('ReferencingEntityNavigationPropertyName', 'Unknown')
            
            print(f"\n🔍 {schema_name}:")
            print(f"   Target Entity: {target_entity}")
            print(f"   Lookup Field:  {lookup_field}")
            print(f"   Nav Property:  {nav_property}")
            
            # This might be the one we need
            if 'sender' in schema_name.lower():
                print(f"   ⭐ LIKELY CANDIDATE!")

# Also try to examine a working email with expanded navigation properties
print(f"\n🔍 Examining working email with expanded properties...")

# Get notify contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'notify@ringcentral.com'&$select=contactid", 
    headers=headers
)

notify_contact_id = contact_response.json()['value'][0]['contactid']

# Get working email with expanded nav properties
working_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact_id}&$top=1&$expand=emailsender_contact,emailsender_queue,emailsender_systemuser",
    headers=headers
)

if working_email_response.status_code == 200:
    working_email = working_email_response.json()['value'][0]
    
    print(f"📧 Working email expanded properties:")
    
    nav_props = ['emailsender_contact', 'emailsender_queue', 'emailsender_systemuser']
    for prop in nav_props:
        value = working_email.get(prop)
        if value:
            print(f"   ✅ {prop}: {value}")
        else:
            print(f"   ❌ {prop}: None")
else:
    print(f"❌ Could not get working email: {working_email_response.status_code}")

# Try different navigation property names
print(f"\n🔧 TESTING ALTERNATIVE NAVIGATION PROPERTIES:")
print("-" * 50)

# Get our test email
service_contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid", 
    headers=headers
)
service_contact_id = service_contact_response.json()['value'][0]['contactid']

test_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {service_contact_id} and actualstart ge 2025-04-01T00:00:00Z&$top=1&$select=activityid",
    headers=headers
)
test_email_id = test_email_response.json()['value'][0]['activityid']

# Try different navigation property patterns
nav_properties_to_try = [
    "emailsender@odata.bind",
    "emailsender_systemuser@odata.bind", 
    "from@odata.bind",
    "sender@odata.bind"
]

for nav_prop in nav_properties_to_try:
    print(f"\n🧪 Trying: {nav_prop}")
    
    if 'systemuser' in nav_prop:
        # Try with systemuser if it's user-related
        update_data = {nav_prop: f"/systemusers(5794f83f-9b37-f011-8c4e-000d3a9c4367)"}
    else:
        # Try with contact
        update_data = {nav_prop: f"/contacts({service_contact_id})"}
    
    test_response = requests.patch(
        f"{crm_base_url}/emails({test_email_id})",
        json=update_data,
        headers=headers
    )
    
    if test_response.status_code in [200, 204]:
        print(f"   ✅ SUCCESS: {nav_prop} worked!")
        print(f"   📅 Please refresh Dynamics to check if 'Email from' changed!")
        break
    else:
        print(f"   ❌ Failed: {test_response.status_code}")

print(f"\n💡 If none of these work, the issue might be:")
print(f"   - Email sender is a calculated/read-only field")
print(f"   - It requires a specific entity type (systemuser vs contact)")
print(f"   - It needs to be set at email creation time, not via update")
print(f"   - There's a business logic preventing the change") 