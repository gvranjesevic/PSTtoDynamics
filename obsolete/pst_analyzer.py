#!/usr/bin/env python3
"""
PST File Analyzer
A simple Python application to analyze PST (Outlook Personal Storage) files
and provide basic email statistics.
"""

logger = logging.getLogger(__name__)

import os
import logging
import sys
import pypff
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
from tabulate import tabulate


class PSTAnalyzer:
    def __init__(self, pst_file_path):
        """Initialize the PST analyzer with the path to the PST file."""
        self.pst_file_path = pst_file_path
        self.pst_file = None
        self.email_data = []
        
    def open_pst_file(self):
        """Open the PST file for reading."""
        try:
            if not os.path.exists(self.pst_file_path):
                raise FileNotFoundError(f"PST file not found: {self.pst_file_path}")
            
            self.pst_file = pypff.file()
            self.pst_file.open(self.pst_file_path)
            logger.info("✅ Successfully opened PST file: {self.pst_file_path}")
            return True
            
        except Exception as e:
            logger.error("❌ Error opening PST file: {str(e)}")
            return False
    
    def close_pst_file(self):
        """Close the PST file."""
        if self.pst_file:
            self.pst_file.close()
            logger.info("✅ PST file closed successfully")
    
    def extract_folder_emails(self, folder, folder_path=""):
        """Recursively extract emails from folders and subfolders."""
        current_path = f"{folder_path}/{folder.name}" if folder_path else folder.name
        
        # Process emails in current folder
        for i in range(folder.number_of_sub_messages):
            try:
                message = folder.get_sub_message(i)
                email_info = self.extract_email_info(message, current_path)
                if email_info:
                    self.email_data.append(email_info)
            except Exception as e:
                logger.warning("⚠️  Error processing message {i} in folder {current_path}: {str(e)}")
        
        # Process subfolders recursively
        for j in range(folder.number_of_sub_folders):
            try:
                subfolder = folder.get_sub_folder(j)
                self.extract_folder_emails(subfolder, current_path)
            except Exception as e:
                logger.warning("⚠️  Error processing subfolder {j} in {current_path}: {str(e)}")
    
    def extract_email_info(self, message, folder_path):
        """Extract relevant information from an email message."""
        try:
            email_info = {
                'folder': folder_path,
                'subject': getattr(message, 'subject', 'No Subject'),
                'sender': getattr(message, 'sender_name', 'Unknown'),
                'sender_email': getattr(message, 'sender_email_address', 'Unknown'),
                'recipients': getattr(message, 'display_to', 'Unknown'),
                'creation_time': getattr(message, 'creation_time', None),
                'delivery_time': getattr(message, 'delivery_time', None),
                'size': getattr(message, 'size', 0),
                'message_class': getattr(message, 'message_class', 'Unknown'),
                'has_attachments': getattr(message, 'number_of_attachments', 0) > 0,
                'attachment_count': getattr(message, 'number_of_attachments', 0)
            }
            return email_info
        except Exception as e:
            logger.warning("⚠️  Error extracting email info: {str(e)}")
            return None
    
    def analyze_emails(self):
        """Extract all emails from the PST file."""
        if not self.pst_file:
            logger.error("❌ PST file not opened. Call open_pst_file() first.")
            return False
        
        try:
            logger.info("📧 Starting email extraction...")
            
            # Get the root folder
            root_folder = self.pst_file.get_root_folder()
            
            # Extract emails from all folders
            self.extract_folder_emails(root_folder)
            
            logger.info("✅ Extracted {len(self.email_data)} emails successfully")
            return True
            
        except Exception as e:
            logger.error("❌ Error during email analysis: {str(e)}")
            return False
    
    def generate_statistics(self):
        """Generate comprehensive statistics about the emails."""
        if not self.email_data:
            logger.error("❌ No email data available. Run analyze_emails() first.")
            return
        
        logger.debug("\n" + "="*60)
        logger.info("📊 PST FILE STATISTICS")
        logger.debug("="*60)
        
        # Basic counts
        total_emails = len(self.email_data)
        logger.info("📧 Total Emails: {total_emails:,}")
        
        # Folder statistics
        folder_counts = Counter(email['folder'] for email in self.email_data)
        logger.debug("\n📁 Emails by Folder:")
        folder_table = [[folder, count] for folder, count in folder_counts.most_common()]
        print(tabulate(folder_table, headers=['Folder', 'Email Count'], tablefmt='grid'))
        
        # Sender statistics
        sender_counts = Counter(email['sender'] for email in self.email_data)
        logger.debug("\n👤 Top 10 Senders:")
        sender_table = [[sender, count] for sender, count in sender_counts.most_common(10)]
        print(tabulate(sender_table, headers=['Sender', 'Email Count'], tablefmt='grid'))
        
        # Size statistics
        total_size = sum(email['size'] for email in self.email_data if email['size'])
        avg_size = total_size / total_emails if total_emails > 0 else 0
        max_size = max((email['size'] for email in self.email_data if email['size']), default=0)
        
        logger.debug("\n💾 Size Statistics:")
        size_stats = [
            ['Total Size', f"{total_size / (1024*1024):.2f} MB"],
            ['Average Size', f"{avg_size / 1024:.2f} KB"],
            ['Largest Email', f"{max_size / 1024:.2f} KB"]
        ]
        print(tabulate(size_stats, headers=['Metric', 'Value'], tablefmt='grid'))
        
        # Attachment statistics
        emails_with_attachments = sum(1 for email in self.email_data if email['has_attachments'])
        total_attachments = sum(email['attachment_count'] for email in self.email_data)
        
        logger.debug("\n📎 Attachment Statistics:")
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
            
            logger.debug("\n📅 Date Range:")
            date_stats = [
                ['Earliest Email', earliest_date.strftime('%Y-%m-%d %H:%M:%S')],
                ['Latest Email', latest_date.strftime('%Y-%m-%d %H:%M:%S')],
                ['Date Range', f"{(latest_date - earliest_date).days} days"]
            ]
            print(tabulate(date_stats, headers=['Metric', 'Value'], tablefmt='grid'))
        
        logger.debug("\n" + "="*60)


def main():
    """Main function to run the PST analyzer."""
    # PST file path
    pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    logger.info("🔍 PST File Analyzer")
    logger.debug("="*50)
    logger.info("📁 Target PST file: {pst_file_path}")
    
    # Create analyzer instance
    analyzer = PSTAnalyzer(pst_file_path)
    
    try:
        # Open PST file
        if not analyzer.open_pst_file():
            sys.exit(1)
        
        # Analyze emails
        if not analyzer.analyze_emails():
            sys.exit(1)
        
        # Generate statistics
        analyzer.generate_statistics()
        
    except KeyboardInterrupt:
        logger.debug("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        logger.error("❌ Unexpected error: {str(e)}")
    finally:
        # Clean up
        analyzer.close_pst_file()


if __name__ == "__main__":
    main() 