#!/usr/bin/env python3
"""
Dynamics 365 Email Attacher
A Python script to attach PST email communications to existing contacts in Dynamics 365 CRM.
Creates email activities linked to contacts for complete communication timeline visibility.

Requirements:
- pip install requests msal pandas tabulate pywin32
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
import msal
import time
import win32com.client
import re
from tabulate import tabulate


class Dynamics365EmailAttacher:
    def __init__(self, username, password, tenant_domain=None):
        """Initialize the Dynamics 365 email attacher."""
        self.username = username
        self.password = password
        self.tenant_domain = tenant_domain or "dynamique.com"
        
        # Dynamics 365 configuration
        self.client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_domain}"
        self.scope = ["https://dynglobal.crm.dynamics.com/.default"]
        
        # Will be set after authentication
        self.access_token = None
        self.crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
        
        # PST and email data
        self.outlook = None
        self.pst_store = None
        self.target_contact = None
        self.target_emails = []
        
        print("📧 Dynamics 365 Email Attacher")
        print("="*35)
        print(f"👤 User: {self.username}")
        print(f"🏢 Tenant: {self.tenant_domain}")
        print(f"🌐 CRM URL: https://dynglobal.crm.dynamics.com")
    
    def authenticate(self):
        """Authenticate with Dynamics 365 using MSAL."""
        try:
            print("\n🔐 Starting authentication...")
            
            app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=self.authority
            )
            
            # Try silent authentication first
            accounts = app.get_accounts()
            if accounts:
                result = app.acquire_token_silent(self.scope, account=accounts[0])
                if result:
                    self.access_token = result['access_token']
                    print("✅ Silent authentication successful!")
                    return True
            
            # Username/password authentication
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
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_contact_from_crm(self, email_address):
        """Get the contact record from Dynamics 365 CRM."""
        try:
            print(f"\n🔍 Looking up contact in CRM: {email_address}")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Query for the contact by email
            query_url = f"{self.crm_base_url}/contacts"
            params = {
                '$select': 'contactid,fullname,firstname,lastname,emailaddress1',
                '$filter': f"emailaddress1 eq '{email_address}'"
            }
            
            response = requests.get(query_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('value', [])
                
                if contacts:
                    contact = contacts[0]
                    self.target_contact = contact
                    print(f"✅ Found contact in CRM:")
                    print(f"   🆔 Contact ID: {contact['contactid']}")
                    print(f"   👤 Name: {contact['fullname']}")
                    print(f"   📧 Email: {contact['emailaddress1']}")
                    return contact
                else:
                    print(f"❌ Contact not found in CRM: {email_address}")
                    return None
            else:
                print(f"❌ Error querying CRM: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting contact from CRM: {str(e)}")
            return None
    
    def open_pst_file(self, pst_path):
        """Open the PST file using Outlook COM interface."""
        try:
            print(f"\n📁 Opening PST file: {pst_path}")
            
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = self.outlook.GetNamespace("MAPI")
            
            # Add the PST file
            namespace.AddStore(pst_path)
            
            # Find the PST store
            for store in namespace.Stores:
                if pst_path.lower() in store.FilePath.lower():
                    self.pst_store = store
                    print(f"✅ PST file opened: {store.DisplayName}")
                    return True
            
            print(f"❌ Could not find PST store")
            return False
            
        except Exception as e:
            print(f"❌ Error opening PST file: {str(e)}")
            return False
    
    def find_emails_for_contact(self, target_emails):
        """Find all emails in the PST that involve the target contact."""
        try:
            # Support both single email string and list of emails
            if isinstance(target_emails, str):
                target_emails = [target_emails]
            
            print(f"\n🔍 Searching for emails involving: {', '.join(target_emails)}")
            
            if not self.pst_store:
                print("❌ PST store not available")
                return []
            
            emails_found = []
            folders_processed = 0
            unique_senders = set()
            unique_recipients = set()
            
            def process_folder(folder, folder_path=""):
                nonlocal folders_processed, emails_found, unique_senders, unique_recipients
                
                current_path = f"{folder_path}/{folder.Name}" if folder_path else folder.Name
                
                # Skip Teams and system folders
                if any(skip in current_path.lower() for skip in ['teamsmessagesdata', 'skypespacesdata', 'applicationdataroot']):
                    return
                
                try:
                    messages = folder.Items
                    folder_emails = 0
                    
                    print(f"   📂 Processing folder: {current_path} ({messages.Count} messages)")
                    
                    for message in messages:
                        try:
                            # Get email addresses
                            sender_email = getattr(message, 'SenderEmailAddress', '').lower()
                            recipients = getattr(message, 'Recipients', None)
                            
                            # Track unique addresses for debugging
                            if sender_email:
                                unique_senders.add(sender_email)
                            
                            # Check if email involves any target contact email
                            email_involves_contact = False
                            
                            # Check sender against all target emails
                            for target_email in target_emails:
                                if sender_email == target_email.lower():
                                    email_involves_contact = True
                                    break
                            
                            # Check recipients
                            if recipients and not email_involves_contact:
                                for recipient in recipients:
                                    recipient_email = getattr(recipient, 'Address', '').lower()
                                    unique_recipients.add(recipient_email)
                                    
                                    for target_email in target_emails:
                                        if recipient_email == target_email.lower():
                                            email_involves_contact = True
                                            break
                                    
                                    if email_involves_contact:
                                        break
                            
                            if email_involves_contact:
                                # Extract email data
                                email_data = {
                                    'subject': getattr(message, 'Subject', ''),
                                    'sender_name': getattr(message, 'SenderName', ''),
                                    'sender_email': sender_email,
                                    'received_time': getattr(message, 'ReceivedTime', None),
                                    'sent_on': getattr(message, 'SentOn', None),
                                    'size': getattr(message, 'Size', 0),
                                    'body': getattr(message, 'Body', '')[:5000],  # Limit body size
                                    'folder_path': current_path,
                                    'importance': getattr(message, 'Importance', 1),
                                    'recipients_list': []
                                }
                                
                                # Get recipient details
                                if recipients:
                                    for recipient in recipients:
                                        email_data['recipients_list'].append({
                                            'name': getattr(recipient, 'Name', ''),
                                            'email': getattr(recipient, 'Address', ''),
                                            'type': getattr(recipient, 'Type', 1)  # 1=To, 2=CC, 3=BCC
                                        })
                                
                                emails_found.append(email_data)
                                folder_emails += 1
                                
                        except Exception as e:
                            # Skip problematic messages
                            continue
                    
                    if folder_emails > 0:
                        print(f"      ✅ Found {folder_emails} emails involving contact")
                    
                    folders_processed += 1
                    
                    # Process subfolders
                    for subfolder in folder.Folders:
                        process_folder(subfolder, current_path)
                        
                except Exception as e:
                    print(f"      ❌ Error processing folder {current_path}: {str(e)}")
            
            # Start processing from root
            root_folder = self.pst_store.GetRootFolder()
            process_folder(root_folder)
            
            print(f"\n📊 Email search completed:")
            print(f"   📂 Folders processed: {folders_processed}")
            print(f"   📧 Emails found: {len(emails_found)}")
            
            # Debug: Show sample email addresses found (for troubleshooting)
            if not emails_found:
                print(f"\n🔍 DEBUG - Sample email addresses found in PST:")
                sample_senders = list(unique_senders)[:20]
                sample_recipients = list(unique_recipients)[:20]
                
                print(f"   📤 Sample senders:")
                for sender in sample_senders:
                    if 'lerceg' in sender.lower() or 'erceg' in sender.lower():
                        print(f"      🎯 {sender}")
                    elif len(sample_senders) <= 10:
                        print(f"         {sender}")
                
                print(f"   📥 Sample recipients:")
                for recipient in sample_recipients:
                    if 'lerceg' in recipient.lower() or 'erceg' in recipient.lower():
                        print(f"      🎯 {recipient}")
                    elif len(sample_recipients) <= 10:
                        print(f"         {recipient}")
            
            self.target_emails = emails_found
            return emails_found
            
        except Exception as e:
            print(f"❌ Error finding emails: {str(e)}")
            return []
    
    def format_email_body(self, raw_body):
        """Format email body with clean structure, separating quoted content."""
        import re
        
        if not raw_body:
            return ""
        
        # Clean up the body text and normalize line endings
        body = raw_body.strip().replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove any "Modified By:" references that might appear
        body = re.sub(r'Modified By:.*?(\n|$)', '', body, flags=re.IGNORECASE)
        
        # Split into lines for processing
        lines = body.split('\n')
        formatted_lines = []
        in_quoted_section = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines at the start
            if not formatted_lines and not stripped:
                continue
            
            # Check for patterns that indicate start of quoted/forwarded content
            if (re.match(r'^From:\s*.+', stripped, re.IGNORECASE) or
                re.match(r'^Sent:\s*.+', stripped, re.IGNORECASE) or
                re.match(r'^To:\s*.+', stripped, re.IGNORECASE) or
                re.match(r'^Subject:\s*.+', stripped, re.IGNORECASE) or
                re.match(r'^On\s+.+wrote:', stripped, re.IGNORECASE) or
                stripped.startswith('-----Original Message-----') or
                stripped.startswith('________________________________') or
                re.match(r'^_{20,}', stripped)):  # Line of many underscores
                
                # Add separator for quoted content
                if not in_quoted_section:
                    if formatted_lines:  # Only add separator if there's content above
                        formatted_lines.append("")
                        formatted_lines.append("_" * 50)
                    in_quoted_section = True
                
                formatted_lines.append(stripped)
                
            elif stripped.startswith('>'):
                # Handle quoted lines with >
                formatted_lines.append(stripped)
                
            else:
                # Regular content - preserve original formatting
                formatted_lines.append(line.rstrip())
        
        # Remove trailing empty lines
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()
        
        # Join with Windows line endings for better Dynamics 365 compatibility
        return '\r\n'.join(formatted_lines)

    def create_email_activity_in_crm(self, email_data, contact_id):
        """Create an email activity in Dynamics 365 CRM."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            # Determine the email date (prefer sent_on, fallback to received_time)
            email_date = email_data.get('sent_on') or email_data.get('received_time')
            if email_date:
                # Convert to ISO format for Dynamics 365
                if hasattr(email_date, 'strftime'):
                    email_date_iso = email_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    email_date_iso = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                email_date_iso = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Prepare recipients string
            recipients_str = ""
            for recipient in email_data.get('recipients_list', []):
                type_label = {1: "To", 2: "CC", 3: "BCC"}.get(recipient.get('type', 1), "To")
                recipients_str += f"{type_label}: {recipient.get('name', '')} <{recipient.get('email', '')}>\n"
            
            # Format email date for better display
            if email_date and hasattr(email_date, 'strftime'):
                email_date_display = email_date.strftime('%A, %B %d, %Y %I:%M:%S %p')
            elif email_data.get('received_time') and hasattr(email_data.get('received_time'), 'strftime'):
                email_date_display = email_data.get('received_time').strftime('%A, %B %d, %Y %I:%M:%S %p')
            else:
                # Try to parse any date string that might be available
                try:
                    # Check if there's a date in the email data
                    for key in ['sent_on', 'received_time', 'creation_time', 'last_modification_time']:
                        date_value = email_data.get(key)
                        if date_value and hasattr(date_value, 'strftime'):
                            email_date_display = date_value.strftime('%A, %B %d, %Y %I:%M:%S %p')
                            break
                    else:
                        email_date_display = 'Date not available'
                except:
                    email_date_display = 'Date not available'
            
            # Create clean Dynamics 365 style email headers with proper line breaks
            headers_parts = []
            
            # From header with bold formatting
            sender_name = email_data.get('sender_name', '').strip()
            sender_email = email_data.get('sender_email', '').strip()
            if sender_name and sender_email:
                headers_parts.append(f"<b>From:</b> {sender_name} <{sender_email}>")
            elif sender_email:
                headers_parts.append(f"<b>From:</b> {sender_email}")
            else:
                headers_parts.append("<b>From:</b> Unknown Sender")
            
            # Sent header with bold formatting
            headers_parts.append(f"<b>Sent:</b> {email_date_display}")
            
            # Format recipients properly
            to_recipients = []
            cc_recipients = []
            bcc_recipients = []
            
            for recipient in email_data.get('recipients_list', []):
                name = recipient.get('name', '').strip()
                email = recipient.get('email', '').strip()
                if name and email:
                    recipient_str = f"{name} <{email}>"
                elif email:
                    recipient_str = email
                else:
                    continue
                    
                if recipient.get('type') == 2:  # CC
                    cc_recipients.append(recipient_str)
                elif recipient.get('type') == 3:  # BCC
                    bcc_recipients.append(recipient_str)
                else:  # TO
                    to_recipients.append(recipient_str)
            
            # Add recipient headers with bold formatting
            if to_recipients:
                headers_parts.append(f"<b>To:</b> {'; '.join(to_recipients)}")
            if cc_recipients:
                headers_parts.append(f"<b>Cc:</b> {'; '.join(cc_recipients)}")
            if bcc_recipients:
                headers_parts.append(f"<b>Bcc:</b> {'; '.join(bcc_recipients)}")
            
            # Subject header with bold formatting
            subject = email_data.get('subject', '').strip()
            headers_parts.append(f"<b>Subject:</b> {subject if subject else 'No Subject'}")
            
            # Join headers with HTML line breaks for Dynamics 365
            email_headers = '<br>'.join(headers_parts)
            
            # Format the email body content
            raw_body = email_data.get('body', '').strip()
            if raw_body:
                # Clean up the body and format quoted content
                formatted_body = self.format_email_body(raw_body)
                # Convert line breaks to HTML for proper display
                formatted_body = formatted_body.replace('\r\n', '<br>').replace('\n', '<br>')
                # Limit body length
                if len(formatted_body) > 2500:
                    formatted_body = formatted_body[:2500] + "<br><br>[Content truncated for display...]"
            else:
                formatted_body = ""
            
            # Create the complete email with HTML structure
            if formatted_body:
                complete_email_content = f"{email_headers}<br><br>{formatted_body}"
            else:
                complete_email_content = email_headers
            
            # Create email activity data
            activity_data = {
                "subject": email_data.get('subject', 'No Subject')[:200],  # Dynamics field limit
                "description": complete_email_content[:4900],  # Limit description size
                
                "actualdurationminutes": 0,
                "actualend": email_date_iso,
                "actualstart": email_date_iso,
                "scheduledend": email_date_iso,
                "scheduledstart": email_date_iso,
                
                # Set the email send date for proper timeline display
                "senton": email_date_iso,  # Email send/receive date for timeline
                
                # Link to the contact
                "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
                
                # Email specific fields
                "directioncode": True,  # True = Outgoing, False = Incoming
                "deliveryprioritycode": email_data.get('importance', 1),
                
                # Set as open draft initially
                "statecode": 0,  # Open
                "statuscode": 1  # Draft
            }
            
            # Determine if email was sent by the contact or to the contact
            target_email = self.target_contact['emailaddress1'].lower()
            sender_email = email_data.get('sender_email', '').lower()
            
            if sender_email == target_email:
                activity_data["directioncode"] = True  # Outgoing from contact
                activity_data["statuscode"] = 1  # Draft
            else:
                activity_data["directioncode"] = False  # Incoming to contact
                activity_data["statuscode"] = 1  # Draft
            
            # Create the email activity
            create_url = f"{self.crm_base_url}/emails"
            response = requests.post(create_url, headers=headers, json=activity_data, timeout=30)
            
            if response.status_code == 204:
                # Get the activity ID from location header
                location = response.headers.get('OData-EntityId', '')
                activity_id = location.split('(')[-1].split(')')[0] if '(' in location else 'Unknown'
                return activity_id
            else:
                print(f"      ❌ Failed to create email activity: {response.status_code}")
                if response.content:
                    error_data = response.json()
                    print(f"         Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"      ❌ Error creating email activity: {str(e)}")
            return None
    
    def attach_emails_to_contact(self):
        """Attach all found emails to the contact in CRM."""
        try:
            if not self.target_emails:
                print("❌ No emails to attach")
                return False
            
            if not self.target_contact:
                print("❌ No target contact available")
                return False
            
            print(f"\n📎 Attaching {len(self.target_emails)} emails to contact...")
            contact_id = self.target_contact['contactid']
            
            successful_attachments = 0
            failed_attachments = 0
            
            for idx, email_data in enumerate(self.target_emails, 1):
                print(f"   📧 Processing email {idx}/{len(self.target_emails)}: {email_data.get('subject', 'No Subject')[:50]}...")
                
                activity_id = self.create_email_activity_in_crm(email_data, contact_id)
                
                if activity_id:
                    successful_attachments += 1
                    print(f"      ✅ Created activity ID: {activity_id}")
                else:
                    failed_attachments += 1
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
            
            print(f"\n📊 Email attachment summary:")
            print(f"   ✅ Successfully attached: {successful_attachments}")
            print(f"   ❌ Failed to attach: {failed_attachments}")
            print(f"   📈 Success rate: {(successful_attachments/len(self.target_emails))*100:.1f}%")
            
            return successful_attachments > 0
            
        except Exception as e:
            print(f"❌ Error attaching emails: {str(e)}")
            return False
    
    def show_email_summary(self):
        """Show a summary of the emails found."""
        try:
            if not self.target_emails:
                return
            
            print(f"\n📊 EMAIL SUMMARY FOR {self.target_contact['emailaddress1']}")
            print("="*60)
            
            # Basic statistics
            total_emails = len(self.target_emails)
            sent_emails = sum(1 for email in self.target_emails 
                            if email.get('sender_email', '').lower() == self.target_contact['emailaddress1'].lower())
            received_emails = total_emails - sent_emails
            
            stats = [
                ['Total Emails', total_emails],
                ['Sent by Contact', sent_emails],
                ['Received by Contact', received_emails],
                ['Average Size', f"{sum(e.get('size', 0) for e in self.target_emails) / total_emails:.0f} bytes"]
            ]
            print(tabulate(stats, headers=['Metric', 'Value'], tablefmt='grid'))
            
            # Top folders
            if self.target_emails:
                folder_counts = {}
                for email in self.target_emails:
                    folder = email.get('folder_path', 'Unknown')
                    folder_counts[folder] = folder_counts.get(folder, 0) + 1
                
                print(f"\n📁 Top 10 Folders with Emails:")
                folder_table = []
                for folder, count in sorted(folder_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    folder_table.append([folder[:50] + ('...' if len(folder) > 50 else ''), count])
                print(tabulate(folder_table, headers=['Folder', 'Count'], tablefmt='grid'))
            
            # Recent emails
            print(f"\n📧 Most Recent 5 Emails:")
            recent_emails = sorted(self.target_emails, 
                                 key=lambda x: x.get('sent_on') or x.get('received_time') or datetime.min, 
                                 reverse=True)[:5]
            
            email_table = []
            for email in recent_emails:
                date = email.get('sent_on') or email.get('received_time')
                date_str = date.strftime('%Y-%m-%d %H:%M') if date else 'Unknown'
                direction = "→" if email.get('sender_email', '').lower() == self.target_contact['emailaddress1'].lower() else "←"
                email_table.append([
                    date_str,
                    direction,
                    email.get('subject', 'No Subject')[:40] + ('...' if len(email.get('subject', '')) > 40 else '')
                ])
            
            print(tabulate(email_table, headers=['Date', 'Dir', 'Subject'], tablefmt='grid'))
            
        except Exception as e:
            print(f"⚠️  Error generating email summary: {str(e)}")
    
    def close_pst_file(self):
        """Close the PST file and clean up Outlook connection."""
        try:
            if self.pst_store:
                # Remove the PST store
                namespace = self.outlook.GetNamespace("MAPI")
                namespace.RemoveStore(self.pst_store.GetRootFolder())
                print("✅ PST file closed")
            
            self.outlook = None
            self.pst_store = None
            
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")
    
    def run_email_attachment(self, target_email, pst_path):
        """Run the complete email attachment process."""
        try:
            print("🚀 Starting Email Attachment Process")
            print("="*40)
            print(f"🎯 Target Contact: {target_email}")
            print(f"📁 PST File: {pst_path}")
            
            # Step 1: Authenticate
            if not self.authenticate():
                return False
            
            # Step 2: Get contact from CRM
            contact = self.get_contact_from_crm(target_email)
            if not contact:
                return False
            
            # Step 3: Open PST file
            if not self.open_pst_file(pst_path):
                return False
            
            # Step 4: Find emails for contact
            # Special case: lerceg@dynamique.com contact uses lukalerceg@dynamique.com in PST
            pst_email_address = target_email
            if target_email == "lerceg@dynamique.com":
                pst_email_address = "lukalerceg@dynamique.com"
                print(f"🔍 Note: Searching PST for {pst_email_address} to attach to {target_email} contact")
            
            emails = self.find_emails_for_contact(pst_email_address)
            
            if not emails:
                print("⚠️  No emails found for this contact")
                self.close_pst_file()
                return False
            
            # Step 5: Show email summary
            self.show_email_summary()
            
            # Step 6: Attach emails to contact
            success = self.attach_emails_to_contact()
            
            # Step 7: Clean up
            self.close_pst_file()
            
            if success:
                print(f"\n🎉 Email attachment process completed successfully!")
                print(f"👤 Contact: {self.target_contact['fullname']}")
                print(f"📧 Emails processed: {len(self.target_emails)}")
                print(f"💡 Check the contact timeline in Dynamics 365 CRM")
                return True
            else:
                print(f"\n❌ Email attachment process failed")
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            self.close_pst_file()
            return False


def main():
    """Main function to run the email attachment process."""
    # Configuration
    username = "gvranjesevic@dynamique.com"
    password = "#SanDiegoChicago77"
    target_email = "lerceg@dynamique.com"
    pst_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    print("📧 DYNAMICS 365 EMAIL ATTACHMENT")
    print("="*35)
    print("🎯 Purpose: Attach PST emails to CRM contact for communication timeline")
    print(f"👤 Target Contact: {target_email}")
    print(f"📁 PST File: {pst_path}")
    print()
    
    # Create email attacher instance
    email_attacher = Dynamics365EmailAttacher(username, password)
    
    try:
        # Run the attachment process
        success = email_attacher.run_email_attachment(target_email, pst_path)
        
        if success:
            print("\n✅ Process completed successfully!")
            print("💡 Email timeline is now available in Dynamics 365 CRM")
        else:
            print("\n❌ Process failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        email_attacher.close_pst_file()
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        email_attacher.close_pst_file()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 