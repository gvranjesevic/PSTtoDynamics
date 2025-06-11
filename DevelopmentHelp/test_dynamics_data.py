"""
Test Script for Dynamics 365 Data Module
========================================

This script tests our Dynamics 365 data access functionality.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dynamics_data
from datetime import datetime

def test_contact_retrieval():
    """Test contact retrieval."""
    print("🧪 Testing Contact Retrieval...")
    
    try:
        data_manager = dynamics_data.get_dynamics_data()
        
        # Test getting all contacts (limited)
        contacts = data_manager.get_contacts()
        
        if contacts:
            print(f"✅ Retrieved {len(contacts)} contacts")
            
            # Show first few contacts
            for i, contact in enumerate(contacts[:3]):
                name = contact.get('fullname', 'No Name')
                email = contact.get('emailaddress1', 'No Email')
                print(f"   📧 {name}: {email}")
                
            return True
        else:
            print("❌ No contacts retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Contact retrieval error: {e}")
        return False

def test_specific_contact_lookup():
    """Test looking up a specific contact."""
    print("\n🧪 Testing Specific Contact Lookup...")
    
    try:
        data_manager = dynamics_data.get_dynamics_data()
        
        # Look for a specific contact (using service@ringcentral.com since we know it exists)
        test_email = "service@ringcentral.com"
        contact = data_manager.get_contact_by_email(test_email)
        
        if contact:
            print(f"✅ Found contact for {test_email}")
            print(f"   📧 Name: {contact.get('fullname', 'Unknown')}")
            print(f"   🆔 ID: {contact.get('contactid', 'Unknown')}")
            return True
        else:
            print(f"❌ No contact found for {test_email}")
            return False
            
    except Exception as e:
        print(f"❌ Contact lookup error: {e}")
        return False

def test_email_retrieval():
    """Test retrieving emails for a contact."""
    print("\n🧪 Testing Email Retrieval...")
    
    try:
        data_manager = dynamics_data.get_dynamics_data()
        
        # First get a contact
        test_email = "service@ringcentral.com"
        contact = data_manager.get_contact_by_email(test_email)
        
        if not contact:
            print(f"❌ Cannot test email retrieval - no contact found for {test_email}")
            return False
        
        contact_id = contact['contactid']
        emails = data_manager.get_emails_for_contact(contact_id)
        
        if emails:
            print(f"✅ Retrieved {len(emails)} emails for contact")
            
            # Show first few emails
            for i, email in enumerate(emails[:3]):
                subject = email.get('subject', 'No Subject')
                status = "Open" if email.get('statecode') == 0 else "Closed"
                print(f"   📧 {subject[:50]}... [{status}]")
                
            return True
        else:
            print(f"✅ No emails found for contact (this is okay)")
            return True
            
    except Exception as e:
        print(f"❌ Email retrieval error: {e}")
        return False

def test_duplicate_detection():
    """Test duplicate email detection."""
    print("\n🧪 Testing Duplicate Detection...")
    
    try:
        data_manager = dynamics_data.get_dynamics_data()
        
        # Create test emails
        email1 = {
            'subject': 'Test Email Subject',
            'sent_time': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        email2 = {
            'subject': 'Test Email Subject',
            'sent_time': datetime(2024, 1, 1, 12, 30, 0)  # 30 minutes later
        }
        
        email3 = {
            'subject': 'Different Subject',
            'sent_time': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        existing_emails = [
            {
                'subject': 'Test Email Subject',
                'createdon': '2024-01-01T12:00:00Z'
            }
        ]
        
        # Test duplicate detection
        is_dup1 = data_manager.is_email_duplicate(email1, existing_emails)
        is_dup2 = data_manager.is_email_duplicate(email2, existing_emails)
        is_dup3 = data_manager.is_email_duplicate(email3, existing_emails)
        
        print(f"   📧 Same subject, same time: {'Duplicate' if is_dup1 else 'Not duplicate'}")
        print(f"   📧 Same subject, 30 min later: {'Duplicate' if is_dup2 else 'Not duplicate'}")
        print(f"   📧 Different subject, same time: {'Duplicate' if is_dup3 else 'Not duplicate'}")
        
        # Expected: email1 is duplicate, email2 might be depending on threshold, email3 is not
        if is_dup1 and not is_dup3:
            print("✅ Duplicate detection working correctly")
            return True
        else:
            print("❌ Duplicate detection not working as expected")
            return False
            
    except Exception as e:
        print(f"❌ Duplicate detection error: {e}")
        return False

def test_timeline_status():
    """Test timeline status retrieval."""
    print("\n🧪 Testing Timeline Status...")
    
    try:
        data_manager = dynamics_data.get_dynamics_data()
        
        # Get a contact to test with
        test_email = "service@ringcentral.com"
        contact = data_manager.get_contact_by_email(test_email)
        
        if not contact:
            print(f"❌ Cannot test timeline status - no contact found for {test_email}")
            return False
        
        contact_id = contact['contactid']
        status = data_manager.get_timeline_status(contact_id)
        
        print(f"✅ Timeline status retrieved:")
        print(f"   📧 Total emails: {status['total_emails']}")
        print(f"   📖 Open emails: {status['open_emails']}")
        print(f"   📕 Closed emails: {status['closed_emails']}")
        
        return True
            
    except Exception as e:
        print(f"❌ Timeline status error: {e}")
        return False

def main():
    """Run all Dynamics data tests."""
    print("=" * 50)
    print("🧪 DYNAMICS 365 DATA MODULE TEST")
    print("=" * 50)
    
    tests = [
        ("Contact Retrieval", test_contact_retrieval),
        ("Specific Contact Lookup", test_specific_contact_lookup),
        ("Email Retrieval", test_email_retrieval),
        ("Duplicate Detection", test_duplicate_detection),
        ("Timeline Status", test_timeline_status)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Dynamics 365 data access is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 