"""
Test Script for PST Reader Module
=================================

This script tests our PST reading functionality.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import pst_reader

def test_pst_connection():
    """Test PST file connection."""
    print("🧪 Testing PST Connection...")
    
    try:
        with pst_reader.PSTReader() as reader:
            if reader.pst_store:
                print("✅ PST connection successful")
                return True
            else:
                print("❌ PST connection failed")
                return False
    except Exception as e:
        print(f"❌ PST connection error: {e}")
        return False

def test_email_extraction():
    """Test email address extraction."""
    print("\n🧪 Testing Email Address Extraction...")
    
    test_cases = [
        ("John Doe <john@example.com>", "john@example.com"),
        ("jane@example.com", "jane@example.com"),
        ("Service <service@ringcentral.com>", "service@ringcentral.com"),
        ("No email here", None),
        ("", None),
        (None, None)
    ]
    
    passed = 0
    for input_val, expected in test_cases:
        result = pst_reader.PSTReader.extract_email_address(input_val)
        if result == expected:
            print(f"   ✅ '{input_val}' -> '{result}'")
            passed += 1
        else:
            print(f"   ❌ '{input_val}' -> '{result}' (expected '{expected}')")
    
    print(f"   📊 {passed}/{len(test_cases)} extraction tests passed")
    return passed == len(test_cases)

def test_quick_pst_scan():
    """Test a quick PST scan (first few emails only)."""
    print("\n🧪 Testing Quick PST Scan...")
    
    try:
        # Temporarily lower the batch size for testing
        original_batch = config.BATCH_SIZE
        config.BATCH_SIZE = 5  # Just scan first 5 emails
        
        emails = pst_reader.scan_pst_file()
        
        # Restore original batch size
        config.BATCH_SIZE = original_batch
        
        if emails:
            print(f"✅ PST scan successful! Found emails from {len(emails)} senders")
            
            # Show first few results
            count = 0
            for sender, email_list in emails.items():
                if count >= 3:  # Show max 3 senders
                    break
                print(f"   📧 {sender}: {len(email_list)} emails")
                count += 1
            
            return True
        else:
            print("❌ PST scan returned no emails")
            return False
            
    except Exception as e:
        print(f"❌ PST scan error: {e}")
        return False

def main():
    """Run all PST reader tests."""
    print("=" * 50)
    print("🧪 PST READER MODULE TEST")
    print("=" * 50)
    
    # Check if PST file exists first
    if not os.path.exists(config.CURRENT_PST_PATH):
        print(f"❌ PST file not found: {config.CURRENT_PST_PATH}")
        print("⚠️  Cannot test PST reader without PST file")
        return False
    
    tests = [
        ("Email Extraction", test_email_extraction),
        ("PST Connection", test_pst_connection),
        ("Quick PST Scan", test_quick_pst_scan)
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
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! PST Reader is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 