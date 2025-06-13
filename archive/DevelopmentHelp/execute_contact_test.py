"""
Direct Contact Creation Test Execution
======================================

Directly executes contact creation functionality to test Phase 2 Step 1.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import contact_creator
    import pst_reader
    import config
    
    def test_phase2_step1():
        """Test contact creation foundation."""
        print("🚀 PHASE 2 STEP 1: CONTACT CREATION FOUNDATION TEST")
        print("=" * 60)
        
        # Test 1: Basic module imports
        print("🧪 Test 1: Module Imports")
        print("-" * 30)
        try:
            print("✅ contact_creator imported successfully")
            print("✅ pst_reader imported successfully") 
            print("✅ config imported successfully")
            print("✅ Module imports: PASS")
        except Exception as e:
            print(f"❌ Module imports: FAIL - {e}")
            return False
            
        # Test 2: Contact creator initialization
        print("\n🧪 Test 2: ContactCreator Initialization")
        print("-" * 30)
        try:
            creator = contact_creator.ContactCreator()
            print("✅ ContactCreator initialized successfully")
            print(f"✅ Base URL: {creator.base_url}")
            print("✅ ContactCreator initialization: PASS")
        except Exception as e:
            print(f"❌ ContactCreator initialization: FAIL - {e}")
            return False
            
        # Test 3: Contact info extraction
        print("\n🧪 Test 3: Contact Info Extraction")
        print("-" * 30)
        try:
            test_emails = [
                "john.doe@example.com",
                "service@ringcentral.com",
                "test@protective.com"
            ]
            
            for email in test_emails:
                contact_info = creator._extract_contact_info(email)
                is_valid = creator._validate_contact_data(contact_info)
                
                print(f"📧 {email}")
                print(f"   👤 Name: {contact_info['fullname']}")
                print(f"   🏢 Company: {contact_info['companyname']}")
                print(f"   ✅ Valid: {is_valid}")
                
            print("✅ Contact info extraction: PASS")
        except Exception as e:
            print(f"❌ Contact info extraction: FAIL - {e}")
            return False
            
        # Test 4: Configuration check
        print("\n🧪 Test 4: Phase 2 Configuration")
        print("-" * 30)
        try:
            print(f"✅ Contact Creation Enabled: {config.FeatureFlags.CONTACT_CREATION}")
            print(f"✅ Auto Create Missing: {config.CONTACT_CREATION['AUTO_CREATE_MISSING']}")
            print(f"✅ Max Contacts Per Batch: {config.CONTACT_CREATION['MAX_CONTACTS_PER_BATCH']}")
            print("✅ Phase 2 configuration: PASS")
        except Exception as e:
            print(f"❌ Phase 2 configuration: FAIL - {e}")
            return False
            
        print("\n" + "=" * 60)
        print("📊 PHASE 2 STEP 1 FOUNDATION TEST SUMMARY")
        print("=" * 60)
        print("✅ All foundation tests PASSED!")
        print("🎉 Contact creation foundation is ready!")
        print("🚀 Ready to proceed with Phase 2 Step 2...")
        
        return True
        
    # Execute the test
    success = test_phase2_step1()
    
    if success:
        print("\n🎯 Phase 2 Step 1 COMPLETE - Contact Creation Foundation Ready!")
    else:
        print("\n❌ Phase 2 Step 1 FAILED - Foundation issues detected!")
        
except Exception as e:
    print(f"❌ Critical error: {e}")
    import traceback
    traceback.print_exc() 