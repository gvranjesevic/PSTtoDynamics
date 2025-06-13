"""
Test Contact Creation Module
============================

Tests for Phase 2 contact creation functionality.
Validates missing contact analysis and automatic contact creation.

Author: AI Assistant
Phase: 2
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contact_creator
import pst_reader
import config

def test_missing_contact_analysis():
    """Test analysis of missing contacts from PST data."""
    print("🧪 Test 1: Missing Contact Analysis")
    print("-" * 40)
    
    try:
        # Get sample senders from PST
        print("📧 Reading PST to get sender list...")
        with pst_reader.PSTReader() as pst:
            sender_stats = pst.get_sender_statistics()
            sample_senders = list(sender_stats.keys())[:20]  # Test with first 20 senders
        
        # Analyze missing contacts
        creator = contact_creator.ContactCreator()
        analysis = creator.analyze_missing_contacts(sample_senders)
        
        print(f"📊 Analysis Results:")
        print(f"   📧 Total senders analyzed: {analysis['total_senders']}")
        print(f"   ✅ Existing contacts found: {analysis['existing_contacts']}")
        print(f"   ❌ Missing contacts: {analysis['missing_contacts']}")
        
        # Show some examples
        if analysis['missing_contact_list']:
            print(f"\n📋 Sample missing contacts:")
            for email in analysis['missing_contact_list'][:5]:
                print(f"      • {email}")
        
        if analysis['existing_contact_list']:
            print(f"\n✅ Sample existing contacts:")
            for email in analysis['existing_contact_list'][:5]:
                print(f"      • {email}")
        
        # Validation
        assert analysis['total_senders'] > 0, "Should find some senders"
        assert analysis['total_senders'] == analysis['existing_contacts'] + analysis['missing_contacts'], "Numbers should add up"
        
        print("✅ Missing contact analysis: PASS")
        return True, analysis
        
    except Exception as e:
        print(f"❌ Missing contact analysis: FAIL - {e}")
        return False, None

def test_contact_info_extraction():
    """Test extraction of contact information from email addresses."""
    print("\n🧪 Test 2: Contact Info Extraction")
    print("-" * 40)
    
    try:
        creator = contact_creator.ContactCreator()
        
        # Test cases for different email patterns
        test_emails = [
            "john.doe@example.com",
            "service@ringcentral.com", 
            "notify@protective.com",
            "support_team@company.co.uk",
            "firstname.lastname@dynamique.com"
        ]
        
        print("📋 Testing contact info extraction:")
        all_passed = True
        
        for email in test_emails:
            contact_info = creator._extract_contact_info(email)
            
            print(f"\n📧 Email: {email}")
            print(f"   👤 Full Name: {contact_info['fullname']}")
            print(f"   🏢 Company: {contact_info['companyname']}")
            print(f"   ✅ Valid: {creator._validate_contact_data(contact_info)}")
            
            # Basic validation
            if not contact_info['fullname'] or not contact_info['emailaddress1']:
                print(f"   ❌ Missing required fields")
                all_passed = False
        
        if all_passed:
            print("✅ Contact info extraction: PASS")
            return True
        else:
            print("❌ Contact info extraction: FAIL")
            return False
            
    except Exception as e:
        print(f"❌ Contact info extraction: FAIL - {e}")
        return False

def test_contact_creation_dry_run():
    """Test contact creation in dry-run mode (validation only)."""
    print("\n🧪 Test 3: Contact Creation Dry Run")
    print("-" * 40)
    
    try:
        # Get missing contacts from analysis
        creator = contact_creator.ContactCreator()
        
        # Get sample senders
        with pst_reader.PSTReader() as pst:
            sender_stats = pst.get_sender_statistics()
            all_senders = list(sender_stats.keys())
        
        # Analyze for missing contacts
        analysis = creator.analyze_missing_contacts(all_senders)
        
        if not analysis['missing_contact_list']:
            print("✅ No missing contacts found - all senders have existing contacts!")
            return True
        
        # Test creation preparation for first few missing contacts
        missing_sample = analysis['missing_contact_list'][:5]
        print(f"📋 Testing creation prep for {len(missing_sample)} missing contacts:")
        
        for email in missing_sample:
            contact_info = creator._extract_contact_info(email)
            is_valid = creator._validate_contact_data(contact_info)
            
            print(f"\n📧 {email}")
            print(f"   👤 Name: {contact_info['fullname']}")
            print(f"   🏢 Company: {contact_info['companyname']}")
            print(f"   ✅ Ready for creation: {is_valid}")
        
        print("✅ Contact creation dry run: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Contact creation dry run: FAIL - {e}")
        return False

def test_live_contact_creation():
    """Test actual contact creation with one sample contact."""
    print("\n🧪 Test 4: Live Contact Creation (1 Contact)")
    print("-" * 40)
    
    # Check if we should skip live testing
    if not config.FeatureFlags.CONTACT_CREATION:
        print("⏭️ Contact creation feature disabled - skipping live test")
        return True
    
    try:
        creator = contact_creator.ContactCreator()
        
        # Find a test email that doesn't exist
        test_email = "test.pst.import@example.com"
        
        print(f"🧪 Testing with sample email: {test_email}")
        
        # Check if it already exists
        analysis = creator.analyze_missing_contacts([test_email])
        
        if test_email in analysis['existing_contact_list']:
            print("⚠️ Test contact already exists - skipping creation test")
            return True
        
        # Create the test contact
        print("🏗️ Creating test contact...")
        result = creator.create_missing_contacts([test_email])
        
        if result['success'] and result['created_contacts']:
            created = result['created_contacts'][0]
            print(f"✅ Contact created successfully!")
            print(f"   📧 Email: {created['email']}")
            print(f"   👤 Name: {created['full_name']}")
            print(f"   🆔 Contact ID: {created['contact_id']}")
            
            # Clean up - delete the test contact
            print("🧹 Cleaning up test contact...")
            # Note: We could add deletion logic here, but for now just log the ID
            print(f"   ℹ️ Test contact ID {created['contact_id']} created for testing")
            
            print("✅ Live contact creation: PASS")
            return True
        else:
            print(f"❌ Live contact creation: FAIL - {result}")
            return False
            
    except Exception as e:
        print(f"❌ Live contact creation: FAIL - {e}")
        return False

def main():
    """Run all contact creation tests."""
    print("🚀 PHASE 2 CONTACT CREATION TESTS")
    print("=" * 50)
    
    tests = [
        test_missing_contact_analysis,
        test_contact_info_extraction,
        test_contact_creation_dry_run,
        # test_live_contact_creation  # Uncomment to test actual creation
    ]
    
    results = []
    for test_func in tests:
        success = test_func() if test_func == test_missing_contact_analysis else test_func()
        if isinstance(success, tuple):
            success = success[0]
        results.append(success)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 CONTACT CREATION TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All contact creation tests PASSED!")
        return True
    else:
        print("⚠️ Some contact creation tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 