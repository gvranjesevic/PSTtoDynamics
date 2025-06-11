#!/usr/bin/env python3
"""
Quick verification of the test email we just created.
"""

import requests
import msal

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# Email ID from the previous test
TEST_EMAIL_ID = "f1e5d887-bc46-f011-8779-7ced8d1c74fb"
RINGCENTRAL_CONTACT_ID = "6a219814-dc41-f011-b4cb-7c1e52168e20"

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("🔐 Authenticating...")
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

def verify_test_email(headers):
    """Verifies the test email we created."""
    print(f"\n🔍 Checking test email {TEST_EMAIL_ID}...")
    
    # Simple verification query
    verify_url = f"{crm_base_url}/emails({TEST_EMAIL_ID})?$select=activityid,subject,statecode,statuscode,createdon,senton,description"
    
    response = requests.get(verify_url, headers=headers)
    
    if response.status_code == 200:
        email_data = response.json()
        print(f"✅ Email found successfully!")
        print(f"   📧 Subject: {email_data.get('subject', 'N/A')}")
        print(f"   📊 State: {email_data.get('statecode', 'N/A')} (0=Open, 1=Completed)")
        print(f"   📊 Status: {email_data.get('statuscode', 'N/A')} (4=Received)")
        print(f"   📅 Created: {email_data.get('createdon', 'N/A')}")
        return True
    else:
        print(f"❌ Failed to verify email: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def check_latest_ringcentral_emails(headers):
    """Checks the latest emails for RingCentral contact."""
    print(f"\n📧 Checking latest emails for RingCentral contact...")
    
    url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {RINGCENTRAL_CONTACT_ID}&$select=activityid,subject,createdon,statecode,statuscode&$orderby=createdon desc&$top=3"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emails = response.json().get('value', [])
        print(f"✅ Found {len(emails)} recent emails:")
        
        for i, email in enumerate(emails):
            created = email.get('createdon', 'N/A')[:16].replace('T', ' ')  # Show date/time only
            state_text = "Completed" if email.get('statecode') == 1 else "Open"
            status_text = "Received" if email.get('statuscode') == 4 else f"Status{email.get('statuscode')}"
            
            print(f"   {i+1}. {email.get('subject', 'No Subject')[:50]}...")
            print(f"      📅 Created: {created} | 📊 {state_text}/{status_text}")
            
            if email.get('activityid') == TEST_EMAIL_ID:
                print(f"      ⭐ THIS IS OUR TEST EMAIL!")
        
        return True
    else:
        print(f"❌ Failed to retrieve emails: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🔍 Quick Verification of Test Email")
    print("=" * 40)
    
    headers = get_auth_headers()
    if not headers:
        exit(1)
    
    # Check the specific test email
    email_verified = verify_test_email(headers)
    
    # Check latest RingCentral emails
    emails_checked = check_latest_ringcentral_emails(headers)
    
    print("\n" + "=" * 40)
    if email_verified and emails_checked:
        print("🎉 Verification complete!")
        print()
        print("📸 NEXT STEP: Please go to Dynamics 365 and:")
        print("   1. Navigate to RingCentral contact timeline")
        print("   2. Look for the email: '✅ CORRECTED TEST: April 2025...'")
        print("   3. Check that it shows 'Email from: RingCentral' (not 'Email from: Closed')")
        print("   4. Verify the status shows as 'Closed'")
        print("   5. Take a screenshot for our review!")
    else:
        print("❌ Verification had issues.")
    
    print("=" * 40) 