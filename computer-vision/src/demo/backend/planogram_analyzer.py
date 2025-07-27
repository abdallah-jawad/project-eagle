import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from .models import (
    DetectedItem, PlanogramSection, MisplacedItem, 
    InventoryStatus, Task, AnalysisResults, BoundingBox,
    PlanogramMetrics
)
from .config import PlanogramConfig
from .inference import ModelInference

class PlanogramAnalyzer:
    """Main class for analyzing planogram images and detecting compliance issues"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config: Optional[PlanogramConfig] = None
        self.inference_layer = ModelInference()
        
        if config_path:
            self.load_planogram_config(config_path)
    
    def load_planogram_config(self, config_name: str) -> None:
        """Load planogram configuration"""
        if config_name.endswith('.json'):
            config_path = PlanogramConfig.get_config_path(config_name)
        else:
            config_path = PlanogramConfig.get_config_path(config_name + '.json')
        
        try:
            self.config = PlanogramConfig(config_path)
            print(f"Loaded planogram configuration: {config_name}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = None
    
    def get_planogram_image_path(self) -> Optional[str]:
        """Get the path to the original planogram image"""
        if self.config and self.config.planogram_image_path:
            return self.config.planogram_image_path
        return None
    
    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Main analysis function that processes an image and returns comprehensive results
        
        Args:
            image: PIL Image to analyze
        """
        if not self.config:
            return self._create_empty_results("No planogram configuration loaded")
        
        try:
            # Use the provided PIL Image directly (no resizing needed)
            original_image = image
            
            # Step 1: Run object detection (TODO: Replace with actual YOLO)
            # Hardcoded optimal thresholds
            confidence_threshold = 0.5
            iou_threshold = 0.4
            detected_items = self._run_object_detection(
                image, confidence_threshold, iou_threshold
            )
            
            # Step 2: Assign detected items to sections
            self._assign_items_to_sections(detected_items)
            
            # Step 3: Find misplaced items
            misplaced_items = self._find_misplaced_items(detected_items)
            
            # Step 4: Calculate inventory status
            inventory_status = self._calculate_inventory_status(detected_items)
            
            # Step 5: Generate tasks
            tasks = self._generate_tasks(misplaced_items, inventory_status)
            
            # Step 6: Create annotated image
            annotated_image = self._create_annotated_image(image, detected_items, misplaced_items)
            
            # Step 7: Convert to DataFrames
            results = AnalysisResults(
                detected_items=pd.DataFrame([item.to_dict() for item in detected_items]),
                misplaced_items=pd.DataFrame([item.to_dict() for item in misplaced_items]),
                inventory_status=pd.DataFrame([status.to_dict() for status in inventory_status]),
                tasks=pd.DataFrame([task.to_dict() for task in tasks]),
                annotated_image=annotated_image
            )
            
            return results.to_dict()
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return self._create_empty_results(f"Analysis failed: {str(e)}")
    
    def _run_object_detection(
        self, 
        image: Image.Image, 
        confidence_threshold: float,
        iou_threshold: float
    ) -> List[DetectedItem]:
        """
        Run object detection on the image using the inference layer
        """
        detected_items = []
        
        # Check if inference layer is ready
        if not self.inference_layer.is_ready():
            print("⚠️ Inference layer not ready, returning empty results")
            return detected_items
        
        # Run inference
        detections = self.inference_layer.infer(image, confidence_threshold, iou_threshold)
        
        # Convert detection dictionaries to DetectedItem objects
        for detection in detections:
            bbox = BoundingBox(*detection['bbox'])
            item = DetectedItem(
                class_id=detection['class_id'],
                class_name=detection['class_name'],
                confidence=detection['confidence'],
                bbox=bbox,
                mask=detection.get('mask'),
                mask_polygon=detection.get('mask_polygon', [])
            )
            detected_items.append(item)
        
        return detected_items
    
    def _assign_items_to_sections(self, detected_items: List[DetectedItem]) -> None:
        """Assign detected items to their corresponding planogram sections"""
        for item in detected_items:
            center_x, center_y = item.bbox.center
            section = self.config.find_section_by_position(center_x, center_y)
            item.section_id = section.section_id if section else None
    
    def _find_misplaced_items(self, detected_items: List[DetectedItem]) -> List[MisplacedItem]:
        """Compare detected items against expected planogram positions"""
        misplaced_items = []
        
        for item in detected_items:
            # Get sections where this item should be placed
            expected_sections = self.config.get_sections_for_item(item.class_name)
            
            if not expected_sections:
                continue  # Item not in planogram, skip
            
            # Find the closest expected section
            min_distance = float('inf')
            closest_section = None
            
            item_center = item.bbox.center
            for section in expected_sections:
                section_center = section.position.center
                distance = np.sqrt(
                    (item_center[0] - section_center[0]) ** 2 + 
                    (item_center[1] - section_center[1]) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_section = section
            
            # Check if item is in the wrong section
            if item.section_id != closest_section.section_id:
                misplaced = MisplacedItem(
                    detected_item=item,
                    expected_section=closest_section.section_id,
                    actual_section=item.section_id,
                    distance_from_expected=min_distance
                )
                misplaced_items.append(misplaced)
        
        return misplaced_items
    
    def _calculate_inventory_status(self, detected_items: List[DetectedItem]) -> List[InventoryStatus]:
        """Calculate inventory status for each section"""
        inventory_status = []
        
        # Count items per section
        section_counts = {}
        for item in detected_items:
            if item.section_id:
                section_counts[item.section_id] = section_counts.get(item.section_id, 0) + 1
        
        # Create status for each configured section
        for section in self.config.sections:
            detected_count = section_counts.get(section.section_id, 0)
            status = PlanogramMetrics.determine_inventory_status(
                section.expected_count, detected_count
            )
            
            inventory = InventoryStatus(
                section_id=section.section_id,
                section_name=section.name,
                expected_count=section.expected_count,
                detected_count=detected_count,
                status=status
            )
            inventory_status.append(inventory)
        
        return inventory_status
    
    def _generate_tasks(
        self, 
        misplaced_items: List[MisplacedItem],
        inventory_status: List[InventoryStatus]
    ) -> List[Task]:
        """Generate tasks based on analysis results"""
        tasks = []
        task_counter = 1
        
        # Tasks for misplaced items
        for misplaced in misplaced_items:
            task = Task(
                task_id=f"RELOCATE_{task_counter:03d}",
                description=f"Move {misplaced.detected_item.class_name} from {misplaced.actual_section or 'unknown'} to {misplaced.expected_section}",
                section_id=misplaced.expected_section,
                priority="Medium",
                task_type="Relocate",
                estimated_time=5
            )
            tasks.append(task)
            task_counter += 1
        
        # Tasks for inventory issues
        for status in inventory_status:
            if status.status == "Out of Stock":
                task = Task(
                    task_id=f"RESTOCK_{task_counter:03d}",
                    description=f"Restock {status.section_name} - currently out of stock",
                    section_id=status.section_id,
                    priority="High",
                    task_type="Restock",
                    estimated_time=10
                )
                tasks.append(task)
                task_counter += 1
            
            elif status.status == "Low Stock":
                task = Task(
                    task_id=f"RESTOCK_{task_counter:03d}",
                    description=f"Restock {status.section_name} - low inventory ({status.detected_count}/{status.expected_count})",
                    section_id=status.section_id,
                    priority="Medium",
                    task_type="Restock",
                    estimated_time=8
                )
                tasks.append(task)
                task_counter += 1
            
            elif status.status == "Overstock":
                task = Task(
                    task_id=f"REMOVE_{task_counter:03d}",
                    description=f"Remove excess items from {status.section_name} ({status.detected_count}/{status.expected_count})",
                    section_id=status.section_id,
                    priority="Low",
                    task_type="Remove",
                    estimated_time=5
                )
                tasks.append(task)
                task_counter += 1
        
        return tasks
    
    def _create_annotated_image(
        self, 
        original_image: Image.Image,
        detected_items: List[DetectedItem],
        misplaced_items: List[MisplacedItem]
    ) -> Image.Image:
        """Create an annotated image showing detections and issues with segmentation masks"""
        # Create a copy of the original image
        annotated = original_image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Get set of misplaced item IDs for color coding
        misplaced_item_objects = [m.detected_item for m in misplaced_items]
        
        # Create color mapping for each class
        class_colors = self._get_class_colors(detected_items)
        
        # Draw masks and bounding boxes for detected items
        for item in detected_items:
            bbox = item.bbox
            
            # Get unique color for this class
            class_color = class_colors.get(item.class_name, "blue")
            
            # Choose color based on whether item is misplaced
            if item in misplaced_item_objects:
                color = "red"  # Misplaced items in red
                mask_color = (255, 0, 0, 64)  # Semi-transparent red
                width = 3
            else:
                color = class_color  # Use class-specific color
                # Convert color name to RGBA for mask
                mask_color = self._color_name_to_rgba(color, alpha=64)
                width = 2
            
            # Draw segmentation mask if available
            if item.mask is not None:
                try:
                    # Try polygon-based mask first (more efficient)
                    if item.mask_polygon:
                        # Create a mask overlay
                        mask_overlay = Image.new('RGBA', annotated.size, (0, 0, 0, 0))
                        mask_draw = ImageDraw.Draw(mask_overlay)
                        
                        # Convert polygon coordinates to PIL format
                        polygon_points = [(int(x), int(y)) for x, y in item.mask_polygon]
                        
                        # Draw filled polygon for mask
                        mask_draw.polygon(polygon_points, fill=mask_color)
                        
                        # Composite the mask overlay onto the annotated image
                        annotated = Image.alpha_composite(annotated.convert('RGBA'), mask_overlay).convert('RGB')
                        draw = ImageDraw.Draw(annotated)
                        
                        # Draw polygon outline
                        draw.polygon(polygon_points, outline=color, width=width)
                        
                    else:
                        # Fallback to binary mask overlay
                        annotated = self._draw_mask_overlay(annotated, item.mask, mask_color)
                        draw = ImageDraw.Draw(annotated)
                        
                        # Draw bounding box as outline
                        draw.rectangle(
                            [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                            outline=color,
                            width=width
                        )
                        
                except Exception as e:
                    print(f"⚠️ Error drawing mask for {item.class_name}: {e}")
                    # Fallback to bounding box only
                    draw.rectangle(
                        [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                        outline=color,
                        width=width
                    )
            else:
                # Draw bounding box if no mask available
                draw.rectangle(
                    [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                    outline=color,
                    width=width
                )
            
            # Draw label with mask information
            label = f"{item.class_name} ({item.confidence:.2f})"
            if item.mask is not None:
                area = item.calculate_mask_area()
                label += f" [Area: {area:.0f}]"
            
            # Try different label positions to avoid overlap
            label_positions = [
                (bbox.x1, bbox.y1 - 25),  # Above
                (bbox.x2 + 5, bbox.y1),   # Right side
                (bbox.x1, bbox.y2 + 5),   # Below
                (bbox.x1 - 100, bbox.y1)  # Left side
            ]
            
            label_placed = False
            for label_x, label_y in label_positions:
                # Check if this position is within image bounds
                if label_x >= 0 and label_y >= 0:
                    # Draw label background for better visibility
                    label_bbox = draw.textbbox((label_x, label_y), label, font=font)
                    
                    # Check if label would fit within image bounds
                    if label_bbox[2] <= annotated.width and label_bbox[3] <= annotated.height:
                        draw.rectangle(
                            [label_bbox[0] - 2, label_bbox[1] - 2, label_bbox[2] + 2, label_bbox[3] + 2],
                            fill="white",
                            outline=color,
                            width=1
                        )
                        
                        draw.text(
                            (label_x, label_y),
                            label,
                            fill=color,
                            font=font
                        )
                        label_placed = True
                        break
            
            # If no position worked, place it at the original position
            if not label_placed:
                label_x = bbox.x1
                label_y = bbox.y1 - 25
                label_bbox = draw.textbbox((label_x, label_y), label, font=font)
                draw.rectangle(
                    [label_bbox[0] - 2, label_bbox[1] - 2, label_bbox[2] + 2, label_bbox[3] + 2],
                    fill="white",
                    outline=color,
                    width=1
                )
                draw.text(
                    (label_x, label_y),
                    label,
                    fill=color,
                    font=font
                )
        
        # Note: Planogram section boundaries are not drawn on the annotated image
        # to avoid confusion with the actual detected objects
        
        # Draw color legend
        self._draw_color_legend(annotated, class_colors, font)
        
        return annotated
    
    def _get_class_colors(self, detected_items: List[DetectedItem]) -> Dict[str, str]:
        """
        Generate unique colors for each class
        
        Args:
            detected_items: List of detected items
            
        Returns:
            Dictionary mapping class names to colors
        """
        # Predefined color palette for classes
        colors = [
            "blue", "green", "orange", "purple", "brown", "pink", "gray", 
            "cyan", "magenta", "lime", "navy", "maroon", "olive", "teal",
            "coral", "gold", "indigo", "violet", "crimson", "forestgreen"
        ]
        
        # Get unique class names
        unique_classes = list(set(item.class_name for item in detected_items))
        
        # Create color mapping
        class_colors = {}
        for i, class_name in enumerate(unique_classes):
            color_index = i % len(colors)
            class_colors[class_name] = colors[color_index]
        
        return class_colors
    
    def _color_name_to_rgba(self, color_name: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """
        Convert color name to RGBA tuple
        
        Args:
            color_name: Name of the color
            alpha: Alpha value (0-255)
            
        Returns:
            RGBA tuple
        """
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "brown": (165, 42, 42),
            "pink": (255, 192, 203),
            "gray": (128, 128, 128),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "lime": (0, 255, 0),
            "navy": (0, 0, 128),
            "maroon": (128, 0, 0),
            "olive": (128, 128, 0),
            "teal": (0, 128, 128),
            "coral": (255, 127, 80),
            "gold": (255, 215, 0),
            "indigo": (75, 0, 130),
            "violet": (238, 130, 238),
            "crimson": (220, 20, 60),
            "forestgreen": (34, 139, 34)
        }
        
        rgb = color_map.get(color_name.lower(), (0, 0, 255))  # Default to blue
        return rgb + (alpha,)
    
    def _draw_color_legend(self, image: Image.Image, class_colors: Dict[str, str], font) -> None:
        """
        Draw a color legend showing which color corresponds to which class
        
        Args:
            image: PIL Image to draw on
            class_colors: Dictionary mapping class names to colors
            font: Font to use for text
        """
        if not class_colors:
            return
        
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Legend position (top-right corner)
        legend_x = width - 200
        legend_y = 10
        box_width = 180
        box_height = 20 * len(class_colors) + 30
        
        # Draw legend background
        draw.rectangle(
            [legend_x, legend_y, legend_x + box_width, legend_y + box_height],
            fill="white",
            outline="black",
            width=2
        )
        
        # Draw legend title
        draw.text(
            (legend_x + 5, legend_y + 5),
            "Class Colors:",
            fill="black",
            font=font
        )
        
        # Draw color boxes and labels
        for i, (class_name, color) in enumerate(class_colors.items()):
            y_pos = legend_y + 25 + (i * 20)
            
            # Draw color box
            draw.rectangle(
                [legend_x + 5, y_pos, legend_x + 20, y_pos + 15],
                fill=color,
                outline="black",
                width=1
            )
            
            # Draw class name (truncated if too long)
            display_name = class_name[:15] + "..." if len(class_name) > 15 else class_name
            draw.text(
                (legend_x + 25, y_pos),
                display_name,
                fill="black",
                font=font
            )
    
    def _draw_mask_overlay(
        self, 
        image: Image.Image, 
        mask: np.ndarray, 
        color: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        Draw a binary mask overlay on an image
        
        Args:
            image: PIL Image to draw on
            mask: Binary mask as numpy array (H, W)
            color: RGBA color tuple for the mask
            
        Returns:
            Image with mask overlay
        """
        try:
            # Convert mask to PIL Image
            mask_pil = Image.fromarray(mask.astype(np.uint8) * 255, mode='L')
            
            # Resize mask to match image size if needed
            if mask_pil.size != image.size:
                mask_pil = mask_pil.resize(image.size, Image.NEAREST)
            
            # Create color overlay
            color_overlay = Image.new('RGBA', image.size, color)
            
            # Apply mask as alpha channel
            color_overlay.putalpha(mask_pil)
            
            # Composite with original image
            result = Image.alpha_composite(image.convert('RGBA'), color_overlay)
            
            return result.convert('RGB')
            
        except Exception as e:
            print(f"⚠️ Error creating mask overlay: {e}")
            return image
    
    def _create_empty_results(self, message: str = "No results") -> Dict[str, Any]:
        """Create empty results structure with error message"""
        return {
            'detected_items': pd.DataFrame(),
            'misplaced_items': pd.DataFrame(),
            'inventory_status': pd.DataFrame(),
            'tasks': pd.DataFrame(),
            'annotated_image': None,
            'error': message
        } 