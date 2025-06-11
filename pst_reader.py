"""
PST Reader Module
================

Handles reading and extracting emails from PST files using Outlook COM.
"""

import win32com.client
import os
import re
from typing import Dict, List, Optional
from collections import defaultdict
import config


class PSTReader:
    """Handles reading emails from PST files."""
    
    def __init__(self, pst_path: str = None):
        self.pst_path = pst_path or config.CURRENT_PST_PATH
        self.outlook = None
        self.namespace = None
        self.pst_store = None
        self.temp_store_added = False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.disconnect()
    
    def connect(self) -> bool:
        """
        Connects to Outlook and opens the PST file.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not os.path.exists(self.pst_path):
            print(f"❌ PST file not found: {self.pst_path}")
            return False
        
        try:
            print(f"📁 Connecting to PST: {self.pst_path}")
            
            # Initialize Outlook application
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            
            # Check if PST is already loaded
            for store in self.namespace.Stores:
                if self.pst_path.lower() in str(store.FilePath).lower():
                    self.pst_store = store
                    print("   ✅ PST already loaded in Outlook")
                    return True
            
            # If not loaded, add it temporarily
            self.namespace.AddStore(self.pst_path)
            self.temp_store_added = True
            print("   ✅ PST temporarily added to Outlook")
            
            # Find the newly added store
            for store in self.namespace.Stores:
                if self.pst_path.lower() in str(store.FilePath).lower():
                    self.pst_store = store
                    return True
            
            print("   ❌ Could not access PST store after adding")
            return False
            
        except Exception as e:
            print(f"❌ Error connecting to PST: {e}")
            return False
    
    def disconnect(self):
        """Disconnects from PST and cleans up."""
        if self.temp_store_added and self.pst_store:
            try:
                self.namespace.RemoveStore(self.pst_store.StoreID)
                print("   🧹 Cleaned up temporary PST store")
            except Exception as e:
                print(f"   ⚠️ Could not clean up PST store: {e}")
        
        self.outlook = None
        self.namespace = None
        self.pst_store = None
        self.temp_store_added = False
    
    @staticmethod
    def extract_email_address(email_string) -> Optional[str]:
        """
        Extracts email address from various formats.
        
        Args:
            email_string: String that may contain an email address
            
        Returns:
            Cleaned email address or None
        """
        if not email_string:
            return None
        
        email_string = str(email_string)
        
        # Look for email in angle brackets first
        match = re.search(r'<([^>]+@[^>]+)>', email_string)
        if match:
            return match.group(1).lower().strip()
        
        # If no brackets, check if the whole string is an email
        if '@' in email_string and '.' in email_string:
            return email_string.lower().strip()
        
        return None
    
    def _extract_sender_email(self, item) -> Optional[str]:
        """
        Extracts sender email from an email item using multiple methods.
        
        Args:
            item: Outlook mail item
            
        Returns:
            Sender email address or None
        """
        sender_email = None
        
        # Method 1: SenderEmailAddress
        if hasattr(item, 'SenderEmailAddress') and item.SenderEmailAddress:
            sender_email = self.extract_email_address(item.SenderEmailAddress)
        
        # Method 2: If sender email is Exchange format, try Reply Recipients
        if not sender_email and hasattr(item, 'ReplyRecipients'):
            try:
                for recipient in item.ReplyRecipients:
                    if hasattr(recipient, 'Address'):
                        sender_email = self.extract_email_address(recipient.Address)
                        if sender_email:
                            break
            except:
                pass
        
        # Method 3: Try Sender property
        if not sender_email and hasattr(item, 'Sender') and item.Sender:
            try:
                if hasattr(item.Sender, 'Address'):
                    sender_email = self.extract_email_address(item.Sender.Address)
            except:
                pass
        
        return sender_email
    
    def _is_teams_message(self, item) -> bool:
        """
        Checks if an email is a Microsoft Teams message.
        
        Args:
            item: Outlook mail item
            
        Returns:
            True if it's a Teams message
        """
        if not config.EXCLUDE_TEAMS_MESSAGES:
            return False
        
        try:
            # Check for Teams indicators
            sender_name = getattr(item, 'SenderName', '') or ''
            subject = getattr(item, 'Subject', '') or ''
            
            teams_indicators = [
                'Microsoft Teams',
                'Teams Notification',
                'teams.microsoft.com'
            ]
            
            for indicator in teams_indicators:
                if indicator.lower() in sender_name.lower() or indicator.lower() in subject.lower():
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def _extract_message_id(self, item) -> Optional[str]:
        """
        Extract Message-ID from email for advanced duplicate detection.
        
        Args:
            item: Outlook mail item
            
        Returns:
            Message-ID string or None
        """
        try:
            # Try PropertyAccessor to get Message-ID
            if hasattr(item, 'PropertyAccessor'):
                try:
                    # Standard Message-ID property
                    message_id = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001E")
                    if message_id:
                        return message_id.strip('<>')
                except:
                    pass
            
            # Try Internet Message-ID property  
            try:
                message_id = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1035001F")
                if message_id:
                    return message_id.strip('<>')
            except:
                pass
                
            # Alternative property tags for Message-ID
            message_id_properties = [
                "http://schemas.microsoft.com/mapi/id/{00062008-0000-0000-C000-000000000046}/0x1035",
                "http://schemas.microsoft.com/mapi/string/{00020386-0000-0000-C000-000000000046}/content-id"
            ]
            
            for prop in message_id_properties:
                try:
                    message_id = item.PropertyAccessor.GetProperty(prop)
                    if message_id:
                        return message_id.strip('<>')
                except:
                    continue
                    
        except Exception as e:
            # Silently handle - Message-ID is optional
            pass
        
        return None
    
    def _extract_basic_headers(self, item) -> Dict[str, str]:
        """
        Extract basic email headers for comparison.
        
        Args:
            item: Outlook mail item
            
        Returns:
            Dictionary of headers
        """
        headers = {}
        
        try:
            # Standard headers
            headers['Subject'] = getattr(item, 'Subject', '') or ''
            headers['From'] = getattr(item, 'SenderEmailAddress', '') or ''
            headers['To'] = getattr(item, 'To', '') or ''
            headers['Date'] = str(getattr(item, 'SentOn', '') or '')
            
            # Try to get additional headers via PropertyAccessor
            if hasattr(item, 'PropertyAccessor'):
                try:
                    # Return-Path
                    return_path = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1046001E")
                    if return_path:
                        headers['Return-Path'] = return_path
                except:
                    pass
                
                try:
                    # Reply-To
                    reply_to = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x1042001E")
                    if reply_to:
                        headers['Reply-To'] = reply_to
                except:
                    pass
                    
        except Exception as e:
            # Headers are optional - don't break on failure
            pass
        
        return headers
    
    def _scan_folder_recursive(self, folder, emails_by_sender: Dict, total_emails: int, depth=0) -> int:
        """
        Recursively scans a folder and its subfolders for emails.
        
        Args:
            folder: Outlook folder object
            emails_by_sender: Dictionary to store emails grouped by sender
            total_emails: Current total email count
            depth: Folder depth for indentation
            
        Returns:
            Updated total email count
        """
        indent = "   " + "  " * depth
        
        try:
            print(f"{indent}📁 Scanning folder: {folder.Name}")
            items = folder.Items
            
            folder_emails = 0
            for item in items:
                try:
                    # Check if it's a mail item (Class 43)
                    if not (hasattr(item, 'Class') and item.Class == 43):
                        continue
                    
                    # Skip Teams messages if configured
                    if self._is_teams_message(item):
                        continue
                    
                    # Extract sender email
                    sender_email = self._extract_sender_email(item)
                    if not sender_email:
                        continue
                    
                    # Check email body length
                    body = getattr(item, 'Body', '') or ''
                    if len(body.strip()) < config.MIN_EMAIL_LENGTH:
                        continue
                    
                    # Extract Message-ID for advanced duplicate detection
                    message_id = self._extract_message_id(item)
                    
                    # Create email data
                    email_data = {
                        'subject': getattr(item, 'Subject', '') or 'No Subject',
                        'body': body,
                        'received_time': getattr(item, 'ReceivedTime', None) or getattr(item, 'CreationTime', None),
                        'sent_time': getattr(item, 'SentOn', None) or getattr(item, 'CreationTime', None),
                        'sender_name': getattr(item, 'SenderName', '') or '',
                        'sender_email': sender_email,
                        'folder_path': folder.Name,
                        'message_id': message_id,
                        'headers': self._extract_basic_headers(item)
                    }
                    
                    emails_by_sender[sender_email].append(email_data)
                    total_emails += 1
                    folder_emails += 1
                    
                    # Progress indicator
                    if total_emails % 50 == 0:
                        print(f"   📧 Processed {total_emails} emails so far...")
                        
                except Exception as e:
                    print(f"{indent}  ⚠️ Error processing email: {e}")
            
            print(f"{indent}  ✅ Found {folder_emails} emails in this folder")
            
            # Recursively scan subfolders
            try:
                for subfolder in folder.Folders:
                    total_emails = self._scan_folder_recursive(subfolder, emails_by_sender, total_emails, depth + 1)
            except Exception as e:
                print(f"{indent}  ⚠️ Error scanning subfolders: {e}")
                
        except Exception as e:
            print(f"{indent}❌ Error scanning folder {folder.Name}: {e}")
        
        return total_emails
    
    def scan_emails(self) -> Dict[str, List[Dict]]:
        """
        Scans the PST file for all emails and groups them by sender.
        
        Returns:
            Dictionary with sender emails as keys and lists of email data as values
        """
        if not self.pst_store:
            if not self.connect():
                return {}
        
        print(f"📧 Starting email scan...")
        
        emails_by_sender = defaultdict(list)
        total_emails = 0
        
        try:
            root_folder = self.pst_store.GetRootFolder()
            print(f"   📂 Root folder: {root_folder.Name}")
            
            total_emails = self._scan_folder_recursive(root_folder, emails_by_sender, total_emails)
            
            print(f"\n✅ PST scan complete!")
            print(f"   📧 Total emails found: {total_emails}")
            print(f"   👥 Unique senders: {len(emails_by_sender)}")
            
            # Show top senders
            if emails_by_sender:
                print(f"\n📊 Top email senders:")
                sorted_senders = sorted(emails_by_sender.items(), key=lambda x: len(x[1]), reverse=True)
                for i, (sender, emails) in enumerate(sorted_senders[:10]):
                    print(f"   {i+1:2d}. {sender:<40} ({len(emails):3d} emails)")
            
            return dict(emails_by_sender)
            
        except Exception as e:
            print(f"❌ Error during PST scan: {e}")
            return {}


def scan_pst_file(pst_path: str = None) -> Dict[str, List[Dict]]:
    """
    Convenience function to scan a PST file and return emails grouped by sender.
    
    Args:
        pst_path: Path to PST file (optional, uses config default)
        
    Returns:
        Dictionary with sender emails as keys and lists of email data as values
    """
    with PSTReader(pst_path) as reader:
        return reader.scan_emails() 