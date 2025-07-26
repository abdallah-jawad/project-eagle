#!/usr/bin/env python3
"""
Script to run the interactive section drawing tool
"""

import os
import sys

def main():
    """Run the section drawing tool"""
    try:
        from backend.section_drawer import create_section_drawer
    except ImportError as e:
        print(f"❌ Error importing section drawer: {e}")
        print("\n📦 Required packages:")
        print("- matplotlib")
        print("- numpy")
        print("- Pillow (already installed)")
        print("\nInstall with: pip install matplotlib numpy")
        return 1
    
    # Default image path
    image_path = "config/images/planogram_demo.jpeg"
    
    # Check if custom path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    # Verify image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} [image_path]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} config/images/my_planogram.jpg")
        return 1
    
    print("🚀 Starting Interactive Section Drawing Tool...")
    print(f"📷 Image: {image_path}")
    print()
    
    try:
        # Create and show the drawing tool
        drawer = create_section_drawer(image_path)
        
        # Show final results
        sections = drawer.get_sections()
        if sections:
            print(f"\n🎉 Successfully created {len(sections)} sections!")
            print("Configuration saved automatically.")
        else:
            print("\n💭 No sections were saved.")
            
    except Exception as e:
        print(f"❌ Error running section drawer: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 