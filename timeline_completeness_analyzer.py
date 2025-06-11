#!/usr/bin/env python3
"""
Timeline Completeness Analyzer
==============================

This script analyzes the completeness of email timelines in Dynamics 365 CRM
by comparing existing email activities with emails found in PST files.

Features:
- Downloads all email activities from Dynamics 365 for each contact
- Extracts detailed email information from PST files
- Compares CRM timelines with PST emails to identify gaps
- Generates completeness reports and recommendations
- Provides contact-specific timeline analysis

Author: AI Assistant
Date: December 2024
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

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available - Excel export will be disabled")

class TimelineCompletenessAnalyzer:
    def __init__(self, username, password, pst_path, tenant_domain=None):
        """Initialize the Timeline Completeness Analyzer."""
        self.username = username
        self.password = password
        self.pst_path = pst_path
        self.tenant_domain = tenant_domain or username.split('@')[1]
        
        # Dynamics 365 configuration
        self.crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
        
        # Authentication and data storage
        self.access_token = None
        self.contacts = {}  # contact_id -> contact_data
        self.crm_activities = {}  # contact_id -> [email_activities]
        self.pst_emails = {}  # contact_email -> [email_data]
        self.timeline_analysis = {}  # contact_id -> analysis_data
        
        # Outlook COM objects
        self.outlook = None
        self.pst_store = None
        
        print("📊 TIMELINE COMPLETENESS ANALYZER")
        print("="*60)
        print(f"👤 User: {self.username}")
        print(f"🏢 Tenant: {self.tenant_domain}")
        print(f"🌐 CRM URL: {self.crm_base_url}")
        print(f"📁 PST File: {pst_path}")

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
            
            # Get contacts with essential fields
            select_fields = [
                'contactid', 'fullname', 'firstname', 'lastname',
                'emailaddress1', 'emailaddress2', 'emailaddress3',
                'telephone1', 'mobilephone', 'jobtitle',
                'createdon', 'modifiedon'
            ]
            
            select_query = ','.join(select_fields)
            url = f"{self.crm_base_url}/contacts?$select={select_query}&$top=5000"
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                contacts_list = data.get('value', [])
                
                # Store contacts by ID and email
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

    def get_contact_email_activities(self, contact_id):
        """Get all email activities for a specific contact."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            # Query ALL email activities first, then we'll filter based on activity parties
            select_fields = [
                'activityid', 'subject', 'description', 'createdon', 'modifiedon',
                'actualstart', 'actualend', 'senton', 'directioncode',
                'sender', 'torecipients'
            ]
            
            select_query = ','.join(select_fields)
            expand_query = "email_activity_parties($select=participationtypemask,partyid,addressused)"
            url = f"{self.crm_base_url}/emails?$select={select_query}&$expand={expand_query}&$top=500"
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_emails = data.get('value', [])
                
                # Filter emails that involve this contact
                contact_emails = []
                for email in all_emails:
                    # Check if this contact is involved through activity parties
                    activity_parties = email.get('email_activity_parties', [])
                    for party in activity_parties:
                        if party.get('partyid') and party.get('partyid').get('contactid') == contact_id:
                            contact_emails.append(email)
                            break
                
                return contact_emails
            else:
                # Try simpler approach - just get emails regarding this contact
                filter_query = f"_regardingobjectid_value eq {contact_id}"
                simple_url = f"{self.crm_base_url}/emails?$filter={filter_query}&$select={select_query}&$top=1000"
                
                simple_response = requests.get(simple_url, headers=headers, timeout=30)
                if simple_response.status_code == 200:
                    simple_data = simple_response.json()
                    return simple_data.get('value', [])
                else:
                    print(f"⚠️  Error getting activities for contact {contact_id}: {response.status_code}")
                    return []
                
        except Exception as e:
            print(f"⚠️  Error getting activities for contact {contact_id}: {str(e)}")
            return []

    def load_all_contact_activities(self):
        """Load email activities for all contacts."""
        try:
            print(f"\n📧 Loading email activities for {len(self.contacts)} contacts...")
            
            total_activities = 0
            for i, (contact_id, contact) in enumerate(self.contacts.items(), 1):
                contact_name = contact.get('fullname', 'Unknown')
                print(f"   📋 {i}/{len(self.contacts)}: {contact_name}")
                
                activities = self.get_contact_email_activities(contact_id)
                self.crm_activities[contact_id] = activities
                total_activities += len(activities)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            print(f"✅ Loaded {total_activities} email activities across all contacts")
            return True
            
        except Exception as e:
            print(f"❌ Error loading contact activities: {str(e)}")
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

    def extract_pst_emails_by_contact(self):
        """Extract emails from PST file organized by contact email address."""
        try:
            print(f"\n🔍 Extracting emails from PST for timeline comparison...")
            
            # Get all email addresses from contacts
            contact_emails = set()
            for contact in self.contacts.values():
                for field in ['emailaddress1', 'emailaddress2', 'emailaddress3']:
                    email = contact.get(field)
                    if email and '@' in email:
                        contact_emails.add(email.lower().strip())
            
            print(f"   🎯 Tracking {len(contact_emails)} contact email addresses")
            
            # Start with root folder
            root_folder = self.pst_store.GetRootFolder()
            self._process_folder_for_contacts(root_folder, "", contact_emails)
            
            print(f"\n📊 PST email extraction completed:")
            emails_found = sum(len(emails) for emails in self.pst_emails.values())
            print(f"   📧 Total emails found for contacts: {emails_found}")
            print(f"   👥 Contacts with PST emails: {len(self.pst_emails)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting PST emails: {str(e)}")
            return False

    def _process_folder_for_contacts(self, folder, folder_path, contact_emails):
        """Process folder and extract emails for known contacts."""
        try:
            current_path = f"{folder_path}/{folder.Name}" if folder_path else folder.Name
            
            # Skip Teams and Skype folders for timeline analysis
            if any(skip in current_path for skip in ['TeamsMessagesData', 'SkypeSpacesData']):
                return
            
            # Process messages in current folder
            messages = folder.Items
            message_count = messages.Count
            
            if message_count > 0:
                print(f"   📂 Processing folder: {current_path} ({message_count} messages)")
                
                for i in range(1, min(message_count + 1, 1001)):  # Limit to avoid timeout
                    try:
                        message = messages[i]
                        self._extract_email_if_contact_involved(message, current_path, contact_emails)
                        
                    except Exception as e:
                        # Skip problematic messages
                        continue
            
            # Process subfolders
            for subfolder in folder.Folders:
                self._process_folder_for_contacts(subfolder, current_path, contact_emails)
                
        except Exception as e:
            print(f"⚠️  Error processing folder {folder_path}: {str(e)}")

    def _extract_email_if_contact_involved(self, message, folder_path, contact_emails):
        """Extract email if it involves any of our contacts."""
        try:
            # Check sender
            sender_email = None
            if hasattr(message, 'SenderEmailAddress') and message.SenderEmailAddress:
                sender_email = message.SenderEmailAddress.lower().strip()
            
            # Check recipients
            recipient_emails = []
            if hasattr(message, 'Recipients'):
                for recipient in message.Recipients:
                    if hasattr(recipient, 'Address') and recipient.Address:
                        rec_email = recipient.Address.lower().strip()
                        if self._is_valid_email(rec_email):
                            recipient_emails.append(rec_email)
            
            # Find contact emails involved
            involved_emails = []
            if sender_email and self._is_valid_email(sender_email) and sender_email in contact_emails:
                involved_emails.append(sender_email)
            
            for rec_email in recipient_emails:
                if rec_email in contact_emails:
                    involved_emails.append(rec_email)
            
            # Extract email data if contacts are involved
            if involved_emails:
                email_data = self._extract_email_data(message, folder_path)
                if email_data:
                    for email in set(involved_emails):  # Remove duplicates
                        if email not in self.pst_emails:
                            self.pst_emails[email] = []
                        self.pst_emails[email].append(email_data)
                        
        except Exception as e:
            # Skip problematic emails
            pass

    def _extract_email_data(self, message, folder_path):
        """Extract detailed email data from message."""
        try:
            # Get basic properties
            subject = getattr(message, 'Subject', '')
            
            # Get dates
            sent_date = None
            received_date = None
            if hasattr(message, 'SentOn'):
                sent_date = message.SentOn
            if hasattr(message, 'ReceivedTime'):
                received_date = message.ReceivedTime
            
            # Get sender info
            sender_email = getattr(message, 'SenderEmailAddress', '')
            sender_name = getattr(message, 'SenderName', '')
            
            # Get recipients
            recipients = []
            if hasattr(message, 'Recipients'):
                for recipient in message.Recipients:
                    recipients.append({
                        'email': getattr(recipient, 'Address', ''),
                        'name': getattr(recipient, 'Name', ''),
                        'type': getattr(recipient, 'Type', 1)  # 1=To, 2=CC, 3=BCC
                    })
            
            # Get body (limited for comparison)
            body_preview = ''
            if hasattr(message, 'Body'):
                body = str(message.Body)[:200]  # First 200 chars for comparison
                body_preview = re.sub(r'\s+', ' ', body).strip()
            
            # Get size
            size = getattr(message, 'Size', 0)
            
            return {
                'subject': subject,
                'sent_date': sent_date,
                'received_date': received_date,
                'sender_email': sender_email.lower().strip() if sender_email else '',
                'sender_name': sender_name,
                'recipients': recipients,
                'body_preview': body_preview,
                'folder_path': folder_path,
                'size': size,
                'pst_message_id': f"{folder_path}:{subject}:{sent_date}"  # Unique ID for matching
            }
            
        except Exception as e:
            return None

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

    def perform_timeline_analysis(self):
        """Perform comprehensive timeline completeness analysis."""
        try:
            print(f"\n🔍 Performing timeline completeness analysis...")
            
            analyzed_contacts = 0
            
            for contact_id, contact in self.contacts.items():
                # Get contact emails
                contact_emails = []
                for field in ['emailaddress1', 'emailaddress2', 'emailaddress3']:
                    email = contact.get(field)
                    if email and '@' in email:
                        contact_emails.append(email.lower().strip())
                
                if not contact_emails:
                    continue
                
                # Get CRM activities for this contact
                crm_activities = self.crm_activities.get(contact_id, [])
                
                # Get PST emails for this contact
                pst_emails = []
                for email in contact_emails:
                    pst_emails.extend(self.pst_emails.get(email, []))
                
                # Perform analysis for this contact
                analysis = self._analyze_contact_timeline(contact, crm_activities, pst_emails)
                self.timeline_analysis[contact_id] = analysis
                analyzed_contacts += 1
            
            print(f"✅ Timeline analysis completed for {analyzed_contacts} contacts")
            return True
            
        except Exception as e:
            print(f"❌ Error performing timeline analysis: {str(e)}")
            return False

    def _analyze_contact_timeline(self, contact, crm_activities, pst_emails):
        """Analyze timeline completeness for a single contact."""
        try:
            contact_name = contact.get('fullname', 'Unknown')
            
            # Basic counts
            crm_count = len(crm_activities)
            pst_count = len(pst_emails)
            
            # Try to match emails between CRM and PST
            matched_emails = 0
            missing_from_crm = []
            
            # Create lookup for CRM activities
            crm_lookup = {}
            for activity in crm_activities:
                # Create matching key based on subject and approximate date
                subject = activity.get('subject', '').lower().strip()
                sent_date = activity.get('senton') or activity.get('createdon')
                if sent_date:
                    try:
                        # Parse ISO date
                        if isinstance(sent_date, str):
                            date_obj = datetime.fromisoformat(sent_date.replace('Z', '+00:00'))
                        else:
                            date_obj = sent_date
                        date_key = date_obj.strftime('%Y-%m-%d')
                    except:
                        date_key = 'unknown'
                else:
                    date_key = 'unknown'
                
                key = f"{subject}:{date_key}"
                crm_lookup[key] = activity
            
            # Check PST emails against CRM
            for pst_email in pst_emails:
                subject = pst_email.get('subject', '').lower().strip()
                sent_date = pst_email.get('sent_date')
                
                if sent_date:
                    try:
                        date_key = sent_date.strftime('%Y-%m-%d')
                    except:
                        date_key = 'unknown'
                else:
                    date_key = 'unknown'
                
                key = f"{subject}:{date_key}"
                
                if key in crm_lookup:
                    matched_emails += 1
                else:
                    # This PST email is missing from CRM
                    missing_from_crm.append(pst_email)
            
            # Calculate completeness percentage
            if pst_count > 0:
                completeness = (matched_emails / pst_count) * 100
            else:
                completeness = 100 if crm_count == 0 else 0
            
            # Determine priority for improvement
            if pst_count >= 10 and completeness < 50:
                priority = 'High'
            elif pst_count >= 5 and completeness < 70:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            return {
                'contact_name': contact_name,
                'contact_emails': [contact.get('emailaddress1', '')],
                'crm_activity_count': crm_count,
                'pst_email_count': pst_count,
                'matched_emails': matched_emails,
                'missing_from_crm': len(missing_from_crm),
                'completeness_percentage': round(completeness, 1),
                'priority': priority,
                'missing_emails': missing_from_crm[:10],  # Top 10 missing emails
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'contact_name': contact.get('fullname', 'Unknown'),
                'error': str(e),
                'analysis_date': datetime.now().isoformat()
            }

    def show_timeline_analysis_results(self):
        """Display comprehensive timeline analysis results."""
        try:
            print("\n📊 TIMELINE COMPLETENESS ANALYSIS RESULTS")
            print("="*70)
            
            if not self.timeline_analysis:
                print("❌ No timeline analysis data available")
                return
            
            # Overall statistics
            total_contacts = len(self.timeline_analysis)
            high_priority = len([a for a in self.timeline_analysis.values() if a.get('priority') == 'High'])
            medium_priority = len([a for a in self.timeline_analysis.values() if a.get('priority') == 'Medium'])
            
            # Calculate averages
            total_crm = sum(a.get('crm_activity_count', 0) for a in self.timeline_analysis.values())
            total_pst = sum(a.get('pst_email_count', 0) for a in self.timeline_analysis.values())
            total_missing = sum(a.get('missing_from_crm', 0) for a in self.timeline_analysis.values())
            
            avg_completeness = sum(a.get('completeness_percentage', 0) for a in self.timeline_analysis.values()) / total_contacts
            
            # Summary statistics
            summary = [
                ['Total Contacts Analyzed', total_contacts],
                ['Total CRM Activities', total_crm],
                ['Total PST Emails', total_pst],
                ['Total Missing from CRM', total_missing],
                ['Average Completeness', f"{avg_completeness:.1f}%"],
                ['High Priority Contacts', high_priority],
                ['Medium Priority Contacts', medium_priority]
            ]
            
            print(tabulate(summary, headers=['Metric', 'Value'], tablefmt='grid'))
            
            # Top contacts needing attention (low completeness, high email count)
            priority_contacts = []
            for contact_id, analysis in self.timeline_analysis.items():
                if analysis.get('pst_email_count', 0) >= 5:  # Only contacts with meaningful email volume
                    priority_contacts.append((
                        analysis.get('contact_name', 'Unknown'),
                        analysis.get('pst_email_count', 0),
                        analysis.get('crm_activity_count', 0),
                        analysis.get('missing_from_crm', 0),
                        analysis.get('completeness_percentage', 0),
                        analysis.get('priority', 'Low')
                    ))
            
            # Sort by missing count descending
            priority_contacts.sort(key=lambda x: x[3], reverse=True)
            
            if priority_contacts:
                print(f"\n🎯 Top 15 Contacts Needing Timeline Improvement:")
                priority_table = []
                for contact, pst_count, crm_count, missing, completeness, priority in priority_contacts[:15]:
                    priority_table.append([
                        contact[:30] + ('...' if len(contact) > 30 else ''),
                        pst_count,
                        crm_count,
                        missing,
                        f"{completeness}%",
                        priority
                    ])
                
                headers = ['Contact', 'PST Emails', 'CRM Activities', 'Missing', 'Complete%', 'Priority']
                print(tabulate(priority_table, headers=headers, tablefmt='grid'))
            
            # Completeness distribution
            print(f"\n📈 Completeness Distribution:")
            ranges = [(0, 25), (25, 50), (50, 75), (75, 90), (90, 100)]
            distribution = []
            
            for min_val, max_val in ranges:
                count = len([a for a in self.timeline_analysis.values() 
                           if min_val <= a.get('completeness_percentage', 0) < max_val])
                distribution.append([f"{min_val}-{max_val}%", count])
            
            # Add 100% separately
            complete_count = len([a for a in self.timeline_analysis.values() 
                                if a.get('completeness_percentage', 0) == 100])
            distribution.append(["100%", complete_count])
            
            print(tabulate(distribution, headers=['Completeness Range', 'Contacts'], tablefmt='grid'))
            
        except Exception as e:
            print(f"❌ Error showing timeline analysis results: {str(e)}")

    def export_timeline_analysis(self, filename=None):
        """Export complete timeline analysis to files."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"timeline_analysis_{timestamp}"
            
            print(f"\n📤 Exporting timeline analysis...")
            
            # Prepare detailed data for export
            export_data = []
            for contact_id, analysis in self.timeline_analysis.items():
                contact = self.contacts.get(contact_id, {})
                
                row = {
                    'Contact ID': contact_id,
                    'Contact Name': analysis.get('contact_name', ''),
                    'Primary Email': contact.get('emailaddress1', ''),
                    'PST Email Count': analysis.get('pst_email_count', 0),
                    'CRM Activity Count': analysis.get('crm_activity_count', 0),
                    'Matched Emails': analysis.get('matched_emails', 0),
                    'Missing from CRM': analysis.get('missing_from_crm', 0),
                    'Completeness %': analysis.get('completeness_percentage', 0),
                    'Priority': analysis.get('priority', 'Low'),
                    'Job Title': contact.get('jobtitle', ''),
                    'Phone': contact.get('telephone1', ''),
                    'Analysis Date': analysis.get('analysis_date', '')
                }
                export_data.append(row)
            
            # Sort by priority and missing count
            priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
            export_data.sort(key=lambda x: (priority_order.get(x['Priority'], 0), x['Missing from CRM']), reverse=True)
            
            # Export to CSV
            csv_filename = f"{filename}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                if export_data:
                    fieldnames = export_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(export_data)
            
            # Export detailed analysis to JSON
            json_filename = f"{filename}.json"
            detailed_export = {
                'analysis_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_contacts': len(self.timeline_analysis),
                    'total_missing_emails': sum(a.get('missing_from_crm', 0) for a in self.timeline_analysis.values()),
                    'average_completeness': sum(a.get('completeness_percentage', 0) for a in self.timeline_analysis.values()) / len(self.timeline_analysis) if self.timeline_analysis else 0
                },
                'contact_analysis': {}
            }
            
            # Add detailed analysis for each contact
            for contact_id, analysis in self.timeline_analysis.items():
                contact = self.contacts.get(contact_id, {})
                detailed_export['contact_analysis'][contact_id] = {
                    'contact_info': {
                        'name': analysis.get('contact_name', ''),
                        'email': contact.get('emailaddress1', ''),
                        'job_title': contact.get('jobtitle', '')
                    },
                    'timeline_metrics': {
                        'pst_email_count': analysis.get('pst_email_count', 0),
                        'crm_activity_count': analysis.get('crm_activity_count', 0),
                        'matched_emails': analysis.get('matched_emails', 0),
                        'missing_from_crm': analysis.get('missing_from_crm', 0),
                        'completeness_percentage': analysis.get('completeness_percentage', 0),
                        'priority': analysis.get('priority', 'Low')
                    },
                    'sample_missing_emails': [
                        {
                            'subject': email.get('subject', ''),
                            'sent_date': email.get('sent_date').isoformat() if email.get('sent_date') else None,
                            'sender': email.get('sender_email', ''),
                            'folder': email.get('folder_path', '')
                        }
                        for email in analysis.get('missing_emails', [])[:5]  # Top 5 missing emails
                    ]
                }
            
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(detailed_export, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Timeline analysis exported:")
            print(f"   📄 Summary CSV: {csv_filename}")
            print(f"   📄 Detailed JSON: {json_filename}")
            
            return csv_filename, json_filename
            
        except Exception as e:
            print(f"❌ Error exporting timeline analysis: {str(e)}")
            return None, None

    def close_pst_file(self):
        """Close PST file and clean up."""
        try:
            if self.pst_store:
                self.pst_store = None
            self.outlook = None
            print("✅ PST file closed")
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")

    def run_complete_timeline_analysis(self):
        """Run the complete timeline completeness analysis."""
        try:
            print("\n🚀 Starting Complete Timeline Completeness Analysis")
            print("="*70)
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Load contacts from CRM
            if not self.load_contacts_from_crm():
                return False
            
            # Step 3: Load email activities for all contacts
            if not self.load_all_contact_activities():
                return False
            
            # Step 4: Open PST file
            if not self.open_pst_file():
                return False
            
            # Step 5: Extract PST emails for contacts
            if not self.extract_pst_emails_by_contact():
                return False
            
            # Step 6: Perform timeline analysis
            if not self.perform_timeline_analysis():
                return False
            
            # Step 7: Show results
            self.show_timeline_analysis_results()
            
            # Step 8: Export results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file, json_file = self.export_timeline_analysis(f"timeline_analysis_{timestamp}")
            
            # Step 9: Cleanup
            self.close_pst_file()
            
            print("\n🎉 Timeline completeness analysis completed!")
            print("="*60)
            print("📁 Generated files:")
            if csv_file:
                print(f"   📄 Summary Report: {csv_file}")
            if json_file:
                print(f"   📄 Detailed Analysis: {json_file}")
            
            print("\n💡 Recommendations:")
            high_priority = len([a for a in self.timeline_analysis.values() if a.get('priority') == 'High'])
            if high_priority > 0:
                print(f"   🔥 {high_priority} contacts need immediate timeline attention")
                print("   📧 Use dynamics_email_attacher.py to import missing emails")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in complete timeline analysis: {str(e)}")
            self.close_pst_file()
            return False

def main():
    """Main function to run the timeline completeness analyzer."""
    print("📊 TIMELINE COMPLETENESS ANALYZER")
    print("="*60)
    print("🎯 Purpose: Analyze email timeline completeness in Dynamics 365 CRM")
    print("📧 Compare: CRM email activities vs PST file emails")
    print("📊 Output: Completeness reports and missing email recommendations")
    print()
    
    # Configuration
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    # Create analyzer instance
    analyzer = TimelineCompletenessAnalyzer(username, password, pst_path)
    
    # Run complete analysis
    success = analyzer.run_complete_timeline_analysis()
    
    if success:
        print("\n✅ Timeline completeness analysis completed successfully!")
        print("💡 Use the generated reports to prioritize timeline improvements")
    else:
        print("\n❌ Timeline completeness analysis failed!")
        print("💡 Check your credentials, network connection, and PST file access")

if __name__ == "__main__":
    main() 