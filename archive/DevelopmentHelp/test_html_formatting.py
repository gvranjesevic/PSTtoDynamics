"""
Test HTML Formatting Fix
========================

Quick test to verify email body HTML formatting is working.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import email_importer

def test_html_formatting():
    """Test that we can import one email with proper HTML formatting."""
    print("🧪 Testing HTML Formatting Fix")
    print("-" * 40)
    
    try:
        # Import just one email from delprem@protective.com to test formatting
        result = email_importer.import_emails(
            test_mode=True,
            sender="delprem@protective.com"
        )
        
        if result.get('success'):
            stats = result.get('stats', {})
            print(f"✅ Test successful!")
            print(f"   📧 Emails imported: {stats.get('emails_imported', 0)}")
            print("\n📋 Check the latest email in Dynamics 365 for proper line breaks!")
            print("   The email body should now show proper formatting instead of underscores.")
            return True
        else:
            print(f"❌ Test failed: {result.get('reason', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_html_formatting()
    if success:
        print("\n🎉 HTML formatting test complete!")
        print("📸 Take a screenshot of the latest email to verify formatting!")
    else:
        print("\n❌ HTML formatting test failed!") 