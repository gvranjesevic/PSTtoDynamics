#!/usr/bin/env python3
"""
PST File Analyzer (libratom version)
A Python application to analyze PST (Outlook Personal Storage) files
using the libratom library for better Windows compatibility.
"""

logger = logging.getLogger(__name__)

import os
import logging
import sys
import sqlite3
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
from tabulate import tabulate
from pathlib import Path

# Import libratom for PST processing
try:
    from libratom.lib.pst import PSTFile
    from libratom.lib.core import open_file
except ImportError:
    logger.error("❌ libratom not found. Install it with: pip install libratom")
    sys.exit(1)


class PSTAnalyzerLibratom:
    def __init__(self, pst_file_path):
        """Initialize the PST analyzer with the path to the PST file."""
        self.pst_file_path = pst_file_path
        self.email_data = []
        
    def analyze_pst_file(self):
        """Analyze the PST file using libratom."""
        try:
            if not os.path.exists(self.pst_file_path):
                raise FileNotFoundError(f"PST file not found: {self.pst_file_path}")
            
            logger.info("✅ Opening PST file: {self.pst_file_path}")
            
            # Use libratom to process the PST file
            pst_file = PSTFile(self.pst_file_path)
            
            logger.info("📧 Extracting email messages...")
            
            # Extract messages from the PST file
            message_count = 0
            for message in pst_file.messages():
                try:
                    email_info = self.extract_message_info(message)
                    if email_info:
                        self.email_data.append(email_info)
                        message_count += 1
                        
                        # Progress indicator
                        if message_count % 100 == 0:
                            logger.info("📊 Processed {message_count} messages...")
                            
                except Exception as e:
                    logger.warning("⚠️  Error processing message: {str(e)}")
                    continue
            
            logger.info("✅ Successfully extracted {len(self.email_data)} emails")
            return True
            
        except Exception as e:
            logger.error("❌ Error analyzing PST file: {str(e)}")
            return False
    
    def extract_message_info(self, message):
        """Extract relevant information from a message object."""
        try:
            # Get message properties safely
            subject = getattr(message, 'subject', '') or 'No Subject'
            sender_name = getattr(message, 'sender_name', '') or 'Unknown'
            sender_email = getattr(message, 'sender_email_address', '') or 'Unknown'
            recipients = getattr(message, 'display_to', '') or 'Unknown'
            
            # Handle dates
            creation_time = None
            delivery_time = None
            
            if hasattr(message, 'creation_time') and message.creation_time:
                creation_time = message.creation_time
            if hasattr(message, 'delivery_time') and message.delivery_time:
                delivery_time = message.delivery_time
                
            # Get size and attachments
            size = getattr(message, 'message_size', 0) or 0
            attachment_count = getattr(message, 'number_of_attachments', 0) or 0
            
            # Get folder path if available
            folder_path = getattr(message, 'folder_path', 'Unknown') or 'Unknown'
            
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
                'attachment_count': attachment_count
            }
            
            return email_info
            
        except Exception as e:
            logger.warning("⚠️  Error extracting message info: {str(e)}")
            return None
    
    def generate_statistics(self):
        """Generate comprehensive statistics about the emails."""
        if not self.email_data:
            logger.error("❌ No email data available. Run analyze_pst_file() first.")
            return
        
        logger.debug("\n" + "="*60)
        logger.info("📊 PST FILE STATISTICS (libratom version)")
        logger.debug("="*60)
        
        # Basic counts
        total_emails = len(self.email_data)
        logger.info("📧 Total Emails: {total_emails:,}")
        
        # Folder statistics
        folder_counts = Counter(email['folder'] for email in self.email_data)
        logger.debug("\n📁 Emails by Folder:")
        folder_table = [[folder, count] for folder, count in folder_counts.most_common(10)]
        print(tabulate(folder_table, headers=['Folder', 'Email Count'], tablefmt='grid'))
        
        # Sender statistics
        sender_counts = Counter(email['sender'] for email in self.email_data if email['sender'] != 'Unknown')
        logger.debug("\n👤 Top 10 Senders:")
        sender_table = [[sender, count] for sender, count in sender_counts.most_common(10)]
        print(tabulate(sender_table, headers=['Sender', 'Email Count'], tablefmt='grid'))
        
        # Size statistics
        sizes = [email['size'] for email in self.email_data if email['size'] > 0]
        if sizes:
            total_size = sum(sizes)
            avg_size = total_size / len(sizes)
            max_size = max(sizes)
            
            logger.debug("\n💾 Size Statistics:")
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
        
        # Subject analysis (most common words)
        subjects = [email['subject'] for email in self.email_data if email['subject'] and email['subject'] != 'No Subject']
        if subjects:
            # Simple word frequency analysis
            all_words = []
            for subject in subjects:
                words = subject.lower().split()
                # Filter out common short words
                filtered_words = [word for word in words if len(word) > 3 and word.isalpha()]
                all_words.extend(filtered_words)
            
            if all_words:
                word_counts = Counter(all_words)
                logger.debug("\n🔤 Most Common Subject Words:")
                word_table = [[word, count] for word, count in word_counts.most_common(10)]
                print(tabulate(word_table, headers=['Word', 'Count'], tablefmt='grid'))
        
        logger.debug("\n" + "="*60)


def main():
    """Main function to run the PST analyzer."""
    # PST file path
    pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    logger.info("🔍 PST File Analyzer (libratom version)")
    logger.debug("="*50)
    logger.info("📁 Target PST file: {pst_file_path}")
    
    # Create analyzer instance
    analyzer = PSTAnalyzerLibratom(pst_file_path)
    
    try:
        # Analyze PST file
        if not analyzer.analyze_pst_file():
            sys.exit(1)
        
        # Generate statistics
        analyzer.generate_statistics()
        
    except KeyboardInterrupt:
        logger.debug("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        logger.error("❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 