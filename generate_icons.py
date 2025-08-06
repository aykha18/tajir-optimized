#!/usr/bin/env python3
"""
Generate PWA icons for Tajir POS
This script creates placeholder icons for the PWA manifest
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the given size"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#3b82f6')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        # Use a larger font for bigger icons
        font_size = max(12, size // 3)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw the letter "T" in white
    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all required icons"""
    # Create icons directory if it doesn't exist
    os.makedirs('static/icons', exist_ok=True)
    
    # Icon sizes required by the manifest
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = f'static/icons/icon-{size}.png'
        create_icon(size, filename)
    
    print("All icons generated successfully!")

if __name__ == "__main__":
    main() 