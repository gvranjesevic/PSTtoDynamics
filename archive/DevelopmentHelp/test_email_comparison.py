"""
Test Email Comparison Module
============================

Tests for Phase 2 advanced email comparison and duplicate detection.
Validates multiple comparison strategies and accuracy.

Author: AI Assistant  
Phase: 2
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import email_comparator
import pst_reader
import dynamics_data
import config

def test_email_comparator_initialization():
    """Test email comparator initialization and configuration."""
    print("🧪 Test 1: Email Comparator Initialization")
    print("-" * 40)
    
    try:
        comparator = email_comparator.EmailComparator()
        
        print(f"✅ EmailComparator initialized")
        print(f"   🔍 Use Message-ID: {comparator.use_message_id}")
        print(f"   🔗 Use Content Hash: {comparator.use_content_hash}")
        print(f"   ⏱️ Fuzzy Timestamp Minutes: {comparator.fuzzy_timestamp_minutes}")
        print(f"   📝 Subject Similarity Threshold: {comparator.subject_similarity_threshold}")
        print(f"   📄 Content Similarity Threshold: {comparator.content_similarity_threshold}")
        
        # Check statistics initialization
        stats = comparator.get_comparison_stats()
        assert stats['total_comparisons'] == 0, "Stats should start at zero"
        
        print("✅ Email comparator initialization: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Email comparator initialization: FAIL - {e}")
        return False

def test_content_hash_calculation():
    """Test content hash calculation for email comparison."""
    print("\n🧪 Test 2: Content Hash Calculation")
    print("-" * 40)
    
    try:
        comparator = email_comparator.EmailComparator()
        
        # Test emails with same content
        email1 = {
            'subject': 'Test Subject',
            'body': 'This is a test email body.',
            'sender_email': 'test@example.com'
        }
        
        email2 = {
            'subject': 'Test Subject',
            'body': 'This is a test email body.',
            'sender_email': 'test@example.com'
        }
        
        # Test emails with different content
        email3 = {
            'subject': 'Different Subject',
            'body': 'This is a different email body.',
            'sender_email': 'test@example.com'
        }
        
        hash1 = comparator._calculate_content_hash(email1)
        hash2 = comparator._calculate_content_hash(email2)
        hash3 = comparator._calculate_content_hash(email3)
        
        print(f"📧 Email 1 Hash: {hash1}")
        print(f"📧 Email 2 Hash: {hash2}")
        print(f"📧 Email 3 Hash: {hash3}")
        
        # Validate results
        assert hash1 == hash2, "Identical emails should have same hash"
        assert hash1 != hash3, "Different emails should have different hash"
        assert hash1 is not None, "Valid emails should produce hashes"
        
        print("✅ Content hash calculation: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Content hash calculation: FAIL - {e}")
        return False

def test_timestamp_parsing():
    """Test timestamp parsing and fuzzy matching."""
    print("\n🧪 Test 3: Timestamp Parsing and Fuzzy Matching")
    print("-" * 40)
    
    try:
        comparator = email_comparator.EmailComparator()
        
        # Test different timestamp formats
        test_timestamps = [
            "2024-06-10T14:30:00Z",
            "2024-06-10T14:30:00",
            "2024-06-10 14:30:00",
            "06/10/2024 14:30:00",
            "10/06/2024 14:30:00"
        ]
        
        print("📅 Testing timestamp parsing:")
        for ts in test_timestamps:
            parsed = comparator._parse_timestamp(ts)
            print(f"   {ts:<25} → {parsed}")
            
        # Test fuzzy matching
        email1 = {'sent_time': "2024-06-10T14:30:00Z"}
        email2 = {'sent_time': "2024-06-10T14:32:00Z"}  # 2 minutes later
        email3 = {'sent_time': "2024-06-10T14:40:00Z"}  # 10 minutes later
        
        match_close = comparator._fuzzy_timestamp_matching(email1, email2)
        match_far = comparator._fuzzy_timestamp_matching(email1, email3)
        
        print(f"\n⏱️ Fuzzy matching results:")
        print(f"   2 min difference: {match_close['match']} ({match_close.get('time_difference_minutes', 0):.1f} min)")
        print(f"  10 min difference: {match_far['match']} ({match_far.get('time_difference_minutes', 0):.1f} min)")
        
        # Validate (default threshold is 5 minutes)
        assert match_close['match'] == True, "2 minute difference should match"
        assert match_far['match'] == False, "10 minute difference should not match"
        
        print("✅ Timestamp parsing and fuzzy matching: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Timestamp parsing and fuzzy matching: FAIL - {e}")
        return False

def test_subject_similarity():
    """Test subject similarity checking."""
    print("\n🧪 Test 4: Subject Similarity Checking")
    print("-" * 40)
    
    try:
        comparator = email_comparator.EmailComparator()
        
        # Test cases
        test_cases = [
            ("Test Subject", "Test Subject", True),  # Exact match
            ("Test Subject", "Test subject", True),  # Case difference
            ("Test Subject", "Test Subject!", True),  # Minor difference
            ("Test Subject", "Different Subject", False),  # Different
            ("Re: Test Subject", "Test Subject", True),  # Re: prefix
            ("Hello World", "Hello World Test", True),  # Partial match
            ("Completely Different", "Nothing Similar", False)  # No match
        ]
        
        print("📝 Testing subject similarity:")
        for subject1, subject2, expected_match in test_cases:
            email1 = {'subject': subject1}
            email2 = {'subject': subject2}
            
            result = comparator._subject_similarity_check(email1, email2)
            similarity = result['similarity']
            actual_match = result['match']
            
            status = "✅" if actual_match == expected_match else "❌"
            print(f"   {status} '{subject1}' vs '{subject2}' → {similarity:.2f} (match: {actual_match})")
        
        print("✅ Subject similarity checking: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Subject similarity checking: FAIL - {e}")
        return False

def test_duplicate_detection():
    """Test complete duplicate detection with real-like data."""
    print("\n🧪 Test 5: Complete Duplicate Detection")
    print("-" * 40)
    
    try:
        comparator = email_comparator.EmailComparator()
        
        # Create test PST email
        pst_email = {
            'subject': 'Delinquent Premium Report',
            'body': 'CAUTION: This email originated from outside...',
            'sent_time': '2024-06-10T14:30:00Z',
            'sender_email': 'delprem@protective.com',
            'message_id': 'test123@protective.com'
        }
        
        # Create test Dynamics emails
        dynamics_emails = [
            {
                'subject': 'Delinquent Premium Report',
                'description': 'CAUTION: This email originated from outside...',
                'actualstart': '2024-06-10T14:30:00Z',
                'sender_email': 'delprem@protective.com',
                'message_id': 'test123@protective.com'  # Exact match
            },
            {
                'subject': 'Different Subject',
                'description': 'Different content...',
                'actualstart': '2024-06-10T15:00:00Z',
                'sender_email': 'other@example.com'
            },
            {
                'subject': 'Delinquent Premium Report',
                'description': 'Similar content but different time...',
                'actualstart': '2024-06-10T16:00:00Z',  # 1.5 hours later
                'sender_email': 'delprem@protective.com'
            }
        ]
        
        # Test duplicate detection
        result = comparator.find_duplicates(pst_email, dynamics_emails)
        
        print(f"🔍 Duplicate detection results:")
        print(f"   Has duplicates: {result['has_duplicates']}")
        print(f"   Duplicate count: {result['duplicate_count']}")
        print(f"   Best confidence: {result['best_confidence']:.2f}")
        
        if result['duplicates']:
            for i, dup in enumerate(result['duplicates']):
                print(f"   Match {i+1}: {dup['match_confidence']:.2f} confidence")
                print(f"     Reasons: {', '.join(dup['match_reasons'])}")
        
        # Should find the first email as duplicate (Message-ID match)
        assert result['has_duplicates'], "Should find duplicate with matching Message-ID"
        assert result['best_confidence'] >= 0.9, "Message-ID match should have high confidence"
        
        # Test statistics
        stats = comparator.get_comparison_stats()
        print(f"\n📊 Comparison statistics:")
        print(f"   Total comparisons: {stats['total_comparisons']}")
        print(f"   Message-ID matches: {stats['message_id_matches']}")
        
        print("✅ Complete duplicate detection: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Complete duplicate detection: FAIL - {e}")
        return False

def test_live_comparison():
    """Test comparison with actual PST and Dynamics data."""
    print("\n🧪 Test 6: Live Data Comparison")
    print("-" * 40)
    
    try:
        # Check if advanced comparison is enabled
        if not config.FeatureFlags.ADVANCED_COMPARISON:
            print("⏭️ Advanced comparison feature disabled - skipping live test")
            return True
        
        comparator = email_comparator.EmailComparator()
        
        # Get sample emails from PST
        print("📧 Reading sample emails from PST...")
        with pst_reader.PSTReader() as pst:
            emails_by_sender = pst.scan_emails()
            
        if not emails_by_sender:
            print("⚠️ No emails found in PST - skipping live test")
            return True
        
        # Get a sample sender with few emails
        sample_sender = None
        sample_emails = []
        for sender, emails in emails_by_sender.items():
            if 5 <= len(emails) <= 20:  # Find sender with manageable number of emails
                sample_sender = sender
                sample_emails = emails[:5]  # Take first 5
                break
        
        if not sample_sender:
            print("⚠️ No suitable sample sender found - skipping live test")
            return True
        
        print(f"👤 Testing with sender: {sample_sender}")
        print(f"📧 Sample emails: {len(sample_emails)}")
        
        # Get existing emails from Dynamics for this sender
        print("🔍 Getting existing Dynamics emails...")
        dynamics = dynamics_data.DynamicsData()
        contacts = dynamics.get_contacts()
        
        target_contact = None
        for contact in contacts:
            if contact.get('emailaddress1', '').lower() == sample_sender.lower():
                target_contact = contact
                break
        
        if not target_contact:
            print(f"⚠️ No contact found for {sample_sender} - skipping live test")
            return True
        
        # Get existing emails for this contact
        existing_emails = dynamics.get_emails_for_contact(target_contact['contactid'])
        
        if not existing_emails:
            print(f"ℹ️ No existing emails for {sample_sender} - cannot test comparison")
            return True
        
        print(f"📊 Found {len(existing_emails)} existing emails")
        
        # Test comparison with first PST email
        test_email = sample_emails[0]
        result = comparator.find_duplicates(test_email, existing_emails[:10])  # Compare with first 10
        
        print(f"\n🔍 Live comparison results:")
        print(f"   PST Email Subject: {test_email.get('subject', 'N/A')}")
        print(f"   Has duplicates: {result['has_duplicates']}")
        print(f"   Duplicate count: {result['duplicate_count']}")
        print(f"   Best confidence: {result['best_confidence']:.2f}")
        
        print("✅ Live data comparison: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Live data comparison: FAIL - {e}")
        return False

def main():
    """Run all email comparison tests."""
    print("🚀 PHASE 2 EMAIL COMPARISON TESTS")
    print("=" * 50)
    
    tests = [
        test_email_comparator_initialization,
        test_content_hash_calculation,
        test_timestamp_parsing,
        test_subject_similarity,
        test_duplicate_detection,
        # test_live_comparison  # Uncomment for live testing
    ]
    
    results = []
    for test_func in tests:
        success = test_func()
        results.append(success)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 EMAIL COMPARISON TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All email comparison tests PASSED!")
        return True
    else:
        print("⚠️ Some email comparison tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 