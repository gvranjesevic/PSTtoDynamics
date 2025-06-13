"""
Simple Test Runner
==================

Runs our contact creation test to validate Phase 2 functionality.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our test module
import DevelopmentHelp.test_contact_creation as test_contact_creation

if __name__ == "__main__":
    print("🚀 Running Contact Creation Test...")
    print("-" * 50)
    
    # Run the main test function
    success = test_contact_creation.main()
    
    if success:
        print("\n✅ Contact creation tests completed successfully!")
    else:
        print("\n❌ Contact creation tests failed!")
    
    print("\n🎯 Phase 2 Step 1 Foundation Testing Complete") 