#!/usr/bin/env python3
"""
PST File Analyzer (Outlook COM version)
A Python application to analyze PST (Outlook Personal Storage) files
using Windows Outlook COM interface - No additional libraries required!

This version works by automating Outlook to open and read PST files.
It requires Outlook to be installed but has no 50-message limitation.
"""

import os
import sys
import win32com.client
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
from tabulate import tabulate
import re
import csv


class PSTAnalyzerCOM:
    def __init__(self, pst_file_path):
        """Initialize the PST analyzer with the path to the PST file."""
        self.pst_file_path = pst_file_path
        self.email_data = []
        self.all_email_addresses = defaultdict(lambda: {'count': 0, 'display_name': '', 'first_name': '', 'last_name': ''})
        self.outlook = None
        self.namespace = None
        self.pst_store = None
        
    def open_pst_file(self):
        """Open the PST file using Outlook COM interface."""
        try:
            if not os.path.exists(self.pst_file_path):
                raise FileNotFoundError(f"PST file not found: {self.pst_file_path}")
            
            print(f"✅ Starting Outlook COM interface...")
            
            # Create Outlook application object
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            
            print(f"📁 Opening PST file: {self.pst_file_path}")
            
            # Add PST file to Outlook
            self.namespace.AddStore(self.pst_file_path)
            
            # Find the PST store
            for store in self.namespace.Stores:
                if store.FilePath.lower() == self.pst_file_path.lower():
                    self.pst_store = store
                    break
            
            if not self.pst_store:
                raise Exception("Could not find PST store after adding")
            
            print(f"✅ PST file opened successfully: {self.pst_store.DisplayName}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening PST file: {str(e)}")
            return False
    
    def close_pst_file(self):
        """Close the PST file and cleanup COM objects."""
        try:
            if self.pst_store:
                # Remove PST store from Outlook
                self.namespace.RemoveStore(self.pst_store.GetRootFolder())
                print("✅ PST file closed successfully")
                
            # Cleanup COM objects
            if self.outlook:
                self.outlook = None
                self.namespace = None
                self.pst_store = None
                
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")
    
    def parse_name(self, display_name):
        """Parse display name to extract first and last name."""
        if not display_name:
            return '', ''
        
        # Clean up the display name
        name = display_name.strip()
        
        # Remove email addresses in parentheses or angle brackets
        name = re.sub(r'\s*[\(<][^)>]*@[^)>]*[\)>]\s*', '', name)
        name = re.sub(r'\s*<[^>]*>\s*', '', name)
        
        # Remove quotes
        name = name.replace('"', '').replace("'", "")
        
        # Remove extra parentheses content (like nicknames)
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
        
        # Clean up extra spaces
        name = ' '.join(name.split())
        
        if not name:
            return '', ''
        
        # Split into parts
        parts = name.split()
        
        if len(parts) == 0:
            return '', ''
        elif len(parts) == 1:
            # Only one name - could be first or last
            return parts[0], ''
        elif len(parts) == 2:
            # First and last name
            return parts[0], parts[1]
        else:
            # Multiple parts - first name is first part, last name is last part
            return parts[0], parts[-1]
    
    def is_real_email_address(self, email_addr):
        """Check if an email address is a real user email (not system-generated)."""
        if not email_addr:
            return False
        
        email_lower = email_addr.lower()
        
        # Filter out Microsoft Teams/Office 365 internal addresses
        if '@unq.gbl.spaces' in email_lower:
            return False
        
        # Filter out emails that are mostly GUIDs (contain multiple long hex sequences)
        guid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        if len(re.findall(guid_pattern, email_lower)) >= 2:
            return False
        
        # Filter out other system domains and patterns
        system_domains = [
            '@unq.gbl.spaces',
            '@outlook.com.invalid',
            '@teams.microsoft.com',
            '@quarantine.messaging.microsoft.com'
        ]
        
        for domain in system_domains:
            if email_lower.endswith(domain):
                return False
        
        # Filter out specific system email patterns
        system_patterns = [
            r'microsoftexchange[a-f0-9]+@',  # Exchange system emails
            r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_',  # GUID-based emails
            r'_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}@'  # Emails ending with GUID
        ]
        
        for pattern in system_patterns:
            if re.search(pattern, email_lower):
                return False
        
        # Filter out emails that are just long random strings
        local_part = email_lower.split('@')[0]
        if len(local_part) > 50:  # Very long local part likely system-generated
            return False
        
        return True

    def extract_email_address(self, email_string):
        """Extract email address from a string that might contain name and email."""
        if not email_string:
            return None
        
        # Look for email pattern in angle brackets
        match = re.search(r'<([^>]+@[^>]+)>', email_string)
        if match:
            email_addr = match.group(1).strip().lower()
            return email_addr if self.is_real_email_address(email_addr) else None
        
        # Look for standalone email pattern
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_string)
        if match:
            email_addr = match.group(0).strip().lower()
            return email_addr if self.is_real_email_address(email_addr) else None
        
        return None
    
    def record_email_address(self, email_string, is_sender=True):
        """Record an email address with name parsing."""
        if not email_string:
            return
        
        email_addr = self.extract_email_address(email_string)
        if not email_addr:
            return
        
        # Extract display name (everything before the email or the whole string if no email found)
        if '<' in email_string and '>' in email_string:
            display_name = email_string.split('<')[0].strip()
        else:
            # If no angle brackets, the whole string might be the display name
            display_name = email_string.strip()
            if '@' in display_name:
                display_name = ''  # It's just an email address
        
        # Parse the name
        first_name, last_name = self.parse_name(display_name)
        
        # Update the record
        record = self.all_email_addresses[email_addr]
        record['count'] += 1
        
        # Update display name if we have a better one
        if display_name and len(display_name) > len(record['display_name']):
            record['display_name'] = display_name
        
        # Update first/last names if we have better ones
        if first_name and len(first_name) > len(record['first_name']):
            record['first_name'] = first_name
        if last_name and len(last_name) > len(record['last_name']):
            record['last_name'] = last_name
    
    def extract_folder_messages(self, folder, folder_path=""):
        """Recursively extract messages from folders and subfolders."""
        current_path = f"{folder_path}/{folder.Name}" if folder_path else folder.Name
        
        # Skip Microsoft Teams chat messages - these are not real emails
        if "TeamsMessagesData" in current_path:
            print(f"📂 Skipping Teams folder: {current_path} (Teams chat messages, not emails)")
            return
        
        print(f"📂 Processing folder: {current_path}")
        
        # Process messages in current folder
        folder_message_count = 0
        expected_count = 0
        try:
            messages = folder.Items
            total_messages = messages.Count
            expected_count = total_messages
            
            if total_messages > 0:
                print(f"  📧 Found {total_messages} messages in {current_path}")
            
            for i in range(1, total_messages + 1):  # COM collections are 1-indexed
                try:
                    message = messages.Item(i)
                    email_info = self.extract_message_info(message, current_path)
                    if email_info:
                        self.email_data.append(email_info)
                        folder_message_count += 1
                        
                    # Progress indicator
                    if i % 100 == 0:
                        print(f"  📧 Processed {i}/{total_messages} messages in {current_path}")
                        
                except Exception as e:
                    print(f"⚠️  Error processing message {i}/{total_messages} in folder {current_path}: {str(e)}")
                    continue
            
            # Verification: Compare extracted count with expected count
            if folder_message_count == expected_count:
                if folder_message_count > 0:
                    print(f"  ✅ Completed folder {current_path}: {folder_message_count} messages extracted (100% success)")
            else:
                print(f"  ⚠️  VERIFICATION WARNING for {current_path}:")
                print(f"      Expected: {expected_count}, Extracted: {folder_message_count}")
                print(f"      Success rate: {(folder_message_count/expected_count)*100:.1f}%")
                    
        except Exception as e:
            print(f"⚠️  Error accessing messages in folder {current_path}: {str(e)}")
        
        # Process subfolders recursively
        try:
            subfolders = folder.Folders
            for i in range(1, subfolders.Count + 1):  # COM collections are 1-indexed
                subfolder = subfolders.Item(i)
                self.extract_folder_messages(subfolder, current_path)
        except Exception as e:
            print(f"⚠️  Error processing subfolders in {current_path}: {str(e)}")
    
    def extract_message_info(self, message, folder_path):
        """Extract relevant information from a message object."""
        try:
            # Get message properties safely
            subject = getattr(message, 'Subject', '') or 'No Subject'
            sender_name = getattr(message, 'SenderName', '') or 'Unknown'
            sender_email = getattr(message, 'SenderEmailAddress', '') or 'Unknown'
            recipients = getattr(message, 'To', '') or 'Unknown'
            
            # Record sender email address
            if sender_name and sender_email:
                if '@' in sender_email:
                    # Use sender email with display name
                    full_sender = f"{sender_name} <{sender_email}>"
                    self.record_email_address(full_sender, is_sender=True)
                else:
                    # Just use sender name (might contain email)
                    self.record_email_address(sender_name, is_sender=True)
            
            # Record recipient email addresses
            if recipients and recipients != 'Unknown':
                # Split multiple recipients (separated by semicolons)
                recipient_list = [r.strip() for r in recipients.split(';') if r.strip()]
                for recipient in recipient_list:
                    self.record_email_address(recipient, is_sender=False)
            
            # Also check CC and BCC fields if they exist
            try:
                cc_recipients = getattr(message, 'CC', '') or ''
                if cc_recipients:
                    cc_list = [r.strip() for r in cc_recipients.split(';') if r.strip()]
                    for cc_recipient in cc_list:
                        self.record_email_address(cc_recipient, is_sender=False)
                        
                bcc_recipients = getattr(message, 'BCC', '') or ''
                if bcc_recipients:
                    bcc_list = [r.strip() for r in bcc_recipients.split(';') if r.strip()]
                    for bcc_recipient in bcc_list:
                        self.record_email_address(bcc_recipient, is_sender=False)
            except:
                pass
            
            # Get dates
            creation_time = None
            delivery_time = None
            try:
                if hasattr(message, 'CreationTime'):
                    creation_time = message.CreationTime
                if hasattr(message, 'ReceivedTime'):
                    delivery_time = message.ReceivedTime
            except:
                pass
            
            # Get size and attachments
            size = getattr(message, 'Size', 0) or 0
            attachment_count = 0
            try:
                if hasattr(message, 'Attachments'):
                    attachment_count = message.Attachments.Count
            except:
                pass
            
            # Get importance
            importance = 'Normal'
            try:
                if hasattr(message, 'Importance'):
                    importance_val = message.Importance
                    if importance_val == 0:
                        importance = 'Low'
                    elif importance_val == 1:
                        importance = 'Normal'
                    elif importance_val == 2:
                        importance = 'High'
            except:
                pass
            
            email_info = {
                'folder': folder_path,
                'subject': subject,
                'sender': sender_name,
                'sender_email': sender_email,
                'recipients': recipients,
                'creation_time': creation_time,
                'delivery_time': delivery_time,
                'size': size,
                'has_attachments': attachment_count > 0,
                'attachment_count': attachment_count,
                'importance': importance
            }
            
            return email_info
            
        except Exception as e:
            print(f"⚠️  Error extracting message info: {str(e)}")
            return None
    
    def count_all_messages_independently(self):
        """Independent verification: Count all messages using a different method."""
        try:
            total_count = 0
            folder_counts = {}
            
            def count_folder_recursive(folder, path=""):
                nonlocal total_count
                current_path = f"{path}/{folder.Name}" if path else folder.Name
                
                # Skip Microsoft Teams chat messages - these are not real emails
                if "TeamsMessagesData" in current_path:
                    return
                
                # Count messages in this folder
                try:
                    message_count = folder.Items.Count
                    folder_counts[current_path] = message_count
                    total_count += message_count
                except:
                    folder_counts[current_path] = 0
                
                # Count subfolders
                try:
                    for i in range(1, folder.Folders.Count + 1):
                        subfolder = folder.Folders.Item(i)
                        count_folder_recursive(subfolder, current_path)
                except:
                    pass
            
            root_folder = self.pst_store.GetRootFolder()
            count_folder_recursive(root_folder)
            
            return total_count, folder_counts
            
        except Exception as e:
            print(f"⚠️  Error in independent count: {str(e)}")
            return 0, {}

    def analyze_pst_file(self):
        """Analyze the PST file."""
        if not self.pst_store:
            print("❌ PST file not opened. Call open_pst_file() first.")
            return False
        
        try:
            # First, do an independent count for verification
            print("🔍 Performing independent message count verification...")
            independent_total, independent_counts = self.count_all_messages_independently()
            print(f"📊 Independent verification found: {independent_total:,} total messages")
            
            print("\n📧 Starting email extraction...")
            
            # Get the root folder
            root_folder = self.pst_store.GetRootFolder()
            
            # Extract messages from all folders
            self.extract_folder_messages(root_folder)
            
            # Verification summary
            extracted_total = len(self.email_data)
            print(f"\n📊 EXTRACTION VERIFICATION SUMMARY:")
            print(f"   Independent count: {independent_total:,}")
            print(f"   Extracted count:   {extracted_total:,}")
            
            if extracted_total == independent_total:
                print(f"   ✅ SUCCESS: 100% of messages extracted!")
            else:
                success_rate = (extracted_total / independent_total) * 100 if independent_total > 0 else 0
                print(f"   ⚠️  WARNING: {success_rate:.1f}% extraction rate")
                print(f"   Missing: {independent_total - extracted_total:,} messages")
            
            print(f"\n✅ Extraction completed: {extracted_total:,} emails processed")
            return True
            
        except Exception as e:
            print(f"❌ Error during PST analysis: {str(e)}")
            return False

    def export_email_addresses_to_csv(self, filename="email_addresses.csv"):
        """Export all email addresses to a CSV file."""
        try:
            print(f"📊 Exporting email addresses to {filename}...")
            
            # Sort by frequency (count) in descending order
            sorted_addresses = sorted(
                self.all_email_addresses.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['email_address', 'first_name', 'last_name', 'display_name', 'count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data
                for email_addr, info in sorted_addresses:
                    writer.writerow({
                        'email_address': email_addr,
                        'first_name': info['first_name'],
                        'last_name': info['last_name'],
                        'display_name': info['display_name'],
                        'count': info['count']
                    })
            
            print(f"✅ Exported {len(sorted_addresses):,} unique email addresses to {filename}")
            
            # Show top 10 for verification
            print(f"\n📧 Top 10 Most Frequent Email Addresses:")
            top_10_table = []
            for i, (email_addr, info) in enumerate(sorted_addresses[:10]):
                name_display = f"{info['first_name']} {info['last_name']}".strip()
                if not name_display:
                    name_display = info['display_name'] or 'N/A'
                top_10_table.append([
                    f"{i+1}",
                    email_addr,
                    name_display,
                    f"{info['count']:,}"
                ])
            
            print(tabulate(top_10_table, 
                         headers=['Rank', 'Email Address', 'Name', 'Count'], 
                         tablefmt='grid'))
            
            return True
            
        except Exception as e:
            print(f"❌ Error exporting email addresses: {str(e)}")
            return False

    def generate_statistics(self):
        """Generate comprehensive statistics about the emails."""
        if not self.email_data:
            print("❌ No email data available. Run analyze_pst_file() first.")
            return
        
        print("\n" + "="*60)
        print("📊 PST FILE STATISTICS (Outlook COM version)")
        print("="*60)
        
        # Basic counts
        total_emails = len(self.email_data)
        print(f"📧 Total Emails: {total_emails:,}")
        
        # Folder statistics
        folder_counts = Counter(email['folder'] for email in self.email_data)
        print(f"\n📁 Emails by Folder:")
        folder_table = [[folder, count] for folder, count in folder_counts.most_common(15)]
        print(tabulate(folder_table, headers=['Folder', 'Email Count'], tablefmt='grid'))
        
        # Sender statistics
        sender_counts = Counter(email['sender'] for email in self.email_data if email['sender'] != 'Unknown')
        print(f"\n👤 Top 15 Senders:")
        sender_table = [[sender, count] for sender, count in sender_counts.most_common(15)]
        print(tabulate(sender_table, headers=['Sender', 'Email Count'], tablefmt='grid'))
        
        # Size statistics
        sizes = [email['size'] for email in self.email_data if email['size'] > 0]
        if sizes:
            total_size = sum(sizes)
            avg_size = total_size / len(sizes)
            max_size = max(sizes)
            
            print(f"\n💾 Size Statistics:")
            size_stats = [
                ['Total Size', f"{total_size / (1024*1024):.2f} MB"],
                ['Average Size', f"{avg_size / 1024:.2f} KB"],
                ['Largest Email', f"{max_size / 1024:.2f} KB"],
                ['Emails with Size Data', f"{len(sizes):,}"]
            ]
            print(tabulate(size_stats, headers=['Metric', 'Value'], tablefmt='grid'))
        
        # Attachment statistics
        emails_with_attachments = sum(1 for email in self.email_data if email['has_attachments'])
        total_attachments = sum(email['attachment_count'] for email in self.email_data)
        
        print(f"\n📎 Attachment Statistics:")
        attachment_stats = [
            ['Emails with Attachments', f"{emails_with_attachments:,}"],
            ['Total Attachments', f"{total_attachments:,}"],
            ['Percentage with Attachments', f"{(emails_with_attachments/total_emails)*100:.1f}%"]
        ]
        print(tabulate(attachment_stats, headers=['Metric', 'Value'], tablefmt='grid'))
        
        # Date range analysis
        dates = [email['creation_time'] for email in self.email_data if email['creation_time']]
        if dates:
            earliest_date = min(dates)
            latest_date = max(dates)
            
            print(f"\n📅 Date Range:")
            date_stats = [
                ['Earliest Email', earliest_date.strftime('%Y-%m-%d %H:%M:%S')],
                ['Latest Email', latest_date.strftime('%Y-%m-%d %H:%M:%S')],
                ['Date Range', f"{(latest_date - earliest_date).days} days"],
                ['Emails with Date Data', f"{len(dates):,}"]
            ]
            print(tabulate(date_stats, headers=['Metric', 'Value'], tablefmt='grid'))
        
        # Importance analysis
        importance_counts = Counter(email['importance'] for email in self.email_data)
        if len(importance_counts) > 1:
            print(f"\n⚡ Email Importance:")
            importance_table = [[importance, count] for importance, count in importance_counts.most_common()]
            print(tabulate(importance_table, headers=['Importance', 'Count'], tablefmt='grid'))
        
        # Subject analysis (most common words)
        subjects = [email['subject'] for email in self.email_data if email['subject'] and email['subject'] != 'No Subject']
        if subjects:
            # Simple word frequency analysis
            all_words = []
            for subject in subjects:
                words = subject.lower().split()
                # Filter out common short words and special characters
                filtered_words = [word.strip('.,!?:;[](){}') for word in words 
                                  if len(word) > 3 and word.isalpha()]
                all_words.extend(filtered_words)
            
            if all_words:
                word_counts = Counter(all_words)
                print(f"\n🔤 Most Common Subject Words:")
                word_table = [[word, count] for word, count in word_counts.most_common(15)]
                print(tabulate(word_table, headers=['Word', 'Count'], tablefmt='grid'))
        
        print("\n" + "="*60)


def main():
    """Main function to run the PST analyzer."""
    print("🔍 PST File Analyzer (Outlook COM version)")
    print("="*55)
    print("   Requires: Microsoft Outlook installed on this machine")
    print()
    
    # PST file path
    pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    print(f"📁 Target PST file: {pst_file_path}")
    
    # Create analyzer instance
    analyzer = PSTAnalyzerCOM(pst_file_path)
    
    try:
        # Open PST file
        if not analyzer.open_pst_file():
            sys.exit(1)
        
        # Analyze PST file
        if not analyzer.analyze_pst_file():
            sys.exit(1)
        
        # Generate statistics
        analyzer.generate_statistics()
        
        # Export email addresses to CSV
        analyzer.export_email_addresses_to_csv("email_addresses.csv")
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Always cleanup
        analyzer.close_pst_file()


if __name__ == "__main__":
    main() 