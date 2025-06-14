#!/usr/bin/env python3
"""
Set LinkedIn Blue as Default Theme
=================================

Simple script to set LinkedIn Blue as the default theme
by directly modifying the application settings.
"""

import sys
import os
from PyQt6.QtCore import QSettings

def set_linkedin_blue_default():
    """Set LinkedIn Blue as the default theme in application settings"""
    try:
        # Create QSettings instance (same as used by ThemeManager)
        settings = QSettings("Dynamique", "PSTtoDynamics365")
        
        # Set LinkedIn Blue as the current theme
        settings.setValue("theme/current", "linkedin_blue")
        
        # Sync settings to ensure they're saved
        settings.sync()
        
        print("✅ LinkedIn Blue theme has been set as the default!")
        print("🎨 Theme colors:")
        print("   • Primary: #0077B5 (LinkedIn Blue)")
        print("   • Background: #F3F6F8 (Light Gray)")
        print("   • Surface: #FFFFFF (White)")
        print("   • Text: #000000 (Black)")
        print("   • Success: #057642 (Green)")
        print("   • Warning: #F5C75D (Gold)")
        print("   • Error: #CC1016 (Red)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting default theme: {e}")
        return False

def create_theme_preview():
    """Create a visual preview of the LinkedIn Blue theme"""
    preview = """
╔══════════════════════════════════════════════════════════════╗
║                    LinkedIn Blue Theme Preview               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎨 LinkedIn Blue Theme Features:                            ║
║                                                              ║
║  • Professional LinkedIn-inspired design                    ║
║  • Signature blue (#0077B5) for primary elements           ║
║  • Clean white surfaces with subtle gray backgrounds        ║
║  • Optimized for business applications                      ║
║  • Excellent readability and accessibility                  ║
║                                                              ║
║  📊 Color Palette:                                          ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ Primary:    #0077B5  ████████████████████████████████   │ ║
║  │ Secondary:  #005885  ████████████████████████████████   │ ║
║  │ Background: #F3F6F8  ████████████████████████████████   │ ║
║  │ Surface:    #FFFFFF  ████████████████████████████████   │ ║
║  │ Success:    #057642  ████████████████████████████████   │ ║
║  │ Warning:    #F5C75D  ████████████████████████████████   │ ║
║  │ Error:      #CC1016  ████████████████████████████████   │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                              ║
║  🚀 Next time you launch the application, you'll see:       ║
║  • LinkedIn blue buttons and highlights                     ║
║  • Professional light gray background                       ║
║  • Clean white panels and surfaces                          ║
║  • Consistent LinkedIn-style branding                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(preview)

def main():
    """Main function"""
    print("🎨 Setting LinkedIn Blue as Default Theme...")
    print()
    
    if set_linkedin_blue_default():
        print()
        create_theme_preview()
        print()
        print("✅ SUCCESS: LinkedIn Blue theme is now the default!")
        print("🚀 Launch the application to see the new theme in action.")
    else:
        print("❌ FAILED: Could not set LinkedIn Blue as default theme.")

if __name__ == "__main__":
    main() 