import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import json
import os
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np

class SectionDrawer:
    """
    Interactive utility for drawing planogram section boundaries on images
    """
    
    def __init__(self, image_path: str, target_size: tuple = (1080, 1440)):
        """
        Initialize the section drawer
        
        Args:
            image_path: Path to the planogram image
            target_size: Target size to normalize image to (width, height)
        """
        self.image_path = image_path
        self.target_size = target_size
        self.sections = []
        self.current_section = None
        self.drawing = False
        self.start_point = None
        
        # Load and resize image
        self.image = self._load_and_resize_image()
        
        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 16))
        self.ax.imshow(self.image)
        self.ax.set_title("Draw Section Boundaries\nClick and drag to draw rectangles")
        
        # Store rectangles for visual feedback
        self.rectangles = []
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('button_press_event', self._on_press)
        self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)
        
        # Add control buttons
        self._setup_buttons()
        
        print("\n🎯 Section Drawing Tool")
        print("=" * 40)
        print("Instructions:")
        print("1. Click and drag to draw section boundaries")
        print("2. Each rectangle will be numbered automatically")
        print("3. Click 'Finish Drawing' when done")
        print("4. Click 'Save Config' to export coordinates")
        print("5. Close window to exit")
    
    def _load_and_resize_image(self) -> np.ndarray:
        """Load and resize image to target size"""
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image not found: {self.image_path}")
        
        image = Image.open(self.image_path)
        
        # Resize with aspect ratio preservation
        target_width, target_height = self.target_size
        original_width, original_height = image.size
        
        # Calculate scaling factor
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = min(scale_w, scale_h)
        
        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create final image with exact target size
        final_image = Image.new('RGB', self.target_size, (255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        final_image.paste(resized, (paste_x, paste_y))
        
        return np.array(final_image)
    
    def _setup_buttons(self):
        """Setup control buttons"""
        # Finish button
        ax_finish = plt.axes([0.02, 0.95, 0.12, 0.04])
        self.btn_finish = Button(ax_finish, 'Finish Drawing')
        self.btn_finish.on_clicked(self._finish_drawing)
        
        # Save config button
        ax_save = plt.axes([0.15, 0.95, 0.12, 0.04])
        self.btn_save = Button(ax_save, 'Save Config')
        self.btn_save.on_clicked(self._save_config)
        
        # Clear all button
        ax_clear = plt.axes([0.28, 0.95, 0.12, 0.04])
        self.btn_clear = Button(ax_clear, 'Clear All')
        self.btn_clear.on_clicked(self._clear_all)
        
        # Undo last button
        ax_undo = plt.axes([0.41, 0.95, 0.12, 0.04])
        self.btn_undo = Button(ax_undo, 'Undo Last')
        self.btn_undo.on_clicked(self._undo_last)
    
    def _on_press(self, event):
        """Handle mouse press events"""
        if event.inaxes != self.ax or event.button != 1:  # Only left click
            return
        
        self.drawing = True
        self.start_point = (event.xdata, event.ydata)
        
        # Create new rectangle
        self.current_section = patches.Rectangle(
            self.start_point, 0, 0, 
            linewidth=2, 
            edgecolor='red', 
            facecolor='red',
            alpha=0.3
        )
        self.ax.add_patch(self.current_section)
        self.fig.canvas.draw()
    
    def _on_motion(self, event):
        """Handle mouse motion events"""
        if not self.drawing or event.inaxes != self.ax or self.start_point is None or self.current_section is None:
            return
        
        # Update rectangle size
        width = event.xdata - self.start_point[0]
        height = event.ydata - self.start_point[1]
        
        self.current_section.set_width(width)
        self.current_section.set_height(height)
        self.fig.canvas.draw_idle()
    
    def _on_release(self, event):
        """Handle mouse release events"""
        if not self.drawing or event.inaxes != self.ax:
            return
        
        self.drawing = False
        
        if self.start_point and self.current_section:
            # Calculate final coordinates
            x1, y1 = self.start_point
            x2, y2 = event.xdata, event.ydata
            
            # Ensure x1 < x2 and y1 < y2
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Only add if rectangle has meaningful size
            if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                section_id = len(self.sections) + 1
                
                section_data = {
                    'section_id': f'SECTION_{section_id:02d}',
                    'name': f'Section {section_id}',
                    'coordinates': {
                        'x1': int(x1),
                        'y1': int(y1), 
                        'x2': int(x2),
                        'y2': int(y2)
                    },
                    'width': int(x2 - x1),
                    'height': int(y2 - y1)
                }
                
                self.sections.append(section_data)
                self.rectangles.append(self.current_section)
                
                # Add section label
                text_x = x1 + 5
                text_y = y1 + 15
                self.ax.text(
                    text_x, text_y, 
                    f"#{section_id}", 
                    color='white',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.7)
                )
                
                print(f"✅ Section {section_id}: ({int(x1)}, {int(y1)}) -> ({int(x2)}, {int(y2)})")
                
            else:
                # Remove rectangle if too small
                self.current_section.remove()
        
        self.current_section = None
        self.start_point = None
        self.fig.canvas.draw()
    
    def _finish_drawing(self, event):
        """Finish drawing and display results"""
        if not self.sections:
            print("❌ No sections drawn yet!")
            return
        
        print(f"\n🎯 Drawing Complete! {len(self.sections)} sections created:")
        print("=" * 50)
        
        for i, section in enumerate(self.sections, 1):
            coords = section['coordinates']
            print(f"Section {i}: {section['section_id']}")
            print(f"  Position: ({coords['x1']}, {coords['y1']}) -> ({coords['x2']}, {coords['y2']})")
            print(f"  Size: {section['width']} × {section['height']} pixels")
            print()
    
    def _save_config(self, event):
        """Save configuration to JSON file"""
        if not self.sections:
            print("❌ No sections to save!")
            return
        
        # Get configuration details from user
        store_name = input("Enter store name: ") or "Custom Store Layout"
        store_id = input("Enter store ID: ") or "STORE_CUSTOM"
        
        config_data = {
            "metadata": {
                "name": store_name,
                "store_id": store_id,
                "created_date": "2024-01-01",
                "version": "1.0",
                "description": f"Custom planogram with {len(self.sections)} sections"
            },
            "planogram_image_path": self.image_path,
            "sections": []
        }
        
        # Convert sections to config format
        for i, section in enumerate(self.sections):
            coords = section['coordinates']
            
            print(f"\nSection {i+1}: {section['section_id']}")
            section_name = input(f"Enter name for section {i+1}: ") or f"Section {i+1}"
            
            print("Expected items (comma-separated):")
            items_input = input("  Items: ") or "item"
            expected_items = [item.strip() for item in items_input.split(',')]
            
            expected_count = input("Expected item count: ") or "1"
            expected_count = int(expected_count) if expected_count.isdigit() else 1
            
            priority = input("Priority (High/Medium/Low): ") or "Medium"
            priority = priority.capitalize() if priority.lower() in ['high', 'medium', 'low'] else "Medium"
            
            section_config = {
                "section_id": section['section_id'],
                "name": section_name,
                "expected_items": expected_items,
                "expected_count": expected_count,
                "position": coords,
                "priority": priority
            }
            
            config_data["sections"].append(section_config)
        
        # Save to file
        output_file = f"config/planograms/{store_id.lower()}_custom.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"\n✅ Configuration saved to: {output_file}")
        print("You can now use this configuration in your planogram demo!")
    
    def _clear_all(self, event):
        """Clear all drawn sections"""
        for rect in self.rectangles:
            rect.remove()
        
        # Clear text labels  
        for text in self.ax.texts:
            text.remove()
            
        self.rectangles.clear()
        self.sections.clear()
        self.fig.canvas.draw()
        print("🧹 All sections cleared!")
    
    def _undo_last(self, event):
        """Undo the last drawn section"""
        if not self.sections:
            print("❌ Nothing to undo!")
            return
        
        # Remove last rectangle and section
        if self.rectangles:
            self.rectangles[-1].remove()
            self.rectangles.pop()
        
        if self.ax.texts:
            self.ax.texts[-1].remove()
            
        self.sections.pop()
        self.fig.canvas.draw()
        print(f"↶ Undone! {len(self.sections)} sections remaining")
    
    def show(self):
        """Display the interactive drawing interface"""
        plt.tight_layout()
        plt.show()
    
    def get_sections(self) -> List[Dict]:
        """Return the drawn sections"""
        return self.sections


def create_section_drawer(image_path: str) -> SectionDrawer:
    """
    Convenience function to create and show section drawer
    
    Args:
        image_path: Path to the planogram image
        
    Returns:
        SectionDrawer instance
    """
    drawer = SectionDrawer(image_path)
    drawer.show()
    return drawer


if __name__ == "__main__":
    # Example usage
    image_path = "config/images/planogram_demo.jpeg"
    
    if os.path.exists(image_path):
        print("🚀 Starting Section Drawing Tool...")
        drawer = create_section_drawer(image_path)
    else:
        print(f"❌ Image not found: {image_path}")
        print("Please provide a valid image path.") 