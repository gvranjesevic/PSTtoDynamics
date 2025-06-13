#!/usr/bin/env python3
"""
Icon Generation Script
=====================

logger = logging.getLogger(__name__)

Generates application icons in various formats from a simple design.
Run this script to create icon files for the installer and application.
"""

import os
import logging
import sys
from pathlib import Path

def create_simple_icons():
    """Create simple text-based icons using PIL if available."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        resources_dir = Path("gui/resources")
        resources_dir.mkdir(exist_ok=True)
        
        logger.debug("🎨 Creating application icons with PIL...")
        
        sizes = [16, 32, 48, 64, 128, 256]
        
        for size in sizes:
            # Create image with transparent background
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw blue circle background
            margin = max(1, size // 16)
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(74, 144, 226, 255), outline=(35, 122, 189, 255), width=max(1, size//32))
            
            # Add text
            font_size = max(6, size // 8)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except (Exception, AttributeError, TypeError, ValueError):
                font = ImageFont.load_default()
            
            text = "PST" if size < 64 else "PST\nto\nD365"
            
            # Get text size and center it
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font, align="center")
            
            # Save PNG
            png_path = resources_dir / f"app_icon_{size}.png"
            img.save(png_path, 'PNG')
            logger.info("✅ Generated {png_path}")
        
        # Create main app icon
        main_img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(main_img)
        
        # Background
        draw.ellipse([2, 2, 126, 126], fill=(74, 144, 226, 255), outline=(35, 122, 189, 255), width=2)
        
        # Text
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except (Exception, AttributeError, TypeError, ValueError):
            font = ImageFont.load_default()
        
        text = "PST\nto\nD365"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (128 - text_width) // 2
        y = (128 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font, align="center")
        
        # Save main icon
        main_icon_path = resources_dir / "app_icon.png"
        main_img.save(main_icon_path, 'PNG')
        logger.info("✅ Generated {main_icon_path}")
        
        # Create ICO file with multiple sizes
        ico_images = []
        for size in [16, 32, 48, 128]:
            ico_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(ico_img)
            
            margin = max(1, size // 16)
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(74, 144, 226, 255), outline=(35, 122, 189, 255))
            
            font_size = max(6, size // 8)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except (Exception, AttributeError, TypeError, ValueError):
                font = ImageFont.load_default()
            
            text = "PST"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            ico_images.append(ico_img)
        
        ico_path = resources_dir / "app_icon.ico"
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in ico_images])
        logger.info("✅ Generated {ico_path}")
        
        logger.info("🎉 Icon generation complete!")
        return True
        
    except ImportError:
        logger.error("❌ PIL not available, creating basic text files...")
        return create_text_placeholder()
    except Exception as e:
        logger.error("❌ Error creating icons: {e}")
        return create_text_placeholder()

def create_text_placeholder():
    """Create placeholder text files if image libraries are not available."""
    resources_dir = Path("gui/resources")
    resources_dir.mkdir(exist_ok=True)
    
    # Create a simple text file to mark the icon location
    icon_info = resources_dir / "icon_info.txt"
    with open(icon_info, 'w') as f:
        f.write("PST to Dynamics 365 Application Icons\n")
        f.write("=====================================\n\n")
        f.write("This directory should contain:\n")
        f.write("- app_icon.png (main application icon)\n")
        f.write("- app_icon.ico (Windows installer icon)\n")
        f.write("- app_icon_*.png (various sizes)\n\n")
        f.write("Icons can be generated using PIL/Pillow or created manually.\n")
    
    logger.info("✅ Created placeholder {icon_info}")
    logger.debug("ℹ️ Install Pillow (pip install Pillow) to generate actual icons")
    return True

if __name__ == "__main__":
    success = create_simple_icons()
    sys.exit(0 if success else 1) 