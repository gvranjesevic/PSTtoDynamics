#!/usr/bin/env python3
"""
PST Contact Analyzer
===================

This script analyzes PST files to extract email addresses and compares them
with existing Dynamics 365 CRM contacts to identify:
- Email addresses in PST that are NOT in CRM
- Contacts in CRM that have no PST email activity
- Statistics and recommendations for contact management

Features:
- PST email extraction and analysis
- CRM contact comparison
- Gap analysis and reporting
- Contact recommendations
- Export results in multiple formats

Author: AI Assistant
Date: December 2024
"""

import os
import sys
import json
import csv
import time
import re
from datetime import datetime
from collections import defaultdict
import win32com.client
from tabulate import tabulate

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available - Excel export will be disabled")

class PSTContactAnalyzer:
    def __init__(self, pst_path, crm_contacts_file=None):
        """Initialize the PST Contact Analyzer."""
        self.pst_path = pst_path
        self.crm_contacts_file = crm_contacts_file
        
        # Data storage
        self.pst_emails = {}  # email -> {name, count, first_seen, last_seen, folders}
        self.crm_contacts = {}  # email -> contact_data
        self.gap_analysis = {
            'in_pst_not_crm': {},
            'in_crm_not_pst': {},
            'in_both': {},
            'stats': {}
        }
        
        # Outlook COM objects
        self.outlook = None
        self.pst_store = None
        
        print("🔍 PST CONTACT ANALYZER")
        print("="*50)
        print(f"📁 PST File: {pst_path}")
        print(f"📊 CRM Contacts: {crm_contacts_file}")

    def load_crm_contacts(self):
        """Load CRM contacts from exported file (JSON or CSV)."""
        try:
            if not self.crm_contacts_file:
                print("⚠️  No CRM contacts file provided - will only analyze PST")
                return True
                
            if not os.path.exists(self.crm_contacts_file):
                print(f"❌ CRM contacts file not found: {self.crm_contacts_file}")
                return False
            
            print(f"\n📥 Loading CRM contacts from: {self.crm_contacts_file}")
            
            file_ext = os.path.splitext(self.crm_contacts_file)[1].lower()
            
            if file_ext == '.json':
                return self._load_from_json()
            elif file_ext == '.csv':
                return self._load_from_csv()
            else:
                print(f"❌ Unsupported file format: {file_ext}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading CRM contacts: {str(e)}")
            return False

    def _load_from_json(self):
        """Load contacts from JSON export file."""
        try:
            with open(self.crm_contacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            contacts = data.get('contacts', []) if isinstance(data, dict) else data
            
            for contact in contacts:
                # Extract email addresses
                emails = []
                for email_field in ['emailaddress1', 'emailaddress2', 'emailaddress3', 'Primary Email']:
                    email = contact.get(email_field)
                    if email:
                        email = str(email).strip().lower()
                        if email and '@' in email:
                            emails.append(email)
                
                # Store contact data for each email
                for email in emails:
                    self.crm_contacts[email] = {
                        'full_name': str(contact.get('fullname') or contact.get('Full Name') or ''),
                        'first_name': str(contact.get('firstname') or contact.get('First Name') or ''),
                        'last_name': str(contact.get('lastname') or contact.get('Last Name') or ''),
                        'company': str(contact.get('companyname') or contact.get('Company') or ''),
                        'job_title': str(contact.get('jobtitle') or contact.get('Job Title') or ''),
                        'phone': str(contact.get('telephone1') or contact.get('Phone') or ''),
                        'contact_id': str(contact.get('contactid') or contact.get('Contact ID') or ''),
                        'primary_email': emails[0] if emails else email
                    }
            
            print(f"✅ Loaded {len(self.crm_contacts)} email addresses from {len(contacts)} CRM contacts")
            return True
            
        except Exception as e:
            print(f"❌ Error loading JSON file: {str(e)}")
            return False

    def _load_from_csv(self):
        """Load contacts from CSV export file."""
        try:
            with open(self.crm_contacts_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                contacts = list(reader)
            
            for contact in contacts:
                # Extract email addresses
                emails = []
                for email_field in ['Primary Email', 'Secondary Email', 'Third Email', 'emailaddress1']:
                    email = contact.get(email_field)
                    if email:
                        email = str(email).strip().lower()
                        if email and '@' in email:
                            emails.append(email)
                
                # Store contact data for each email
                for email in emails:
                    self.crm_contacts[email] = {
                        'full_name': str(contact.get('Full Name') or ''),
                        'first_name': str(contact.get('First Name') or ''),
                        'last_name': str(contact.get('Last Name') or ''),
                        'company': str(contact.get('Company') or ''),
                        'job_title': str(contact.get('Job Title') or ''),
                        'phone': str(contact.get('Phone') or contact.get('Phone 1') or ''),
                        'contact_id': str(contact.get('Contact ID') or ''),
                        'primary_email': emails[0] if emails else email
                    }
            
            print(f"✅ Loaded {len(self.crm_contacts)} email addresses from {len(contacts)} CRM contacts")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV file: {str(e)}")
            return False

    def open_pst_file(self):
        """Open PST file using Outlook COM interface."""
        try:
            print(f"\n📁 Opening PST file: {self.pst_path}")
            
            # Initialize Outlook
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = self.outlook.GetNamespace("MAPI")
            
            # Add PST file to Outlook
            namespace.AddStore(self.pst_path)
            
            # Find the PST store
            for store in namespace.Stores:
                if self.pst_path.lower() in store.FilePath.lower():
                    self.pst_store = store
                    break
            
            if not self.pst_store:
                print(f"❌ Could not find PST store for: {self.pst_path}")
                return False
            
            print(f"✅ PST file opened: {self.pst_store.DisplayName}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening PST file: {str(e)}")
            return False

    def extract_pst_emails(self):
        """Extract all email addresses from PST file."""
        try:
            print(f"\n🔍 Extracting email addresses from PST file...")
            
            # Start with root folder
            root_folder = self.pst_store.GetRootFolder()
            self._process_folder(root_folder, "")
            
            print(f"\n📊 PST email extraction completed:")
            print(f"   📧 Unique email addresses: {len(self.pst_emails)}")
            print(f"   📂 Total messages processed")
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting PST emails: {str(e)}")
            return False

    def _process_folder(self, folder, folder_path):
        """Recursively process folders and extract email addresses."""
        try:
            current_path = f"{folder_path}/{folder.Name}" if folder_path else folder.Name
            
            # Process messages in current folder
            messages = folder.Items
            message_count = messages.Count
            
            if message_count > 0:
                print(f"   📂 Processing folder: {current_path} ({message_count} messages)")
                
                for i in range(1, min(message_count + 1, 1001)):  # Limit to avoid timeout
                    try:
                        message = messages[i]
                        
                        # Extract sender email
                        if hasattr(message, 'SenderEmailAddress') and message.SenderEmailAddress:
                            sender_email = message.SenderEmailAddress.lower().strip()
                            sender_name = getattr(message, 'SenderName', '')
                            
                            # Skip system/internal emails
                            if self._is_valid_email(sender_email):
                                self._add_email_to_collection(sender_email, sender_name, current_path, message)
                        
                        # Extract recipient emails
                        if hasattr(message, 'Recipients'):
                            for recipient in message.Recipients:
                                if hasattr(recipient, 'Address') and recipient.Address:
                                    recipient_email = recipient.Address.lower().strip()
                                    recipient_name = getattr(recipient, 'Name', '')
                                    
                                    if self._is_valid_email(recipient_email):
                                        self._add_email_to_collection(recipient_email, recipient_name, current_path, message)
                        
                    except Exception as e:
                        # Skip problematic messages
                        continue
            
            # Process subfolders
            for subfolder in folder.Folders:
                self._process_folder(subfolder, current_path)
                
        except Exception as e:
            print(f"⚠️  Error processing folder {folder_path}: {str(e)}")

    def _is_valid_email(self, email):
        """Check if email address is valid and not system-generated."""
        if not email or '@' not in email:
            return False
        
        # Skip system emails
        skip_patterns = [
            r'/o=',  # Exchange internal format
            r'/ou=',  # Exchange organizational unit
            r'[a-f0-9]{32}@',  # GUID-based emails
            r'postmaster@',
            r'mailer-daemon@',
            r'noreply@',
            r'no-reply@'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        return True

    def _add_email_to_collection(self, email, name, folder_path, message):
        """Add email to collection with metadata."""
        try:
            # Get message date
            message_date = None
            if hasattr(message, 'ReceivedTime'):
                message_date = message.ReceivedTime
            elif hasattr(message, 'SentOn'):
                message_date = message.SentOn
            
            if email not in self.pst_emails:
                self.pst_emails[email] = {
                    'name': name,
                    'count': 0,
                    'first_seen': message_date,
                    'last_seen': message_date,
                    'folders': set()
                }
            
            # Update statistics
            self.pst_emails[email]['count'] += 1
            self.pst_emails[email]['folders'].add(folder_path)
            
            if message_date:
                if not self.pst_emails[email]['first_seen'] or message_date < self.pst_emails[email]['first_seen']:
                    self.pst_emails[email]['first_seen'] = message_date
                if not self.pst_emails[email]['last_seen'] or message_date > self.pst_emails[email]['last_seen']:
                    self.pst_emails[email]['last_seen'] = message_date
            
            # Update name if current one is better
            if name and (not self.pst_emails[email]['name'] or len(name) > len(self.pst_emails[email]['name'])):
                self.pst_emails[email]['name'] = name
                
        except Exception as e:
            # Skip problematic entries
            pass

    def perform_gap_analysis(self):
        """Perform gap analysis between PST emails and CRM contacts."""
        try:
            print(f"\n🔍 Performing gap analysis...")
            
            # Find emails in PST but not in CRM
            for email, data in self.pst_emails.items():
                if email in self.crm_contacts:
                    self.gap_analysis['in_both'][email] = {
                        'pst_data': data,
                        'crm_data': self.crm_contacts[email]
                    }
                else:
                    self.gap_analysis['in_pst_not_crm'][email] = data
            
            # Find emails in CRM but not in PST
            for email, data in self.crm_contacts.items():
                if email not in self.pst_emails:
                    self.gap_analysis['in_crm_not_pst'][email] = data
            
            # Calculate statistics
            self.gap_analysis['stats'] = {
                'total_pst_emails': len(self.pst_emails),
                'total_crm_emails': len(self.crm_contacts),
                'in_both': len(self.gap_analysis['in_both']),
                'pst_only': len(self.gap_analysis['in_pst_not_crm']),
                'crm_only': len(self.gap_analysis['in_crm_not_pst'])
            }
            
            print(f"✅ Gap analysis completed")
            return True
            
        except Exception as e:
            print(f"❌ Error performing gap analysis: {str(e)}")
            return False

    def show_analysis_results(self):
        """Display detailed analysis results."""
        try:
            print("\n📊 CONTACT GAP ANALYSIS RESULTS")
            print("="*60)
            
            stats = self.gap_analysis['stats']
            
            # Summary statistics
            summary = [
                ['Total PST Email Addresses', stats['total_pst_emails']],
                ['Total CRM Email Addresses', stats['total_crm_emails']],
                ['Present in Both', stats['in_both']],
                ['PST Only (Missing from CRM)', stats['pst_only']],
                ['CRM Only (No PST Activity)', stats['crm_only']]
            ]
            
            print(tabulate(summary, headers=['Metric', 'Count'], tablefmt='grid'))
            
            # Top missing contacts (PST only)
            if self.gap_analysis['in_pst_not_crm']:
                print(f"\n📧 Top 20 Email Addresses in PST but NOT in CRM:")
                pst_only = sorted(
                    self.gap_analysis['in_pst_not_crm'].items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )[:20]
                
                pst_table = []
                for email, data in pst_only:
                    name = data['name'] if data['name'] else 'Unknown'
                    count = data['count']
                    folders = len(data['folders'])
                    pst_table.append([email, name, count, folders])
                
                print(tabulate(pst_table, headers=['Email', 'Name', 'Messages', 'Folders'], tablefmt='grid'))
            
            # Coverage analysis
            if stats['total_pst_emails'] > 0:
                coverage = (stats['in_both'] / stats['total_pst_emails']) * 100
                print(f"\n📈 CRM Coverage: {coverage:.1f}% of PST emails are in CRM")
            
        except Exception as e:
            print(f"❌ Error showing analysis results: {str(e)}")

    def export_missing_contacts(self, filename=None):
        """Export missing contacts (PST only) to CSV for potential import."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"missing_contacts_for_import_{timestamp}.csv"
            
            print(f"\n📤 Exporting missing contacts to: {filename}")
            
            missing_contacts = []
            for email, data in self.gap_analysis['in_pst_not_crm'].items():
                # Parse name into first/last
                name = data['name'].strip() if data['name'] else ''
                if name:
                    name_parts = name.split()
                    first_name = name_parts[0] if name_parts else ''
                    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                else:
                    first_name = ''
                    last_name = ''
                
                # Format dates
                first_seen = data['first_seen'].strftime('%Y-%m-%d') if data['first_seen'] else ''
                last_seen = data['last_seen'].strftime('%Y-%m-%d') if data['last_seen'] else ''
                
                contact_row = {
                    'Email Address': email,
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Full Name': name,
                    'Message Count': data['count'],
                    'Folder Count': len(data['folders']),
                    'First Seen': first_seen,
                    'Last Seen': last_seen,
                    'Priority': 'High' if data['count'] >= 10 else 'Medium' if data['count'] >= 3 else 'Low',
                    'Folders': '; '.join(list(data['folders'])[:3])  # First 3 folders
                }
                missing_contacts.append(contact_row)
            
            # Sort by message count (highest first)
            missing_contacts.sort(key=lambda x: x['Message Count'], reverse=True)
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if missing_contacts:
                    fieldnames = missing_contacts[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(missing_contacts)
            
            print(f"✅ Exported {len(missing_contacts)} missing contacts")
            print(f"   📁 File: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting missing contacts: {str(e)}")
            return None

    def export_full_analysis(self, filename=None):
        """Export complete analysis to JSON."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"pst_contact_analysis_{timestamp}.json"
            
            print(f"\n📤 Exporting full analysis to: {filename}")
            
            # Prepare export data
            export_data = {
                'analysis_info': {
                    'timestamp': datetime.now().isoformat(),
                    'pst_file': self.pst_path,
                    'crm_file': self.crm_contacts_file,
                    'statistics': self.gap_analysis['stats']
                },
                'pst_emails': {},
                'gap_analysis': {
                    'in_pst_not_crm': {},
                    'in_crm_not_pst': {},
                    'in_both': {}
                }
            }
            
            # Convert PST emails (handle datetime serialization)
            for email, data in self.pst_emails.items():
                export_data['pst_emails'][email] = {
                    'name': data['name'],
                    'count': data['count'],
                    'first_seen': data['first_seen'].isoformat() if data['first_seen'] else None,
                    'last_seen': data['last_seen'].isoformat() if data['last_seen'] else None,
                    'folders': list(data['folders'])
                }
            
            # Convert gap analysis
            for category in ['in_pst_not_crm', 'in_crm_not_pst', 'in_both']:
                for email, data in self.gap_analysis[category].items():
                    if category == 'in_pst_not_crm':
                        export_data['gap_analysis'][category][email] = {
                            'name': data['name'],
                            'count': data['count'],
                            'first_seen': data['first_seen'].isoformat() if data['first_seen'] else None,
                            'last_seen': data['last_seen'].isoformat() if data['last_seen'] else None,
                            'folders': list(data['folders'])
                        }
                    elif category == 'in_crm_not_pst':
                        export_data['gap_analysis'][category][email] = data
                    else:  # in_both
                        export_data['gap_analysis'][category][email] = {
                            'pst_data': {
                                'name': data['pst_data']['name'],
                                'count': data['pst_data']['count'],
                                'first_seen': data['pst_data']['first_seen'].isoformat() if data['pst_data']['first_seen'] else None,
                                'last_seen': data['pst_data']['last_seen'].isoformat() if data['pst_data']['last_seen'] else None,
                                'folders': list(data['pst_data']['folders'])
                            },
                            'crm_data': data['crm_data']
                        }
            
            # Write JSON
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Full analysis exported")
            print(f"   📁 File: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting full analysis: {str(e)}")
            return None

    def close_pst_file(self):
        """Close PST file and clean up."""
        try:
            if self.pst_store:
                # Note: We don't remove the store as it might be in use
                self.pst_store = None
            self.outlook = None
            print("✅ PST file closed")
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")

    def run_complete_analysis(self):
        """Run the complete PST contact analysis."""
        try:
            print("\n🚀 Starting Complete PST Contact Analysis")
            print("="*60)
            
            # Step 1: Load CRM contacts
            if not self.load_crm_contacts():
                print("⚠️  Continuing without CRM contacts")
            
            # Step 2: Open PST file
            if not self.open_pst_file():
                return False
            
            # Step 3: Extract PST emails
            if not self.extract_pst_emails():
                return False
            
            # Step 4: Perform gap analysis (if CRM data available)
            if self.crm_contacts:
                if not self.perform_gap_analysis():
                    return False
                
                # Step 5: Show results
                self.show_analysis_results()
                
                # Step 6: Export results
                print("\n📤 Exporting analysis results...")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                missing_file = self.export_missing_contacts(f"missing_contacts_{timestamp}.csv")
                analysis_file = self.export_full_analysis(f"analysis_{timestamp}.json")
                
                print("\n🎉 Analysis completed!")
                print("="*50)
                print("📁 Generated files:")
                if missing_file:
                    print(f"   📄 Missing Contacts: {missing_file}")
                if analysis_file:
                    print(f"   📄 Full Analysis: {analysis_file}")
                
            else:
                print("\n📊 PST Email Statistics (CRM comparison not available)")
                print("="*60)
                print(f"Total unique email addresses found: {len(self.pst_emails)}")
                
                # Show top emails by message count
                top_emails = sorted(self.pst_emails.items(), key=lambda x: x[1]['count'], reverse=True)[:20]
                email_table = []
                for email, data in top_emails:
                    name = data['name'] if data['name'] else 'Unknown'
                    count = data['count']
                    folders = len(data['folders'])
                    email_table.append([email, name, count, folders])
                
                print(tabulate(email_table, headers=['Email', 'Name', 'Messages', 'Folders'], tablefmt='grid'))
            
            # Step 7: Cleanup
            self.close_pst_file()
            return True
            
        except Exception as e:
            print(f"❌ Error in complete analysis: {str(e)}")
            self.close_pst_file()
            return False

def main():
    """Main function to run the PST contact analyzer."""
    print("🔍 PST CONTACT ANALYZER")
    print("="*50)
    print("🎯 Purpose: Analyze PST emails and compare with CRM contacts")
    print("📊 Outputs: Gap analysis, missing contacts, recommendations")
    print()
    
    # Configuration
    pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    crm_contacts_file = None  # Will look for exported CRM files
    
    # Try to find the most recent CRM export file
    crm_files = []
    for file in os.listdir('.'):
        if file.startswith('dynamics_contacts_') and (file.endswith('.json') or file.endswith('.csv')):
            crm_files.append(file)
    
    if crm_files:
        # Use the most recent file
        crm_contacts_file = max(crm_files, key=os.path.getmtime)
        print(f"📊 Found CRM export file: {crm_contacts_file}")
    else:
        print("⚠️  No CRM export file found. Run dynamics_contact_exporter.py first for comparison.")
    
    # Create analyzer instance
    analyzer = PSTContactAnalyzer(pst_path, crm_contacts_file)
    
    # Run complete analysis
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ PST contact analysis completed successfully!")
        print("💡 Use the generated files to identify contacts to add to CRM")
    else:
        print("\n❌ PST contact analysis failed!")
        print("💡 Check your PST file path and permissions")

if __name__ == "__main__":
    main() 