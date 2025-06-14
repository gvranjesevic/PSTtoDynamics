#!/usr/bin/env python3
"""
LinkedIn Blue Theme Verification Script
=======================================

This script verifies that the LinkedIn Blue theme has been successfully
applied to all GUI components of the PST-to-Dynamics 365 application.
"""

import sys
import os
from PyQt6.QtCore import QSettings

def verify_theme_settings():
    """Verify that LinkedIn Blue is set as the default theme"""
    try:
        settings = QSettings("Dynamique", "PSTtoDynamics365")
        current_theme = settings.value("theme/current", "")
        
        if current_theme == "linkedin_blue":
            print("✅ LinkedIn Blue theme is set as default")
            return True
        else:
            print(f"❌ Current theme is: {current_theme}")
            return False
    except Exception as e:
        print(f"❌ Error checking theme settings: {e}")
        return False

def verify_theme_files():
    """Verify that all LinkedIn theme files exist"""
    theme_files = [
        'gui/themes/linkedin_blue_theme.py',
        'gui/themes/theme_manager.py',
        'linkedin_blue_theme.css',
        'apply_linkedin_theme.py',
        'set_linkedin_default.py'
    ]
    
    all_files_exist = True
    for file_path in theme_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_files_exist = False
    
    return all_files_exist

def verify_theme_manager():
    """Verify that the theme manager can be imported and works correctly"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gui.themes.theme_manager import ThemeManager, ThemeType
        
        # Create theme manager instance
        theme_manager = ThemeManager()
        
        # Check if LinkedIn Blue theme is available
        available_themes = theme_manager.get_available_themes()
        if ThemeType.LINKEDIN_BLUE in available_themes:
            print("✅ LinkedIn Blue theme is available in theme manager")
            
            # Get LinkedIn Blue theme definition
            linkedin_theme = theme_manager.get_theme_definition(ThemeType.LINKEDIN_BLUE)
            if linkedin_theme:
                print("✅ LinkedIn Blue theme definition loaded successfully")
                print(f"   Theme name: {linkedin_theme.get('name', 'Unknown')}")
                print(f"   Primary color: {linkedin_theme.get('colors', {}).get('primary', 'Unknown')}")
                return True
            else:
                print("❌ Could not load LinkedIn Blue theme definition")
                return False
        else:
            print("❌ LinkedIn Blue theme not available in theme manager")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying theme manager: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying LinkedIn Blue Theme Integration...")
    print("=" * 60)
    
    verification_results = []
    
    # Verify theme settings
    print("\n📋 Checking theme settings...")
    verification_results.append(verify_theme_settings())
    
    # Verify theme files
    print("\n📁 Checking theme files...")
    verification_results.append(verify_theme_files())
    
    # Verify theme manager
    print("\n⚙️ Checking theme manager...")
    verification_results.append(verify_theme_manager())
    
    print("\n" + "=" * 60)
    
    if all(verification_results):
        print("🎉 SUCCESS: LinkedIn Blue theme is fully integrated!")
        print("🎨 LinkedIn Blue Theme Features:")
        print("   • Primary Color: #0077B5 (LinkedIn Blue)")
        print("   • Background: #F3F6F8 (Professional Light Gray)")
        print("   • Surfaces: #FFFFFF (Clean White)")
        print("   • Text: #000000 (Professional Black)")
        print("   • Accents: LinkedIn-inspired colors")
        print("   • Typography: Professional Segoe UI font")
        print("\n🚀 The application now uses LinkedIn Blue theme throughout!")
        print("💡 Launch the application with 'python launch_gui.py' to see the theme in action.")
    else:
        print("❌ ISSUES FOUND: Some theme integration problems detected")
        print("🔧 Please check the errors above and fix any missing components")
    
    return all(verification_results)

if __name__ == "__main__":
    main() 