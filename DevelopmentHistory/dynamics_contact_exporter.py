#!/usr/bin/env python3
"""
Dynamics 365 Contact Exporter
============================

This script downloads all contacts from Dynamics 365 CRM and exports them 
in multiple human-readable formats (CSV, JSON, Excel).

Features:
- Complete contact export with all fields
- Multiple output formats (CSV, JSON, Excel)
- Progress tracking and statistics
- Error handling and logging
- Human-readable field mapping

Author: AI Assistant
Date: December 2024
"""

import os
import sys
import json
import csv
import time
import requests
from datetime import datetime
import msal
from tabulate import tabulate

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available - Excel export will be disabled")

class Dynamics365ContactExporter:
    def __init__(self, username, password, tenant_domain=None):
        """Initialize the Dynamics 365 Contact Exporter."""
        self.username = username
        self.password = password
        self.tenant_domain = tenant_domain or username.split('@')[1]
        self.tenant_id = f"{self.tenant_domain}"
        
        # Dynamics 365 configuration
        self.crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"  # Microsoft Dynamics CRM client ID
        
        # Authentication
        self.access_token = None
        self.contacts = []
        
        print("📊 DYNAMICS 365 CONTACT EXPORTER")
        print("="*50)
        print(f"👤 User: {self.username}")
        print(f"🏢 Tenant: {self.tenant_domain}")
        print(f"🌐 CRM URL: {self.crm_base_url}")

    def authenticate(self):
        """Authenticate with Dynamics 365 using MSAL."""
        try:
            print("\n🔐 Starting authentication...")
            
            # Create MSAL application
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_domain}"
            )
            
            # Define scopes for Dynamics 365
            scopes = ["https://dynglobal.crm.dynamics.com/.default"]
            
            # Attempt to get token
            result = app.acquire_token_by_username_password(
                username=self.username,
                password=self.password,
                scopes=scopes
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                print("✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def get_all_contacts(self):
        """Download all contacts from Dynamics 365 CRM."""
        try:
            print("\n📥 Downloading contacts from Dynamics 365...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            # Define comprehensive contact fields to retrieve
            select_fields = [
                'contactid', 'fullname', 'firstname', 'lastname', 
                'emailaddress1', 'emailaddress2', 'emailaddress3',
                'telephone1', 'mobilephone',
                'jobtitle', 
                'address1_city', 'address1_stateorprovince', 'address1_country',
                'createdon', 'modifiedon', 
                'statuscode', 'statecode'
            ]
            
            select_query = ','.join(select_fields)
            
            # Start with first page
            url = f"{self.crm_base_url}/contacts?$select={select_query}&$top=5000"
            all_contacts = []
            page_count = 0
            
            while url:
                page_count += 1
                print(f"   📄 Processing page {page_count}...")
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    contacts_batch = data.get('value', [])
                    all_contacts.extend(contacts_batch)
                    
                    print(f"      ✅ Retrieved {len(contacts_batch)} contacts (Total: {len(all_contacts)})")
                    
                    # Check for next page
                    url = data.get('@odata.nextLink')
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.2)
                    
                else:
                    print(f"      ❌ Error retrieving contacts: {response.status_code}")
                    if response.content:
                        error_data = response.json()
                        print(f"         Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
                    break
            
            self.contacts = all_contacts
            print(f"\n📊 Contact download completed:")
            print(f"   📄 Pages processed: {page_count}")
            print(f"   👥 Total contacts: {len(all_contacts)}")
            
            return len(all_contacts) > 0
            
        except Exception as e:
            print(f"❌ Error downloading contacts: {str(e)}")
            return False

    def export_to_csv(self, filename=None):
        """Export contacts to CSV format."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"dynamics_contacts_export_{timestamp}.csv"
            
            print(f"\n📄 Exporting to CSV: {filename}")
            
            if not self.contacts:
                print("❌ No contacts to export")
                return False
            
            # Prepare data for CSV
            csv_data = []
            for contact in self.contacts:
                # Create human-readable row
                row = {
                    'Contact ID': contact.get('contactid', ''),
                    'Full Name': contact.get('fullname', ''),
                    'First Name': contact.get('firstname', ''),
                    'Last Name': contact.get('lastname', ''),
                    'Primary Email': contact.get('emailaddress1', ''),
                    'Secondary Email': contact.get('emailaddress2', ''),
                    'Third Email': contact.get('emailaddress3', ''),
                    'Phone': contact.get('telephone1', ''),
                    'Mobile Phone': contact.get('mobilephone', ''),
                    'Job Title': contact.get('jobtitle', ''),
                    'City': contact.get('address1_city', ''),
                    'State': contact.get('address1_stateorprovince', ''),
                    'Country': contact.get('address1_country', ''),
                    'Created On': self._format_datetime(contact.get('createdon')),
                    'Modified On': self._format_datetime(contact.get('modifiedon')),
                    'Status': self._format_status(contact.get('statuscode'))
                }
                csv_data.append(row)
            
            # Write CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if csv_data:
                    fieldnames = csv_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            print(f"✅ CSV export completed: {len(csv_data)} contacts")
            print(f"   📁 File: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")
            return None

    def export_to_json(self, filename=None):
        """Export contacts to JSON format."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"dynamics_contacts_export_{timestamp}.json"
            
            print(f"\n📄 Exporting to JSON: {filename}")
            
            if not self.contacts:
                print("❌ No contacts to export")
                return False
            
            # Prepare JSON structure with metadata
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_contacts': len(self.contacts),
                    'crm_url': self.crm_base_url,
                    'exported_by': self.username
                },
                'contacts': []
            }
            
            # Process each contact
            for contact in self.contacts:
                processed_contact = {}
                for key, value in contact.items():
                    # Format specific fields for better readability
                    if key in ['createdon', 'modifiedon'] and value:
                        processed_contact[key] = self._format_datetime(value)
                    elif key == 'gendercode':
                        processed_contact[key] = self._format_gender(value)
                    elif key == 'statuscode':
                        processed_contact[key] = self._format_status(value)
                    else:
                        processed_contact[key] = value
                
                export_data['contacts'].append(processed_contact)
            
            # Write JSON file
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ JSON export completed: {len(self.contacts)} contacts")
            print(f"   📁 File: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {str(e)}")
            return None

    def export_to_excel(self, filename=None):
        """Export contacts to Excel format (requires pandas)."""
        try:
            if not PANDAS_AVAILABLE:
                print("❌ Excel export requires pandas. Install with: pip install pandas openpyxl")
                return None
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"dynamics_contacts_export_{timestamp}.xlsx"
            
            print(f"\n📄 Exporting to Excel: {filename}")
            
            if not self.contacts:
                print("❌ No contacts to export")
                return False
            
            # Prepare data for Excel
            excel_data = []
            for contact in self.contacts:
                row = {
                    'Contact ID': contact.get('contactid', ''),
                    'Full Name': contact.get('fullname', ''),
                    'First Name': contact.get('firstname', ''),
                    'Last Name': contact.get('lastname', ''),
                    'Primary Email': contact.get('emailaddress1', ''),
                    'Secondary Email': contact.get('emailaddress2', ''),
                    'Phone': contact.get('telephone1', ''),
                    'Mobile': contact.get('mobilephone', ''),
                    'Job Title': contact.get('jobtitle', ''),
                    'City': contact.get('address1_city', ''),
                    'State': contact.get('address1_stateorprovince', ''),
                    'Country': contact.get('address1_country', ''),
                    'Created On': self._format_datetime(contact.get('createdon')),
                    'Modified On': self._format_datetime(contact.get('modifiedon')),
                    'Status': self._format_status(contact.get('statuscode'))
                }
                excel_data.append(row)
            
            # Create Excel file with pandas
            df = pd.DataFrame(excel_data)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main contacts sheet
                df.to_excel(writer, sheet_name='Contacts', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Contacts',
                        'Contacts with Email',
                        'Contacts with Phone',
                        'Contacts with Company',
                        'Export Date',
                        'CRM URL'
                    ],
                    'Value': [
                        len(self.contacts),
                        len([c for c in self.contacts if c.get('emailaddress1')]),
                        len([c for c in self.contacts if c.get('telephone1') or c.get('mobilephone')]),
                        len([c for c in self.contacts if c.get('parentcustomerid')]),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        self.crm_base_url
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"✅ Excel export completed: {len(excel_data)} contacts")
            print(f"   📁 File: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            return None

    def show_contact_statistics(self):
        """Display detailed statistics about the contacts."""
        try:
            if not self.contacts:
                print("❌ No contacts available for statistics")
                return
            
            print("\n📊 CONTACT STATISTICS")
            print("="*50)
            
            total_contacts = len(self.contacts)
            
            # Basic statistics
            stats = [
                ['Total Contacts', total_contacts],
                ['Contacts with Email', len([c for c in self.contacts if c.get('emailaddress1')])],
                ['Contacts with Phone', len([c for c in self.contacts if c.get('telephone1') or c.get('mobilephone')])],
                ['Contacts with Company', len([c for c in self.contacts if c.get('parentcustomerid')])],
                ['Contacts with Address', len([c for c in self.contacts if c.get('address1_city')])],
                ['Contacts with Job Title', len([c for c in self.contacts if c.get('jobtitle')])]
            ]
            
            print(tabulate(stats, headers=['Metric', 'Count'], tablefmt='grid'))
            
            # Top companies
            companies = {}
            for contact in self.contacts:
                company = contact.get('parentcustomerid', 'No Company').strip()
                if company:
                    companies[company] = companies.get(company, 0) + 1
            
            if companies:
                print(f"\n🏢 Top 10 Companies:")
                top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
                print(tabulate(top_companies, headers=['Company', 'Contacts'], tablefmt='grid'))
            
            # Email domains
            domains = {}
            for contact in self.contacts:
                email = contact.get('emailaddress1', '')
                if email and '@' in email:
                    domain = email.split('@')[1].lower()
                    domains[domain] = domains.get(domain, 0) + 1
            
            if domains:
                print(f"\n📧 Top 10 Email Domains:")
                top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
                print(tabulate(top_domains, headers=['Domain', 'Contacts'], tablefmt='grid'))
            
        except Exception as e:
            print(f"❌ Error generating statistics: {str(e)}")

    def _format_datetime(self, dt_string):
        """Format datetime string for human readability."""
        if not dt_string:
            return ''
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(dt_string)

    def _format_gender(self, gender_code):
        """Format gender code to human readable."""
        gender_map = {1: 'Male', 2: 'Female'}
        return gender_map.get(gender_code, 'Not Specified')

    def _format_status(self, status_code):
        """Format status code to human readable."""
        status_map = {1: 'Active', 2: 'Inactive'}
        return status_map.get(status_code, 'Unknown')

    def run_complete_export(self):
        """Run the complete contact export process."""
        try:
            print("\n🚀 Starting Complete Contact Export")
            print("="*50)
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Download contacts
            if not self.get_all_contacts():
                return False
            
            # Step 3: Show statistics
            self.show_contact_statistics()
            
            # Step 4: Export to multiple formats
            print("\n📤 Exporting to multiple formats...")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # CSV Export
            csv_file = self.export_to_csv(f"dynamics_contacts_{timestamp}.csv")
            
            # JSON Export
            json_file = self.export_to_json(f"dynamics_contacts_{timestamp}.json")
            
            # Excel Export (if pandas available)
            excel_file = None
            if PANDAS_AVAILABLE:
                excel_file = self.export_to_excel(f"dynamics_contacts_{timestamp}.xlsx")
            
            # Summary
            print("\n🎉 Export process completed!")
            print("="*50)
            print("📁 Generated files:")
            if csv_file:
                print(f"   📄 CSV: {csv_file}")
            if json_file:
                print(f"   📄 JSON: {json_file}")
            if excel_file:
                print(f"   📄 Excel: {excel_file}")
            
            print(f"\n📊 Total contacts exported: {len(self.contacts)}")
            return True
            
        except Exception as e:
            print(f"❌ Error in complete export: {str(e)}")
            return False

def main():
    """Main function to run the contact exporter."""
    print("📊 DYNAMICS 365 CONTACT EXPORTER")
    print("="*50)
    print("🎯 Purpose: Download and export all CRM contacts in human-readable formats")
    print("📤 Formats: CSV, JSON, Excel (if pandas available)")
    print()
    
    # Configuration - update these credentials
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    
    # Create exporter instance
    exporter = Dynamics365ContactExporter(username, password)
    
    # Run complete export
    success = exporter.run_complete_export()
    
    if success:
        print("\n✅ Contact export completed successfully!")
        print("💡 Use the generated files for analysis and comparison")
    else:
        print("\n❌ Contact export failed!")
        print("💡 Check your credentials and network connection")

if __name__ == "__main__":
    main() 