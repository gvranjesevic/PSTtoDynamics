"""
Complete System Test for Phase 1
===============================

This script tests the complete email import system end-to-end.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import email_importer

def test_quick_import():
    """Test the quick import functionality."""
    print("🧪 Testing Quick Import System...")
    
    try:
        success = email_importer.quick_test()
        
        if success:
            print("✅ Quick import test successful")
            return True
        else:
            print("❌ Quick import test failed")
            return False
            
    except Exception as e:
        print(f"❌ Quick import test error: {e}")
        return False

def test_specific_sender_import():
    """Test importing for a specific sender."""
    print("\n🧪 Testing Specific Sender Import...")
    
    try:
        # Use a sender we know exists
        test_sender = "service@ringcentral.com"
        
        result = email_importer.import_emails(
            test_mode=True,
            sender=test_sender
        )
        
        if result.get('success'):
            stats = result.get('stats', {})
            print(f"✅ Specific sender import successful")
            print(f"   📧 Emails imported: {stats.get('emails_imported', 0)}")
            print(f"   ⏭️  Emails skipped: {stats.get('emails_skipped_duplicate', 0)}")
            return True
        else:
            print(f"❌ Specific sender import failed: {result.get('reason', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Specific sender import error: {e}")
        return False

def test_multi_sender_import():
    """Test importing for multiple senders in test mode."""
    print("\n🧪 Testing Multi-Sender Import (Test Mode)...")
    
    try:
        result = email_importer.import_emails(test_mode=True)
        
        if result.get('success'):
            stats = result.get('stats', {})
            print(f"✅ Multi-sender import successful")
            print(f"   👥 Senders processed: {stats.get('processed_senders', 0)}")
            print(f"   📧 Total emails found: {stats.get('total_emails_found', 0)}")
            print(f"   📧 Emails imported: {stats.get('emails_imported', 0)}")
            print(f"   ⏭️  Emails skipped (duplicates): {stats.get('emails_skipped_duplicate', 0)}")
            print(f"   👤 Emails skipped (no contact): {stats.get('emails_skipped_no_contact', 0)}")
            return True
        else:
            print(f"❌ Multi-sender import failed: {result.get('reason', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-sender import error: {e}")
        return False

def test_configuration_validation():
    """Test that configuration is properly set up."""
    print("\n🧪 Testing Configuration Validation...")
    
    try:
        # Test PST file exists
        if not os.path.exists(config.CURRENT_PST_PATH):
            print(f"❌ PST file not found: {config.CURRENT_PST_PATH}")
            return False
        
        # Test essential config values
        if not config.USERNAME or not config.PASSWORD:
            print("❌ Authentication credentials not configured")
            return False
        
        if not config.SYSTEM_USER_ID:
            print("❌ System user ID not configured")
            return False
        
        # Test feature flags
        if not config.FeatureFlags.PST_READING:
            print("❌ PST reading feature not enabled")
            return False
        
        if not config.FeatureFlags.BASIC_IMPORT:
            print("❌ Basic import feature not enabled")
            return False
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False

def main():
    """Run complete system tests."""
    print("=" * 60)
    print("🧪 COMPLETE PHASE 1 SYSTEM TEST")
    print("=" * 60)
    
    # Check configuration first
    print("📋 Checking configuration...")
    config_errors = config.validate_config()
    if config_errors:
        print("❌ Configuration errors found:")
        for error in config_errors:
            print(f"   - {error}")
        print("\n⚠️  Cannot run system tests with configuration errors")
        return False
    else:
        print("✅ Configuration is valid")
    
    tests = [
        ("Configuration Validation", test_configuration_validation),
        ("Quick Import Test", test_quick_import),
        ("Specific Sender Import", test_specific_sender_import),
        ("Multi-Sender Import", test_multi_sender_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE SYSTEM TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 1 email import system is fully functional")
        print("✅ Ready for production deployment")
        print("\n🚀 Next steps:")
        print("   - Phase 2: Contact creation and advanced comparison")
        print("   - Phase 3: Attachment handling and optimization")
        print("   - Phase 4: Enterprise UI and reporting")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed")
        print("🔧 Please address the failing tests before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 