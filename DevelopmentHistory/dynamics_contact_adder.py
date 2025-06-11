#!/usr/bin/env python3
"""
Dynamics 365 Contact Adder
A Python script to add new contacts to Dynamics 365 CRM from the cleaned email list.
This version adds ONE contact as a test to establish the functionality.

Requirements:
- pip install requests msal pandas tabulate
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import msal
import time


class Dynamics365ContactAdder:
    def __init__(self, username, password, tenant_domain=None):
        """Initialize the Dynamics 365 contact adder."""
        self.username = username
        self.password = password
        self.tenant_domain = tenant_domain or "dynamique.com"
        
        # Dynamics 365 configuration
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"  # Common PowerApps client ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_domain}"
        self.scope = ["https://dynglobal.crm.dynamics.com/.default"]
        
        # Will be set after authentication
        self.access_token = None
        self.crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
        self.cleaned_emails_df = None
        
        print("➕ Dynamics 365 Contact Adder")
        print("="*35)
        print(f"📧 User: {self.username}")
        print(f"🏢 Tenant: {self.tenant_domain}")
        print(f"🌐 CRM URL: https://dynglobal.crm.dynamics.com")
    
    def authenticate(self):
        """Authenticate with Dynamics 365 using MSAL."""
        try:
            print("\n🔐 Starting authentication...")
            
            # Create MSAL app
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=self.authority
            )
            
            # Try to get token silently first
            accounts = app.get_accounts()
            if accounts:
                print("🔍 Found existing account, attempting silent authentication...")
                result = app.acquire_token_silent(self.scope, account=accounts[0])
                if result:
                    self.access_token = result['access_token']
                    print("✅ Silent authentication successful!")
                    return True
            
            # Interactive authentication with username/password
            print("🔑 Performing username/password authentication...")
            result = app.acquire_token_by_username_password(
                username=self.username,
                password=self.password,
                scopes=self.scope
            )
            
            if "access_token" in result:
                self.access_token = result['access_token']
                print("✅ Authentication successful!")
                return True
            else:
                print("❌ Authentication failed:")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Description: {result.get('error_description', 'No description')}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_connection(self):
        """Test the connection to Dynamics 365."""
        try:
            print("\n🔗 Testing Dynamics 365 connection...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Test the connection with WhoAmI
            test_url = f"{self.crm_base_url}/WhoAmI"
            response = requests.get(test_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Successfully connected to Dynamics 365!")
                print(f"   👤 User ID: {user_info.get('UserId', 'Unknown')}")
                print(f"   🏢 Organization ID: {user_info.get('OrganizationId', 'Unknown')}")
                return True
            else:
                print(f"❌ Connection failed with status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing connection: {str(e)}")
            return False
    
    def load_cleaned_emails(self, csv_file):
        """Load the cleaned email addresses CSV file."""
        try:
            print(f"\n📂 Loading cleaned email addresses from {csv_file}...")
            
            self.cleaned_emails_df = pd.read_csv(csv_file)
            print(f"✅ Loaded {len(self.cleaned_emails_df)} cleaned email addresses")
            
            # Show the first few entries
            print(f"\n📧 Top 5 candidates for addition:")
            top_5 = self.cleaned_emails_df.head(5)
            for idx, row in top_5.iterrows():
                print(f"   {idx+1}. {row['email_address']} - {row['display_name']} ({row['count']} emails)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading cleaned emails: {str(e)}")
            return False
    
    def select_test_contact(self):
        """Select the first contact from the cleaned list for testing."""
        try:
            if self.cleaned_emails_df is None or len(self.cleaned_emails_df) == 0:
                print("❌ No cleaned email data available")
                return None
            
            # Get the first contact (highest activity)
            test_contact = self.cleaned_emails_df.iloc[0]
            
            print(f"\n🎯 Selected test contact:")
            print(f"   📧 Email: {test_contact['email_address']}")
            print(f"   👤 Name: {test_contact['display_name']}")
            print(f"   📊 Email Count: {test_contact['count']}")
            print(f"   🏷️  First Name: {test_contact['first_name']}")
            print(f"   🏷️  Last Name: {test_contact['last_name']}")
            
            return test_contact
            
        except Exception as e:
            print(f"❌ Error selecting test contact: {str(e)}")
            return None
    
    def create_contact_data(self, contact_row):
        """Create the contact data structure for Dynamics 365."""
        try:
            # Extract contact information
            email = contact_row['email_address']
            first_name = contact_row['first_name'] if pd.notna(contact_row['first_name']) else ""
            last_name = contact_row['last_name'] if pd.notna(contact_row['last_name']) else ""
            display_name = contact_row['display_name'] if pd.notna(contact_row['display_name']) else ""
            
            # Handle cases where first/last name might be empty
            if not first_name and not last_name:
                # Try to parse from display_name or email
                if display_name and display_name != email:
                    # Try to split display_name
                    name_parts = display_name.strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = " ".join(name_parts[1:])
                    else:
                        first_name = name_parts[0] if name_parts else ""
                        last_name = ""
                else:
                    # Use email local part as first name
                    first_name = email.split('@')[0]
                    last_name = ""
            
            # Clean up names (remove quotes, parentheses content, etc.)
            first_name = first_name.replace('"', '').strip()
            last_name = last_name.replace('"', '').strip()
            
            # Remove content in parentheses from names
            import re
            first_name = re.sub(r'\([^)]*\)', '', first_name).strip()
            last_name = re.sub(r'\([^)]*\)', '', last_name).strip()
            
            # Create the contact data
            contact_data = {
                "firstname": first_name[:50],  # Dynamics has field length limits
                "lastname": last_name[:50],
                "emailaddress1": email,
                "fullname": f"{first_name} {last_name}".strip()[:160],
                "description": f"Added from PST analysis - {contact_row['count']} email interactions",
                "preferredcontactmethodcode": 2,  # Email preferred
                "donotsendmm": False,  # Allow marketing materials
                "donotemail": False,   # Allow emails
            }
            
            # Remove empty string fields
            contact_data = {k: v for k, v in contact_data.items() if v != ""}
            
            print(f"\n📋 Contact data prepared:")
            for key, value in contact_data.items():
                print(f"   {key}: {value}")
            
            return contact_data
            
        except Exception as e:
            print(f"❌ Error creating contact data: {str(e)}")
            return None
    
    def add_contact_to_crm(self, contact_data):
        """Add the contact to Dynamics 365 CRM."""
        try:
            print(f"\n➕ Adding contact to Dynamics 365 CRM...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            # Create contact endpoint
            create_url = f"{self.crm_base_url}/contacts"
            
            print(f"   🌐 POST URL: {create_url}")
            print(f"   📦 Payload: {json.dumps(contact_data, indent=2)}")
            
            # Make the request
            response = requests.post(create_url, headers=headers, json=contact_data, timeout=30)
            
            if response.status_code == 204:  # Success - Created
                # Get the contact ID from the location header
                location = response.headers.get('OData-EntityId', '')
                contact_id = location.split('(')[-1].split(')')[0] if '(' in location else 'Unknown'
                
                print(f"✅ Contact successfully created!")
                print(f"   🆔 Contact ID: {contact_id}")
                print(f"   📧 Email: {contact_data['emailaddress1']}")
                print(f"   👤 Name: {contact_data.get('fullname', 'Unknown')}")
                
                return contact_id
                
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                print(f"❌ Bad request (400): {error_message}")
                if 'duplicate' in error_message.lower() or 'already exists' in error_message.lower():
                    print(f"   💡 Contact may already exist in CRM")
                else:
                    print(f"   💡 Check the contact data format and field requirements")
                return None
                
            elif response.status_code == 401:
                print(f"❌ Unauthorized (401): Authentication token may have expired")
                return None
                
            elif response.status_code == 403:
                print(f"❌ Forbidden (403): Insufficient permissions to create contacts")
                return None
                
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error adding contact to CRM: {str(e)}")
            return None
    
    def verify_contact_creation(self, contact_id, email):
        """Verify the contact was created successfully."""
        try:
            print(f"\n🔍 Verifying contact creation...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Query for the contact by email
            query_url = f"{self.crm_base_url}/contacts"
            params = {
                '$select': 'contactid,fullname,firstname,lastname,emailaddress1,createdon',
                '$filter': f"emailaddress1 eq '{email}'"
            }
            
            response = requests.get(query_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('value', [])
                
                if contacts:
                    contact = contacts[0]  # Should be unique by email
                    created_on = contact.get('createdon', '')
                    
                    print(f"✅ Contact verification successful!")
                    print(f"   🆔 Contact ID: {contact.get('contactid', 'Unknown')}")
                    print(f"   👤 Full Name: {contact.get('fullname', 'Unknown')}")
                    print(f"   📧 Email: {contact.get('emailaddress1', 'Unknown')}")
                    print(f"   📅 Created: {created_on}")
                    
                    return True
                else:
                    print(f"⚠️  Contact not found in verification query")
                    return False
            else:
                print(f"❌ Verification query failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying contact: {str(e)}")
            return False
    
    def run_test(self, csv_file):
        """Run the complete test process to add one contact."""
        try:
            print("🚀 Starting Dynamics 365 Contact Addition Test")
            print("="*50)
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Test connection
            if not self.test_connection():
                return False
            
            # Step 3: Load cleaned emails
            if not self.load_cleaned_emails(csv_file):
                return False
            
            # Step 4: Select test contact
            test_contact = self.select_test_contact()
            if test_contact is None:
                return False
            
            # Step 5: Create contact data
            contact_data = self.create_contact_data(test_contact)
            if contact_data is None:
                return False
            
            # Step 6: Add contact to CRM
            contact_id = self.add_contact_to_crm(contact_data)
            if contact_id is None:
                return False
            
            # Step 7: Verify creation
            verified = self.verify_contact_creation(contact_id, contact_data['emailaddress1'])
            
            if verified:
                print(f"\n🎉 Contact addition test completed successfully!")
                print(f"📧 Email: {contact_data['emailaddress1']}")
                print(f"👤 Name: {contact_data.get('fullname', 'Unknown')}")
                print(f"🆔 Contact ID: {contact_id}")
                print(f"💡 This contact is now in your Dynamics 365 CRM system")
                return True
            else:
                print(f"\n⚠️  Contact may have been created but verification failed")
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error in test: {str(e)}")
            return False


def main():
    """Main function to run the contact addition test."""
    # Configuration
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    csv_file = "email_addresses_cleaned_20250610_160516.csv"
    
    print("➕ DYNAMICS 365 CONTACT ADDITION TEST")
    print("="*40)
    print("🎯 Purpose: Add ONE contact from cleaned email list to test functionality")
    print(f"📧 User: {username}")
    print(f"📂 Source: {csv_file}")
    print()
    
    # Create contact adder instance
    contact_adder = Dynamics365ContactAdder(username, password)
    
    try:
        # Run the test
        success = contact_adder.run_test(csv_file)
        
        if success:
            print("\n✅ Test completed successfully!")
            print("💡 You can now use this functionality to add more contacts")
        else:
            print("\n❌ Test failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 