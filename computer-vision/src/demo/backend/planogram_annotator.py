import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from .config import PlanogramConfig

class PlanogramAnnotator:
    """Utility class to annotate planogram images with section boundaries"""
    
    def __init__(self, config: PlanogramConfig):
        self.config = config
        
    def annotate_planogram_image(self, output_path: Optional[str] = None, target_size: tuple = (1080, 1440)) -> str:
        """
        Create an annotated version of the planogram image with section boundaries
        
        Args:
            output_path: Optional custom output path. If None, creates annotated version in same directory
            target_size: Target size (width, height) to resize image to. Default is 1080x1440 for 3:4 aspect ratio
            
        Returns:
            Path to the annotated image
        """
        if not self.config.planogram_image_path:
            raise ValueError("No planogram image path specified in configuration")
        
        # Load the original image
        if not os.path.exists(self.config.planogram_image_path):
            raise FileNotFoundError(f"Planogram image not found: {self.config.planogram_image_path}")
        
        image = Image.open(self.config.planogram_image_path)
        
        # Resize image to target size while maintaining aspect ratio
        resized_image = self._resize_image_with_aspect_ratio(image, target_size)
        
        # Create annotated version
        annotated_image = self._draw_section_boundaries(resized_image)
        
        # Determine output path
        if output_path is None:
            base_name = os.path.splitext(self.config.planogram_image_path)[0]
            output_path = f"{base_name}_annotated_1080x1440.jpg"
        
        # Save annotated image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        annotated_image.save(output_path, format='JPEG', quality=95)
        
        return output_path
    
    def _draw_section_boundaries(self, image: Image.Image) -> Image.Image:
        """Draw section boundaries and labels on the image"""
        # Create a copy to work with
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a nice font, fallback to default
        # Try multiple font options for cross-platform compatibility
        font_large = None
        font_small = None
        
        # List of fonts to try (common across different OS)
        font_options = [
            "arial.ttf",           # Windows
            "Arial.ttf",           # Windows (case-sensitive systems)
            "DejaVuSans.ttf",      # Linux
            "Helvetica.ttc",       # macOS
            "LiberationSans-Regular.ttf",  # Linux alternative
            "/System/Library/Fonts/Arial.ttf",  # macOS absolute path
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # Linux absolute path
        ]
        
        for font_name in font_options:
            try:
                font_large = ImageFont.truetype(font_name, 24)
                font_small = ImageFont.truetype(font_name, 16)
                break
            except (OSError, IOError):
                continue
        
        # If no fonts found, use default
        if font_large is None:
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Color scheme for different priority levels
        priority_colors = {
            "High": "#FF4444",      # Red
            "Medium": "#4444FF",    # Blue  
            "Low": "#44FF44"        # Green
        }
        
        # Draw each section
        for i, section in enumerate(self.config.sections):
            bbox = section.position
            color = priority_colors.get(section.priority, "#888888")
            
            # Draw bounding rectangle
            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline=color,
                width=3
            )
            
            # Draw semi-transparent background for label
            label_height = 30
            label_bg_coords = [
                bbox.x1, 
                bbox.y1 - label_height,
                min(bbox.x1 + 250, bbox.x2), 
                bbox.y1
            ]
            
            # Create semi-transparent overlay for label background
            overlay = Image.new('RGBA', annotated.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                label_bg_coords,
                fill=(*self._hex_to_rgb(color), 200)  # Semi-transparent
            )
            annotated = Image.alpha_composite(annotated.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(annotated)
            
            # Draw section ID label
            draw.text(
                (bbox.x1 + 5, bbox.y1 - 25),
                section.section_id,
                fill="white",
                font=font_small
            )
            
            # Draw expected count in corner
            count_text = f"Exp: {section.expected_count}"
            draw.text(
                (bbox.x1 + 5, bbox.y1 + 5),
                count_text,
                fill=color,
                font=font_small
            )
            
            # Draw priority indicator
            priority_text = f"[{section.priority}]"
            draw.text(
                (bbox.x2 - 80, bbox.y1 + 5),
                priority_text,
                fill=color,
                font=font_small
            )
        
        # Draw legend
        self._draw_legend(draw, font_small, priority_colors, annotated.width, annotated.height)
        
        return annotated
    
    def _draw_legend(self, draw, font, priority_colors, img_width, img_height):
        """Draw a legend explaining the color coding"""
        legend_x = img_width - 200
        legend_y = img_height - 120
        
        # Legend background
        legend_coords = [legend_x - 10, legend_y - 10, img_width - 10, img_height - 10]
        draw.rectangle(legend_coords, fill="white", outline="black", width=1)
        
        # Legend title
        draw.text((legend_x, legend_y), "Priority Levels:", fill="black", font=font)
        
        # Legend items
        y_offset = 20
        for priority, color in priority_colors.items():
            # Color square
            color_coords = [legend_x, legend_y + y_offset, legend_x + 15, legend_y + y_offset + 15]
            draw.rectangle(color_coords, fill=color, outline="black")
            
            # Priority text
            draw.text((legend_x + 20, legend_y + y_offset), priority, fill="black", font=font)
            y_offset += 20
    
    def _resize_image_with_aspect_ratio(self, image: Image.Image, target_size: tuple) -> Image.Image:
        """
        Resize image to target size while maintaining aspect ratio
        
        Args:
            image: Original PIL Image
            target_size: Target (width, height)
            
        Returns:
            Resized PIL Image
        """
        target_width, target_height = target_size
        original_width, original_height = image.size
        
        # Calculate scaling factor to fit within target size while maintaining aspect ratio
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = min(scale_w, scale_h)  # Use smaller scale to fit within bounds
        
        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with exact target size and paste resized image centered
        final_image = Image.new('RGB', target_size, (255, 255, 255))  # White background
        
        # Calculate position to center the image
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        final_image.paste(resized, (paste_x, paste_y))
        
        return final_image
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @classmethod
    def create_annotated_planogram(cls, config_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convenience method to create an annotated planogram from a config file
        
        Args:
            config_path: Path to the planogram configuration JSON file
            output_dir: Optional output directory. If None, saves in same dir as config
            
        Returns:
            Path to the annotated image
        """
        config = PlanogramConfig(config_path)
        annotator = cls(config)
        
        if output_dir and config.planogram_image_path:
            base_name = os.path.splitext(os.path.basename(config.planogram_image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_annotated.jpg")
        else:
            output_path = None
            
        return annotator.annotate_planogram_image(output_path)
    
    def get_section_info(self) -> dict:
        """Get summary information about all sections"""
        return {
            'total_sections': len(self.config.sections),
            'total_expected_items': sum(section.expected_count for section in self.config.sections),
            'sections_by_priority': {
                priority: len([s for s in self.config.sections if s.priority == priority])
                for priority in ['High', 'Medium', 'Low']
            },
            'sections': [
                {
                    'id': section.section_id,
                    'name': section.name,
                    'expected_count': section.expected_count,
                    'priority': section.priority,
                    'expected_items': section.expected_items
                }
                for section in self.config.sections
            ]
        } 