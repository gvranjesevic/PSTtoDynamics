#!/usr/bin/env python3
"""
Quick PST Test - Just scan and show results
"""

import win32com.client
import re
from collections import defaultdict
import os

# Configuration
PST_FILE_PATH = r"PST\gvranjesevic@dynamique.com.001.pst"
TEST_EMAIL_ADDRESS = "service@ringcentral.com"

def extract_email_address(email_string):
    """Extracts email address from various formats."""
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

def quick_scan_pst():
    """Quick scan of PST file to show what's available."""
    print(f"Quick PST Scan: {PST_FILE_PATH}")
    
    if not os.path.exists(PST_FILE_PATH):
        print(f"PST file not found: {PST_FILE_PATH}")
        return
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        print("Opening PST file...")
        
        # Find PST store
        pst_store = None
        for store in namespace.Stores:
            if PST_FILE_PATH.lower() in str(store.FilePath).lower():
                pst_store = store
                break
        
        if not pst_store:
            namespace.AddStore(PST_FILE_PATH)
            for store in namespace.Stores:
                if PST_FILE_PATH.lower() in str(store.FilePath).lower():
                    pst_store = store
                    break
        
        if not pst_store:
            print("Could not access PST store")
            return
        
        root_folder = pst_store.GetRootFolder()
        print(f"Root folder: {root_folder.Name}")
        
        emails_by_sender = defaultdict(list)
        total_emails = 0
        
        def scan_folder(folder, depth=0):
            nonlocal total_emails
            indent = "  " * depth
            
            try:
                print(f"{indent}Folder: {folder.Name}")
                items = folder.Items
                
                folder_emails = 0
                for item in items:
                    try:
                        if hasattr(item, 'Class') and item.Class == 43:  # Mail item
                            sender_email = None
                            
                            if hasattr(item, 'SenderEmailAddress') and item.SenderEmailAddress:
                                sender_email = extract_email_address(item.SenderEmailAddress)
                            
                            if sender_email:
                                emails_by_sender[sender_email].append({
                                    'subject': item.Subject or 'No Subject',
                                    'folder': folder.Name
                                })
                                total_emails += 1
                                folder_emails += 1
                    except:
                        pass
                
                print(f"{indent}  -> {folder_emails} emails")
                
                # Scan subfolders
                try:
                    for subfolder in folder.Folders:
                        scan_folder(subfolder, depth + 1)
                except:
                    pass
                    
            except Exception as e:
                print(f"{indent}Error: {e}")
        
        scan_folder(root_folder)
        
        print(f"\nScan Results:")
        print(f"  Total emails: {total_emails}")
        print(f"  Unique senders: {len(emails_by_sender)}")
        
        # Show top senders
        print(f"\nTop senders:")
        sorted_senders = sorted(emails_by_sender.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (sender, emails) in enumerate(sorted_senders[:15]):
            print(f"  {i+1:2d}. {sender:<40} ({len(emails):3d} emails)")
        
        # Check for our test email address
        if TEST_EMAIL_ADDRESS in emails_by_sender:
            test_emails = emails_by_sender[TEST_EMAIL_ADDRESS]
            print(f"\nTest email address ({TEST_EMAIL_ADDRESS}) found!")
            print(f"  Total emails: {len(test_emails)}")
            print(f"  Sample subjects:")
            for i, email in enumerate(test_emails[:5]):
                print(f"    {i+1}. {email['subject'][:60]}")
        else:
            print(f"\nTest email address ({TEST_EMAIL_ADDRESS}) NOT found in PST")
            print("Available similar addresses:")
            for sender in sorted_senders[:20]:
                if 'ring' in sender[0].lower():
                    print(f"  - {sender[0]} ({sender[1]} emails)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_scan_pst() 