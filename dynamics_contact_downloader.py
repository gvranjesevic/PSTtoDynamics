#!/usr/bin/env python3
"""
Dynamics 365 Contact Downloader
A Python script to connect to Dynamics 365 CRM and download contact information to CSV.

Requirements:
- pip install requests msal pandas tabulate
"""

import os
import sys
import json
import csv
import requests
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import msal
import time


class Dynamics365ContactDownloader:
    def __init__(self, username, password, tenant_domain=None):
        """Initialize the Dynamics 365 connection."""
        self.username = username
        self.password = password
        self.tenant_domain = tenant_domain or "dynamique.com"
        
        # Dynamics 365 configuration
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"  # Common PowerApps client ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_domain}"
        self.scope = ["https://dynglobal.crm.dynamics.com/.default"]
        
        # Will be set after authentication
        self.access_token = None
        self.crm_base_url = None
        self.contacts_data = []
        
        print("🔧 Dynamics 365 Contact Downloader Initialized")
        print(f"📧 User: {self.username}")
        print(f"🏢 Tenant: {self.tenant_domain}")
    
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
    
    def discover_crm_url(self):
        """Connect to the known Dynamics 365 CRM URL."""
        try:
            print("\n🔗 Connecting to Dynamics 365 CRM...")
            
            # Use the known CRM URL
            crm_url = "https://dynglobal.crm.dynamics.com"
            self.crm_base_url = f"{crm_url}/api/data/v9.2"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Test the connection
            test_url = f"{self.crm_base_url}/WhoAmI"
            print(f"   🎯 Testing connection to: {crm_url}")
            
            response = requests.get(test_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Successfully connected to Dynamics 365!")
                print(f"   🌐 CRM URL: {crm_url}")
                print(f"   👤 User ID: {user_info.get('UserId', 'Unknown')}")
                print(f"   🏢 Organization ID: {user_info.get('OrganizationId', 'Unknown')}")
                return True
            elif response.status_code == 401:
                print(f"❌ Unauthorized (401): Invalid credentials or insufficient permissions")
                print(f"   💡 Check if the user has access to Dynamics 365 CRM")
                return False
            elif response.status_code == 403:
                print(f"❌ Forbidden (403): Access denied")
                print(f"   💡 User may need proper licensing or permissions")
                return False
            else:
                print(f"❌ Connection failed with status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to CRM: {str(e)}")
            return False
    
    def get_contacts(self):
        """Retrieve contacts from Dynamics 365."""
        try:
            print("\n📞 Retrieving contacts from Dynamics 365...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Prefer': 'odata.maxpagesize=500'
            }
            
            # OData query to get contact information
            select_fields = [
                "contactid",
                "fullname", 
                "firstname",
                "lastname",
                "emailaddress1",
                "emailaddress2", 
                "emailaddress3",
                "telephone1",
                "telephone2",
                "mobilephone",
                "fax",
                "jobtitle",
                "address1_line1",
                "address1_line2", 
                "address1_city",
                "address1_stateorprovince",
                "address1_postalcode",
                "address1_country",
                "createdon",
                "modifiedon",
                "statecode",
                "statuscode"
            ]
            
            contacts_url = f"{self.crm_base_url}/contacts"
            params = {
                '$select': ','.join(select_fields),
                '$orderby': 'fullname asc',
                '$filter': 'statecode eq 0'  # Active contacts only
            }
            
            all_contacts = []
            page_count = 0
            
            while contacts_url:
                page_count += 1
                print(f"   📄 Fetching page {page_count}...")
                
                response = requests.get(contacts_url, headers=headers, params=params if page_count == 1 else None, timeout=30)
                
                if response.status_code != 200:
                    print(f"❌ Error fetching contacts: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                data = response.json()
                contacts = data.get('value', [])
                all_contacts.extend(contacts)
                
                print(f"   ✅ Retrieved {len(contacts)} contacts from page {page_count}")
                
                # Check for next page
                contacts_url = data.get('@odata.nextLink')
                params = None  # Clear params for subsequent requests
            
            self.contacts_data = all_contacts
            print(f"\n✅ Total contacts retrieved: {len(self.contacts_data)}")
            return True
            
        except Exception as e:
            print(f"❌ Error retrieving contacts: {str(e)}")
            return False
    
    def export_to_csv(self, filename="dynamics_contacts.csv"):
        """Export contacts to CSV file."""
        try:
            print(f"\n📊 Exporting {len(self.contacts_data)} contacts to {filename}...")
            
            if not self.contacts_data:
                print("❌ No contact data to export")
                return False
            
            # Prepare data for CSV
            csv_data = []
            for contact in self.contacts_data:
                # Format dates
                created_on = contact.get('createdon', '')
                modified_on = contact.get('modifiedon', '')
                
                if created_on:
                    try:
                        created_on = datetime.fromisoformat(created_on.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                if modified_on:
                    try:
                        modified_on = datetime.fromisoformat(modified_on.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                # Format address
                address_parts = [
                    contact.get('address1_line1', ''),
                    contact.get('address1_line2', ''),
                    contact.get('address1_city', ''),
                    contact.get('address1_stateorprovince', ''),
                    contact.get('address1_postalcode', ''),
                    contact.get('address1_country', '')
                ]
                full_address = ', '.join([part for part in address_parts if part])
                
                csv_row = {
                    'contact_id': contact.get('contactid', ''),
                    'full_name': contact.get('fullname', ''),
                    'first_name': contact.get('firstname', ''),
                    'last_name': contact.get('lastname', ''),
                    'primary_email': contact.get('emailaddress1', ''),
                    'secondary_email': contact.get('emailaddress2', ''),
                    'tertiary_email': contact.get('emailaddress3', ''),
                    'business_phone': contact.get('telephone1', ''),
                    'home_phone': contact.get('telephone2', ''),
                    'mobile_phone': contact.get('mobilephone', ''),
                    'fax': contact.get('fax', ''),
                    'job_title': contact.get('jobtitle', ''),
                    'company': '',  # Company field will be retrieved separately if needed
                    'full_address': full_address,
                    'address_line1': contact.get('address1_line1', ''),
                    'address_line2': contact.get('address1_line2', ''),
                    'city': contact.get('address1_city', ''),
                    'state': contact.get('address1_stateorprovince', ''),
                    'postal_code': contact.get('address1_postalcode', ''),
                    'country': contact.get('address1_country', ''),
                    'created_on': created_on,
                    'modified_on': modified_on,
                    'status': 'Active' if contact.get('statecode') == 0 else 'Inactive'
                }
                csv_data.append(csv_row)
            
            # Write to CSV
            if csv_data:
                df = pd.DataFrame(csv_data)
                df.to_csv(filename, index=False, encoding='utf-8')
                
                print(f"✅ Successfully exported to {filename}")
                
                # Show summary statistics
                self.show_summary_statistics(csv_data)
                return True
            else:
                print("❌ No data to write to CSV")
                return False
                
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")
            return False
    
    def show_summary_statistics(self, csv_data):
        """Display summary statistics of the exported contacts."""
        try:
            print(f"\n📊 CONTACT EXPORT SUMMARY")
            print("="*50)
            
            total_contacts = len(csv_data)
            print(f"📞 Total Contacts: {total_contacts:,}")
            
            # Email statistics
            primary_emails = sum(1 for contact in csv_data if contact['primary_email'])
            secondary_emails = sum(1 for contact in csv_data if contact['secondary_email'])
            any_email = sum(1 for contact in csv_data if contact['primary_email'] or contact['secondary_email'] or contact['tertiary_email'])
            
            print(f"\n📧 Email Statistics:")
            email_stats = [
                ['Contacts with Primary Email', f"{primary_emails:,}", f"{(primary_emails/total_contacts)*100:.1f}%"],
                ['Contacts with Secondary Email', f"{secondary_emails:,}", f"{(secondary_emails/total_contacts)*100:.1f}%"],
                ['Contacts with Any Email', f"{any_email:,}", f"{(any_email/total_contacts)*100:.1f}%"]
            ]
            print(tabulate(email_stats, headers=['Metric', 'Count', 'Percentage'], tablefmt='grid'))
            
            # Phone statistics  
            business_phones = sum(1 for contact in csv_data if contact['business_phone'])
            mobile_phones = sum(1 for contact in csv_data if contact['mobile_phone'])
            any_phone = sum(1 for contact in csv_data if contact['business_phone'] or contact['mobile_phone'] or contact['home_phone'])
            
            print(f"\n📱 Phone Statistics:")
            phone_stats = [
                ['Contacts with Business Phone', f"{business_phones:,}", f"{(business_phones/total_contacts)*100:.1f}%"],
                ['Contacts with Mobile Phone', f"{mobile_phones:,}", f"{(mobile_phones/total_contacts)*100:.1f}%"],
                ['Contacts with Any Phone', f"{any_phone:,}", f"{(any_phone/total_contacts)*100:.1f}%"]
            ]
            print(tabulate(phone_stats, headers=['Metric', 'Count', 'Percentage'], tablefmt='grid'))
            
            # Address statistics
            addresses = sum(1 for contact in csv_data if contact['full_address'])
            cities = sum(1 for contact in csv_data if contact['city'])
            
            print(f"\n🏠 Address Statistics:")
            address_stats = [
                ['Contacts with Address', f"{addresses:,}", f"{(addresses/total_contacts)*100:.1f}%"],
                ['Contacts with City', f"{cities:,}", f"{(cities/total_contacts)*100:.1f}%"]
            ]
            print(tabulate(address_stats, headers=['Metric', 'Count', 'Percentage'], tablefmt='grid'))
            
            # Top companies (if available)
            companies = [contact['company'] for contact in csv_data if contact['company']]
            if companies:
                from collections import Counter
                company_counts = Counter(companies)
                print(f"\n🏢 Top 10 Companies:")
                company_table = [[company, count] for company, count in company_counts.most_common(10)]
                print(tabulate(company_table, headers=['Company', 'Contacts'], tablefmt='grid'))
            
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"⚠️  Error generating summary: {str(e)}")
    
    def run(self):
        """Run the complete contact download process."""
        try:
            print("🚀 Starting Dynamics 365 Contact Download Process")
            print("="*55)
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Discover CRM URL
            if not self.discover_crm_url():
                return False
            
            # Step 3: Get contacts
            if not self.get_contacts():
                return False
            
            # Step 4: Export to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dynamics_contacts_{timestamp}.csv"
            if not self.export_to_csv(filename):
                return False
            
            print(f"\n🎉 Contact download completed successfully!")
            print(f"📁 File saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False


def main():
    """Main function to run the Dynamics 365 contact downloader."""
    # Credentials
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    
    print("🔍 DYNAMICS 365 CONTACT DOWNLOADER")
    print("="*40)
    print("🎯 Purpose: Download all contacts from Dynamics 365 CRM to CSV")
    print(f"📧 User: {username}")
    print()
    
    # Create downloader instance
    downloader = Dynamics365ContactDownloader(username, password)
    
    try:
        # Run the download process
        success = downloader.run()
        
        if success:
            print("\n✅ Process completed successfully!")
        else:
            print("\n❌ Process failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 