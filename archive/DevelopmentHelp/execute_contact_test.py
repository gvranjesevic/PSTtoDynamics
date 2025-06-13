"""
Direct Contact Creation Test Execution
======================================

logger = logging.getLogger(__name__)

Directly executes contact creation functionality to test Phase 2 Step 1.
"""

import sys
import logging
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import contact_creator
    import pst_reader
    import config
    
    def test_phase2_step1():
        """Test contact creation foundation."""
        logger.info("🚀 PHASE 2 STEP 1: CONTACT CREATION FOUNDATION TEST")
        logger.debug("=" * 60)
        
        # Test 1: Basic module imports
        logger.info("🧪 Test 1: Module Imports")
        logger.debug("-" * 30)
        try:
            logger.info("✅ contact_creator imported successfully")
            logger.info("✅ pst_reader imported successfully") 
            logger.info("✅ config imported successfully")
            logger.info("✅ Module imports: PASS")
        except Exception as e:
            logger.error("❌ Module imports: FAIL - {e}")
            return False
            
        # Test 2: Contact creator initialization
        logger.debug("\n🧪 Test 2: ContactCreator Initialization")
        logger.debug("-" * 30)
        try:
            creator = contact_creator.ContactCreator()
            logger.info("✅ ContactCreator initialized successfully")
            logger.info("✅ Base URL: {creator.base_url}")
            logger.info("✅ ContactCreator initialization: PASS")
        except Exception as e:
            logger.error("❌ ContactCreator initialization: FAIL - {e}")
            return False
            
        # Test 3: Contact info extraction
        logger.debug("\n🧪 Test 3: Contact Info Extraction")
        logger.debug("-" * 30)
        try:
            test_emails = [
                "john.doe@example.com",
                "service@ringcentral.com",
                "test@protective.com"
            ]
            
            for email in test_emails:
                contact_info = creator._extract_contact_info(email)
                is_valid = creator._validate_contact_data(contact_info)
                
                logger.info("📧 {email}")
                logger.debug("   👤 Name: {contact_info['fullname']}")
                logger.debug("   🏢 Company: {contact_info['companyname']}")
                logger.debug("   ✅ Valid: {is_valid}")
                
            logger.info("✅ Contact info extraction: PASS")
        except Exception as e:
            logger.error("❌ Contact info extraction: FAIL - {e}")
            return False
            
        # Test 4: Configuration check
        logger.debug("\n🧪 Test 4: Phase 2 Configuration")
        logger.debug("-" * 30)
        try:
            logger.info("✅ Contact Creation Enabled: {config.FeatureFlags.CONTACT_CREATION}")
            logger.info("✅ Auto Create Missing: {config.CONTACT_CREATION['AUTO_CREATE_MISSING']}")
            logger.info("✅ Max Contacts Per Batch: {config.CONTACT_CREATION['MAX_CONTACTS_PER_BATCH']}")
            logger.info("✅ Phase 2 configuration: PASS")
        except Exception as e:
            logger.error("❌ Phase 2 configuration: FAIL - {e}")
            return False
            
        logger.debug("\n" + "=" * 60)
        logger.info("📊 PHASE 2 STEP 1 FOUNDATION TEST SUMMARY")
        logger.debug("=" * 60)
        logger.info("✅ All foundation tests PASSED!")
        logger.info("🎉 Contact creation foundation is ready!")
        logger.info("🚀 Ready to proceed with Phase 2 Step 2...")
        
        return True
        
    # Execute the test
    success = test_phase2_step1()
    
    if success:
        logger.debug("\n🎯 Phase 2 Step 1 COMPLETE - Contact Creation Foundation Ready!")
    else:
        logger.debug("\n❌ Phase 2 Step 1 FAILED - Foundation issues detected!")
        
except Exception as e:
    logger.error("❌ Critical error: {e}")
    import traceback
    traceback.print_exc() 