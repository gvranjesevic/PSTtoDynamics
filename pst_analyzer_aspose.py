#!/usr/bin/env python3
"""
PST File Analyzer (Aspose.Email version)
A Python application to analyze PST (Outlook Personal Storage) files
using the Aspose.Email library for reliable Windows compatibility.

NOTE: The evaluation version of Aspose.Email has a limitation of only 50 emails
per folder. To extract all emails, you need either:
1. A valid Aspose.Email license file
2. A temporary license (free for 30 days) from: https://purchase.aspose.com/temporary-license
3. Or use one of the alternative implementations (pypff or libratom versions)

If you have a license file, place it in the same directory as this script.
"""

import os
import sys
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
from tabulate import tabulate

# Import Aspose.Email for PST processing
try:
    import aspose.email as ae
    from aspose.email.storage.pst import PersonalStorage, StandardIpmFolder
except ImportError:
    print("❌ Aspose.Email not found. Install it with: pip install aspose-email")
    sys.exit(1)


def apply_license():
    """Try to apply Aspose.Email license to remove evaluation limitations."""
    license_files = [
        "Aspose.Email.lic",
        "Aspose.Email.Python.lic", 
        "Aspose.Total.lic",
        "Aspose.Total.Python.lic"
    ]
    
    for license_file in license_files:
        if os.path.exists(license_file):
            try:
                license = ae.License()
                license.set_license(license_file)
                print(f"✅ License applied successfully: {license_file}")
                return True
            except Exception as e:
                print(f"⚠️  Error applying license {license_file}: {str(e)}")
                continue
    
    print("⚠️  No valid license found. Using evaluation version (50 emails per folder limit)")
    print("   To remove this limitation:")
    print("   1. Get a free temporary license: https://purchase.aspose.com/temporary-license")
    print("   2. Place license file in the same directory as this script")
    print("   3. Or use the pypff/libratom alternatives for unlimited extraction")
    return False


class PSTAnalyzerAspose:
    def __init__(self, pst_file_path):
        """Initialize the PST analyzer with the path to the PST file."""
        self.pst_file_path = pst_file_path
        self.email_data = []
        self.pst = None
        
    def open_pst_file(self):
        """Open the PST file for reading."""
        try:
            if not os.path.exists(self.pst_file_path):
                raise FileNotFoundError(f"PST file not found: {self.pst_file_path}")
            
            print(f"✅ Opening PST file: {self.pst_file_path}")
            self.pst = PersonalStorage.from_file(self.pst_file_path)
            
            print(f"📁 PST file opened successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error opening PST file: {str(e)}")
            return False
    
    def close_pst_file(self):
        """Close the PST file."""
        if self.pst:
            # Aspose PersonalStorage doesn't have dispose method, just set to None
            self.pst = None
            print("✅ PST file closed successfully")
    
    def extract_folder_messages(self, folder, folder_path=""):
        """Recursively extract messages from folders and subfolders."""
        current_path = f"{folder_path}/{folder.display_name}" if folder_path else folder.display_name
        
        print(f"📂 Processing folder: {current_path}")
        
        # Process messages in current folder
        folder_message_count = 0
        try:
            messages = folder.get_contents()
            total_messages = len(list(messages))  # Get total count first
            messages = folder.get_contents()  # Get fresh iterator
            
            if total_messages > 0:
                print(f"  📧 Found {total_messages} messages in {current_path}")
            
            for i, message_info in enumerate(messages):
                try:
                    # Extract message from PST
                    message = self.pst.extract_message(message_info)
                    email_info = self.extract_message_info(message, current_path)
                    if email_info:
                        self.email_data.append(email_info)
                        folder_message_count += 1
                        
                    # Progress indicator
                    if (i + 1) % 100 == 0:
                        print(f"  📧 Processed {i + 1}/{total_messages} messages in {current_path}")
                        
                except Exception as e:
                    print(f"⚠️  Error processing message {i+1}/{total_messages} in folder {current_path}: {str(e)}")
                    continue
            
            # Final count for this folder
            if folder_message_count > 0:
                print(f"  ✅ Completed folder {current_path}: {folder_message_count} messages extracted")
                    
        except Exception as e:
            print(f"⚠️  Error accessing messages in folder {current_path}: {str(e)}")
        
        # Process subfolders recursively
        try:
            subfolders = folder.get_sub_folders()
            for subfolder in subfolders:
                self.extract_folder_messages(subfolder, current_path)
        except Exception as e:
            print(f"⚠️  Error processing subfolders in {current_path}: {str(e)}")
    
    def extract_message_info(self, message, folder_path):
        """Extract relevant information from a message object."""
        try:
            # Get message properties safely using MAPI properties
            subject = getattr(message, 'subject', '') or 'No Subject'
            
            # For MAPI messages, use sender_name and sender_email_address
            sender_name = getattr(message, 'sender_name', '') or 'Unknown'
            sender_email = getattr(message, 'sender_email_address', '') or 'Unknown'
            
            # Get recipients - try different properties
            recipients_str = 'Unknown'
            try:
                if hasattr(message, 'display_to') and message.display_to:
                    recipients_str = message.display_to
                elif hasattr(message, 'recipients') and message.recipients:
                    recipients_list = []
                    for recipient in message.recipients:
                        if hasattr(recipient, 'display_name') and recipient.display_name:
                            recipients_list.append(recipient.display_name)
                        elif hasattr(recipient, 'email_address') and recipient.email_address:
                            recipients_list.append(recipient.email_address)
                    recipients_str = "; ".join(recipients_list) if recipients_list else 'Unknown'
            except:
                pass
            
            # Get dates
            creation_time = None
            delivery_time = None
            try:
                if hasattr(message, 'creation_time') and message.creation_time:
                    creation_time = message.creation_time
                if hasattr(message, 'client_submit_time') and message.client_submit_time:
                    delivery_time = message.client_submit_time
                elif hasattr(message, 'delivery_time') and message.delivery_time:
                    delivery_time = message.delivery_time
            except:
                pass
            
            # Get size and attachments
            size = 0
            attachment_count = 0
            try:
                if hasattr(message, 'message_size'):
                    size = message.message_size or 0
                if hasattr(message, 'attachments') and message.attachments:
                    attachment_count = message.attachments.count()
            except:
                pass
            
            # Get priority
            priority = 'Normal'
            try:
                if hasattr(message, 'priority'):
                    priority = str(message.priority)
            except:
                pass
            
            email_info = {
                'folder': folder_path,
                'subject': subject,
                'sender': sender_name,
                'sender_email': sender_email,
                'recipients': recipients_str,
                'creation_time': creation_time,
                'delivery_time': delivery_time,
                'size': size,
                'has_attachments': attachment_count > 0,
                'attachment_count': attachment_count,
                'priority': priority
            }
            
            return email_info
            
        except Exception as e:
            print(f"⚠️  Error extracting message info: {str(e)}")
            return None
    
    def analyze_pst_file(self):
        """Analyze the PST file."""
        if not self.pst:
            print("❌ PST file not opened. Call open_pst_file() first.")
            return False
        
        try:
            print("📧 Starting email extraction...")
            
            # Get the root folder
            root_folder = self.pst.root_folder
            
            # Extract messages from all folders
            self.extract_folder_messages(root_folder)
            
            print(f"✅ Extracted {len(self.email_data)} emails successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during PST analysis: {str(e)}")
            return False
    
    def generate_statistics(self):
        """Generate comprehensive statistics about the emails."""
        if not self.email_data:
            print("❌ No email data available. Run analyze_pst_file() first.")
            return
        
        print("\n" + "="*60)
        print("📊 PST FILE STATISTICS (Aspose.Email version)")
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
        
        # Priority analysis
        priorities = [email['priority'] for email in self.email_data if email['priority'] != 'Normal']
        if priorities:
            priority_counts = Counter(priorities)
            print(f"\n⚡ Email Priorities (non-normal):")
            priority_table = [[priority, count] for priority, count in priority_counts.most_common()]
            print(tabulate(priority_table, headers=['Priority', 'Count'], tablefmt='grid'))
        
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
    print("🔍 PST File Analyzer (Aspose.Email version)")
    print("="*55)
    
    # Try to apply license to remove evaluation limitations
    apply_license()
    print()
    
    # PST file path
    pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    print(f"📁 Target PST file: {pst_file_path}")
    
    # Create analyzer instance
    analyzer = PSTAnalyzerAspose(pst_file_path)
    
    try:
        # Open PST file
        if not analyzer.open_pst_file():
            sys.exit(1)
        
        # Analyze PST file
        if not analyzer.analyze_pst_file():
            sys.exit(1)
        
        # Generate statistics
        analyzer.generate_statistics()
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        analyzer.close_pst_file()


if __name__ == "__main__":
    main() 