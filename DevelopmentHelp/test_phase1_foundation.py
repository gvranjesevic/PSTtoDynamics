"""
Test Script for Phase 1 Foundation
==================================

This script tests our basic configuration and authentication setup.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import auth

def test_config():
    """Test configuration validation."""
    print("🧪 Testing Configuration...")
    
    # Test config validation
    errors = config.validate_config()
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Configuration validation passed")
        return True

def test_feature_flags():
    """Test feature flags."""
    print("\n🚩 Testing Feature Flags...")
    
    # Check Phase 1 features are enabled
    phase1_features = [
        config.FeatureFlags.TIMELINE_CLEANUP,
        config.FeatureFlags.PST_READING,
        config.FeatureFlags.BASIC_IMPORT
    ]
    
    if all(phase1_features):
        print("✅ Phase 1 features properly enabled")
        return True
    else:
        print("❌ Phase 1 features not properly configured")
        return False

def test_authentication():
    """Test Dynamics 365 authentication."""
    print("\n🔐 Testing Authentication...")
    
    try:
        auth_manager = auth.get_auth()
        if auth_manager.authenticate():
            print("✅ Authentication successful")
            
            # Test connection
            if auth_manager.test_connection():
                print("✅ Connection test passed")
                return True
            else:
                print("❌ Connection test failed")
                return False
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def main():
    """Run all foundation tests."""
    print("=" * 50)
    print("🧪 PHASE 1 FOUNDATION TEST")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Feature Flags", test_feature_flags),
        ("Authentication", test_authentication)
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
        print("🎉 ALL TESTS PASSED! Phase 1 foundation is solid.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 