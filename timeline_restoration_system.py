#!/usr/bin/env python3
"""
Timeline Restoration System - Restore complete email timelines in Dynamics 365 CRM
"""

import os
import sys
import json
import csv
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict
import win32com.client
import requests
import msal
from tabulate import tabulate

class TimelineRestorationSystem:
    def __init__(self, username, password, pst_path, tenant_domain=None):
        self.username = username
        self.password = password
        self.pst_path = pst_path
        self.tenant_domain = tenant_domain or username.split('@')[1]
        
        # Dynamics 365 configuration
        self.crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
        
        # Authentication and data storage
        self.access_token = None
        self.contacts = {}
        self.timeline_analysis = {}
        self.import_queue = []
        self.import_progress = {}
        
        # Import settings
        self.max_emails_per_batch = 10
        self.delay_between_emails = 2
        self.delay_between_batches = 10
        
        # Outlook COM objects
        self.outlook = None
        self.pst_store = None
        
        print("🔄 TIMELINE RESTORATION SYSTEM")
        print("="*70)
        print(f"👤 User: {self.username}")
        print(f"📁 PST File: {pst_path}")

    def authenticate(self):
        """Authenticate with Dynamics 365 using MSAL."""
        try:
            print("\n🔐 Starting authentication...")
            
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_domain}"
            )
            
            scopes = ["https://dynglobal.crm.dynamics.com/.default"]
            
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

    def load_timeline_analysis(self, analysis_file=None):
        """Load the timeline completeness analysis results."""
        try:
            if not analysis_file:
                # Find the most recent timeline analysis file
                analysis_files = [f for f in os.listdir('.') if f.startswith('timeline_analysis_') and f.endswith('.json')]
                if not analysis_files:
                    print("❌ No timeline analysis file found! Please run timeline_completeness_analyzer.py first.")
                    return False
                analysis_file = sorted(analysis_files)[-1]
            
            print(f"\n📊 Loading timeline analysis: {analysis_file}")
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            self.timeline_analysis = analysis_data.get('contact_analysis', {})
            analysis_info = analysis_data.get('analysis_info', {})
            
            print(f"✅ Timeline analysis loaded:")
            print(f"   📅 Analysis Date: {analysis_info.get('timestamp', 'Unknown')}")
            print(f"   👥 Contacts: {analysis_info.get('total_contacts', 0)}")
            print(f"   📧 Missing Emails: {analysis_info.get('total_missing_emails', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading timeline analysis: {str(e)}")
            return False

    def load_contacts_from_crm(self):
        """Load all contacts from Dynamics 365 CRM."""
        try:
            print("\n📥 Loading contacts from Dynamics 365...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            select_fields = [
                'contactid', 'fullname', 'firstname', 'lastname',
                'emailaddress1', 'emailaddress2', 'emailaddress3',
                'telephone1', 'mobilephone', 'jobtitle'
            ]
            
            select_query = ','.join(select_fields)
            url = f"{self.crm_base_url}/contacts?$select={select_query}&$top=5000"
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                contacts_list = data.get('value', [])
                
                for contact in contacts_list:
                    contact_id = contact.get('contactid')
                    if contact_id:
                        self.contacts[contact_id] = contact
                
                print(f"✅ Loaded {len(self.contacts)} contacts from CRM")
                return True
                
            else:
                print(f"❌ Error loading contacts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading contacts: {str(e)}")
            return False

    def create_import_queue(self):
        """Create prioritized import queue based on timeline analysis."""
        try:
            print("\n📋 Creating prioritized import queue...")
            
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for contact_id, analysis in self.timeline_analysis.items():
                contact = self.contacts.get(contact_id, {})
                if not contact:
                    continue
                
                missing_count = analysis.get('timeline_metrics', {}).get('missing_from_crm', 0)
                if missing_count == 0:
                    continue
                
                priority = analysis.get('timeline_metrics', {}).get('priority', 'Low')
                
                import_item = {
                    'contact_id': contact_id,
                    'contact_name': contact.get('fullname', 'Unknown'),
                    'contact_email': contact.get('emailaddress1', ''),
                    'missing_count': missing_count,
                    'priority': priority,
                    'analysis': analysis
                }
                
                if priority == 'High':
                    high_priority.append(import_item)
                elif priority == 'Medium':
                    medium_priority.append(import_item)
                else:
                    low_priority.append(import_item)
            
            # Sort each priority group by missing count (descending)
            high_priority.sort(key=lambda x: x['missing_count'], reverse=True)
            medium_priority.sort(key=lambda x: x['missing_count'], reverse=True)
            low_priority.sort(key=lambda x: x['missing_count'], reverse=True)
            
            # Combine into final queue
            self.import_queue = high_priority + medium_priority + low_priority
            
            print(f"✅ Import queue created:")
            print(f"   🔥 High Priority: {len(high_priority)} contacts")
            print(f"   🟡 Medium Priority: {len(medium_priority)} contacts")
            print(f"   🟢 Low Priority: {len(low_priority)} contacts")
            print(f"   📧 Total Missing Emails: {sum(item['missing_count'] for item in self.import_queue)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating import queue: {str(e)}")
            return False

    def show_import_plan(self):
        """Display the import plan for user review."""
        try:
            print("\n📋 TIMELINE RESTORATION IMPORT PLAN")
            print("="*60)
            
            if not self.import_queue:
                print("❌ No contacts in import queue")
                return
            
            # Show top 15 contacts in queue
            print("🎯 Top 15 Contacts for Timeline Restoration:")
            
            table_data = []
            total_emails = 0
            
            for i, item in enumerate(self.import_queue[:15], 1):
                table_data.append([
                    i,
                    item['contact_name'][:25] + ('...' if len(item['contact_name']) > 25 else ''),
                    item['missing_count'],
                    item['priority'],
                    item['contact_email'][:30] + ('...' if len(item['contact_email']) > 30 else '')
                ])
                total_emails += item['missing_count']
            
            headers = ['#', 'Contact', 'Missing', 'Priority', 'Email']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            # Summary
            print(f"\n📊 Import Summary:")
            print(f"   👥 Total Contacts: {len(self.import_queue)}")
            print(f"   📧 Total Missing Emails: {sum(item['missing_count'] for item in self.import_queue)}")
            print(f"   ⏱️  Estimated Time: {self._estimate_import_time()} minutes")
            
        except Exception as e:
            print(f"❌ Error showing import plan: {str(e)}")

    def _estimate_import_time(self):
        """Estimate total import time in minutes."""
        total_emails = sum(item['missing_count'] for item in self.import_queue)
        
        email_time = total_emails * self.delay_between_emails
        batch_count = (total_emails + self.max_emails_per_batch - 1) // self.max_emails_per_batch
        batch_time = batch_count * self.delay_between_batches
        
        total_seconds = email_time + batch_time
        return round(total_seconds / 60, 1)

    def open_pst_file(self):
        """Open PST file using Outlook COM interface."""
        try:
            print(f"\n📁 Opening PST file: {self.pst_path}")
            
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = self.outlook.GetNamespace("MAPI")
            
            namespace.AddStore(self.pst_path)
            
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

    def start_timeline_restoration(self, max_contacts=None, priority_only=False):
        """Start the timeline restoration process."""
        try:
            print("\n🚀 STARTING TIMELINE RESTORATION")
            print("="*60)
            
            if not self.import_queue:
                print("❌ No contacts in import queue")
                return False
            
            # Apply filters
            contacts_to_process = self.import_queue.copy()
            
            if priority_only:
                contacts_to_process = [c for c in contacts_to_process if c['priority'] in ['High', 'Medium']]
                print(f"🎯 Processing priority contacts only: {len(contacts_to_process)} contacts")
            
            if max_contacts:
                contacts_to_process = contacts_to_process[:max_contacts]
                print(f"🔢 Processing limited set: {max_contacts} contacts")
            
            total_contacts = len(contacts_to_process)
            total_emails = sum(c['missing_count'] for c in contacts_to_process)
            
            print(f"\n📊 Restoration Scope:")
            print(f"   👥 Contacts: {total_contacts}")
            print(f"   📧 Total Emails: {total_emails}")
            
            # Confirm before starting
            print(f"\n⚠️  This will import {total_emails} emails to Dynamics 365.")
            confirmation = input("🤔 Continue with timeline restoration? (yes/no): ").strip().lower()
            
            if confirmation not in ['yes', 'y']:
                print("❌ Timeline restoration cancelled by user")
                return False
            
            # Initialize progress tracking
            self.import_progress = {
                'start_time': time.time(),  # Use time.time() for consistent timing
                'contacts_processed': 0,
                'emails_imported': 0,
                'errors': 0
            }
            
            print("\n🔄 Starting ACTUAL timeline restoration...")
            print("📧 This will create real email activities in Dynamics 365!")
            
            # Process each contact for real
            for i, contact_item in enumerate(contacts_to_process, 1):
                success = self._process_contact_timeline_real(contact_item, i, total_contacts)
                
                if success:
                    self.import_progress['contacts_processed'] += 1
                
                # Batch delay between contacts
                if i < total_contacts:
                    print(f"   ⏸️  Batch delay: {self.delay_between_batches}s...")
                    time.sleep(self.delay_between_batches)
            
            # Show final results
            self._show_restoration_results()
            
            print(f"\n✅ Timeline restoration completed!")
            print(f"📊 Processed {self.import_progress['contacts_processed']} contacts")
            print(f"📧 Imported {self.import_progress['emails_imported']} emails")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in timeline restoration: {str(e)}")
            return False

    def _process_contact_timeline_real(self, contact_item, contact_num, total_contacts):
        """Actually process and import emails for a contact"""
        try:
            print(f"\n📋 Processing Contact {contact_num}/{total_contacts}")
            print(f"   👤 Name: {contact_item['contact_name']}")
            print(f"   📧 Email: {contact_item['contact_email']}")
            print(f"   📊 Missing Emails: {contact_item['missing_count']}")
            
            # Get PST emails for this contact
            contact_emails = self._get_pst_emails_for_contact(contact_item['contact_email'])
            
            if not contact_emails:
                print(f"   ⚠️  No PST emails found for {contact_item['contact_email']}")
                return False
            
            # Limit to expected missing count
            contact_emails = contact_emails[:contact_item['missing_count']]
            
            # Import emails in batches
            imported_count = 0
            batch_size = 5  # Smaller batches for better error handling
            
            for batch_start in range(0, len(contact_emails), batch_size):
                batch_emails = contact_emails[batch_start:batch_start + batch_size]
                batch_num = (batch_start // batch_size) + 1
                total_batches = (len(contact_emails) + batch_size - 1) // batch_size
                
                print(f"   📦 Processing batch {batch_num}/{total_batches} ({len(batch_emails)} emails)...")
                
                batch_success = self._import_email_batch(batch_emails, contact_item)
                if batch_success:
                    imported_count += len(batch_emails)
                    print(f"   ✅ Batch {batch_num} imported successfully!")
                else:
                    print(f"   ❌ Batch {batch_num} failed!")
                
                # Delay between batches
                if batch_start + batch_size < len(contact_emails):
                    print(f"   ⏸️  Batch delay: 2s...")
                    time.sleep(2)
            
            print(f"   ✅ Contact completed: {imported_count}/{len(contact_emails)} emails imported")
            self.import_progress['emails_imported'] += imported_count
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing contact {contact_item['contact_name']}: {str(e)}")
            return False
    
    def _get_pst_emails_for_contact(self, contact_email):
        """Extract emails for a specific contact from PST using Outlook COM"""
        try:
            contact_emails = []
            
            # Access the root folder of the PST
            root_folder = self.pst_store.GetRootFolder()
            
            # Search through folders recursively
            self._search_folder_for_emails(root_folder, contact_email, contact_emails)
            
            # Sort by received time (newest first)
            contact_emails.sort(key=lambda x: x.get('received_time') or x.get('sent_time') or '', reverse=True)
            
            print(f"   📧 Found {len(contact_emails)} emails for {contact_email}")
            return contact_emails
            
        except Exception as e:
            print(f"   ❌ Error extracting PST emails for {contact_email}: {str(e)}")
            return []
    
    def _search_folder_for_emails(self, folder, contact_email, contact_emails):
        """Recursively search folder for emails involving the contact"""
        try:
            # Search messages in current folder
            for message in folder.Items:
                try:
                    # Check if this is an email
                    if message.Class == 43:  # olMail
                        # Check if contact is involved
                        sender = getattr(message, 'SenderEmailAddress', '') or ''
                        recipients = []
                        
                        # Get recipients
                        try:
                            for recipient in message.Recipients:
                                rec_email = getattr(recipient, 'Address', '') or ''
                                recipients.append(rec_email)
                        except:
                            pass
                        
                        involved = False
                        
                        # Check sender
                        if contact_email.lower() in sender.lower():
                            involved = True
                        
                        # Check recipients
                        if not involved:
                            for rec_email in recipients:
                                if contact_email.lower() in rec_email.lower():
                                    involved = True
                                    break
                        
                        if involved:
                            email_data = {
                                'subject': getattr(message, 'Subject', '') or 'No Subject',
                                'sender': sender,
                                'recipients': recipients,
                                'received_time': getattr(message, 'ReceivedTime', None),
                                'sent_time': getattr(message, 'SentOn', None),
                                'body': getattr(message, 'Body', '') or '',
                                'html_body': getattr(message, 'HTMLBody', '') or '',
                                'size': getattr(message, 'Size', 0)
                            }
                            contact_emails.append(email_data)
                            
                except Exception:
                    # Skip problematic messages
                    continue
            
            # Search subfolders recursively
            try:
                for subfolder in folder.Folders:
                    self._search_folder_for_emails(subfolder, contact_email, contact_emails)
            except:
                pass
                
        except Exception:
            # Skip problematic folders
            pass
    
    def _import_email_batch(self, email_batch, contact_item):
        """Import a batch of emails to Dynamics 365"""
        try:
            for email_data in email_batch:
                success = self._create_email_activity(email_data, contact_item)
                if not success:
                    return False
                    
                # Small delay between individual emails
                time.sleep(0.2)
                    
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing email batch: {str(e)}")
            return False
    
    def _create_email_activity(self, email_data, contact_item):
        """Create an email activity in Dynamics 365"""
        try:
            # Prepare email activity data
            sent_time = email_data.get('sent_time') or email_data.get('received_time')
            subject = email_data.get('subject', 'No Subject')[:200]  # Limit length
            body = (email_data.get('body', '') or email_data.get('html_body', ''))[:2000]  # Limit length
            
            activity_data = {
                'subject': subject,
                'description': body,
                'directioncode': True,  # Outgoing (assume outgoing for now)
                'regardingobjectid_contact@odata.bind': f"{self.crm_base_url}/contacts({contact_item['contact_id']})"
            }
            
            # Add timing if available  
            if sent_time:
                try:
                    # Convert to ISO format
                    if hasattr(sent_time, 'isoformat'):
                        time_str = sent_time.isoformat()
                    else:
                        time_str = str(sent_time)
                    
                    activity_data['actualend'] = time_str
                    activity_data['actualstart'] = time_str
                except Exception:
                    pass
            
            # Make API call to create email activity with contact relationship
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Prefer': 'return=representation'
            }
            
            # Create the email first
            response = requests.post(
                f"{self.crm_base_url}/emails",
                json=activity_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 204]:
                # 204 means successful creation with no content returned
                if response.status_code == 204:
                    return True  # Email created and linked successfully
                
                # For 200/201, we can get the ID and update state
                email_response = response.json()
                email_id = email_response.get('activityid')
                
                if email_id:
                    # Now set the email to completed state
                    state_data = {
                        'statecode': 1,  # Completed
                        'statuscode': 3   # Sent
                    }
                    
                    state_response = requests.patch(
                        f"{self.crm_base_url}/emails({email_id})",
                        json=state_data,
                        headers=headers,
                        timeout=30
                    )
                    
                    if state_response.status_code in [200, 204]:
                        return True
                    else:
                        print(f"   ⚠️  State update warning {state_response.status_code}: {state_response.text[:100]}")
                        return True  # Still consider successful since email was created and linked
                else:
                    print(f"   ❌ No email ID returned from creation")
                    return False
            else:
                error_text = response.text[:200] if response.text else 'No error details'
                print(f"   ❌ API Error {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating email activity: {str(e)}")
            return False
    
    def _show_restoration_results(self):
        """Display final restoration results"""
        elapsed_time = time.time() - self.import_progress['start_time']
        print(f"\n🎯 TIMELINE RESTORATION RESULTS:")
        print(f"   👥 Contacts Processed: {self.import_progress['contacts_processed']}")
        print(f"   📧 Emails Imported: {self.import_progress['emails_imported']}")
        print(f"   ⏱️  Total Time: {elapsed_time:.1f} seconds")
        print(f"   📈 Rate: {self.import_progress['emails_imported'] / max(elapsed_time/60, 0.1):.1f} emails/minute")

    def close_pst_file(self):
        """Close PST file and clean up."""
        try:
            if self.pst_store:
                self.pst_store = None
            self.outlook = None
            print("✅ PST file closed")
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")

    def run_timeline_restoration(self, max_contacts=None, priority_only=False):
        """Run the complete timeline restoration process."""
        try:
            print("\n🚀 Timeline Restoration System")
            print("="*60)
            print("🎯 Goal: Restore complete email timelines in Dynamics 365 CRM")
            print("📧 Source: PST file email history")
            print("🔄 Method: Strategic priority-based import")
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Load timeline analysis
            if not self.load_timeline_analysis():
                return False
            
            # Step 3: Load contacts from CRM
            if not self.load_contacts_from_crm():
                return False
            
            # Step 4: Create import queue
            if not self.create_import_queue():
                return False
            
            # Step 5: Show import plan
            self.show_import_plan()
            
            # Step 6: Open PST file
            if not self.open_pst_file():
                return False
            
            # Step 7: Start restoration
            success = self.start_timeline_restoration(max_contacts, priority_only)
            
            # Step 8: Cleanup
            self.close_pst_file()
            
            if success:
                print("\n🌟 Timeline restoration system demonstrated successfully!")
                print("💡 This system is ready to restore your Dynamics 365 timelines!")
            else:
                print("\n⚠️  Timeline restoration system encountered issues")
            
            return success
            
        except Exception as e:
            print(f"❌ Error in timeline restoration: {str(e)}")
            self.close_pst_file()
            return False

def main():
    """Main function to run the timeline restoration system."""
    print("🔄 TIMELINE RESTORATION SYSTEM")
    print("="*70)
    print("🎯 Purpose: Restore complete email timelines in Dynamics 365 CRM")
    print("📊 Source: Timeline completeness analysis + PST emails")
    print("🚀 Method: Strategic priority-based import with rate limiting")
    print()
    
    # Configuration
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    # Create restoration system
    restoration_system = TimelineRestorationSystem(username, password, pst_path)
    
    # Options for restoration
    print("🔧 Restoration Options:")
    print("   1. Start with high-priority contacts only (recommended)")
    print("   2. Restore all timelines (full restoration)")
    print("   3. Test with limited contacts (3 contacts max)")
    
    choice = input("\n🤔 Choose restoration option (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🎯 Starting with high-priority contacts...")
        success = restoration_system.run_timeline_restoration(priority_only=True)
    elif choice == "2":
        print("\n🔄 Starting full timeline restoration...")
        success = restoration_system.run_timeline_restoration()
    elif choice == "3":
        print("\n🧪 Starting test restoration with 3 contacts...")
        success = restoration_system.run_timeline_restoration(max_contacts=3)
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    if success:
        print("\n✅ Timeline restoration system completed successfully!")
        print("🌟 Your system is ready to restore Dynamics 365 timelines!")
    else:
        print("\n❌ Timeline restoration system encountered issues!")

if __name__ == "__main__":
    main() 