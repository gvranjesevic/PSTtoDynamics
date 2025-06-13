"""
Simple Test Runner
==================

logger = logging.getLogger(__name__)

Runs our contact creation test to validate Phase 2 functionality.
"""

import sys
import logging
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our test module
import DevelopmentHelp.test_contact_creation as test_contact_creation

if __name__ == "__main__":
    logger.info("🚀 Running Contact Creation Test...")
    logger.debug("-" * 50)
    
    # Run the main test function
    success = test_contact_creation.main()
    
    if success:
        logger.debug("\n✅ Contact creation tests completed successfully!")
    else:
        logger.debug("\n❌ Contact creation tests failed!")
    
    logger.debug("\n🎯 Phase 2 Step 1 Foundation Testing Complete") 