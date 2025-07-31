import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from .models import (
    DetectedItem, PlanogramSection, MisplacedItem, 
    InventoryStatus, DetailedInventoryStatus,
    Task, AnalysisResults, BoundingBox, PlanogramMetrics
)
from .config import PlanogramConfig
from .inference import ModelInference
from .coordinate_system import CoordinateSystem

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
            
            
            # Step 4.5: Calculate detailed inventory status
            detailed_inventory_status = self._calculate_detailed_inventory_status(detected_items, misplaced_items)
            
            # Step 5: Generate tasks
            tasks = self._generate_tasks(detailed_inventory_status, misplaced_items)
            
            # Step 6: Create annotated image
            annotated_image = self._create_annotated_image(image, detected_items, misplaced_items)
            
            # Step 7: Convert to DataFrames
            results = AnalysisResults(
                detected_items=pd.DataFrame([item.to_dict() for item in detected_items]),
                misplaced_items=pd.DataFrame([item.to_dict() for item in misplaced_items]),
                detailed_inventory_status=pd.DataFrame([status.to_dict() for status in detailed_inventory_status]),
                tasks=pd.DataFrame([task.to_dict() for task in tasks]) if tasks else pd.DataFrame(),
                annotated_image=annotated_image
            )
            
            return results
            
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
        
        # Run inference - YOLO returns coordinates in original image space
        detections = self.inference_layer.infer(image, confidence_threshold, iou_threshold)
        
        # Normalize detection coordinates to reference system
        normalized_detections = CoordinateSystem.normalize_detection_coordinates(detections, image)
        
        # Convert detection dictionaries to DetectedItem objects
        for detection in normalized_detections:
            bbox = BoundingBox(*detection['bbox'])  # Now in reference coordinates
            item = DetectedItem(
                class_id=detection['class_id'],
                class_name=detection['class_name'],
                confidence=detection['confidence'],
                bbox=bbox,  # Reference coordinates
                mask=detection.get('mask'),
                mask_polygon=detection.get('mask_polygon', [])  # Also normalized
            )
            detected_items.append(item)
        
        return detected_items
    
    def _assign_items_to_sections(self, detected_items: List[DetectedItem]) -> None:
        """Assign detected items to their corresponding planogram sections using polygon centroids"""
        for item in detected_items:
            # Use the DetectedItem's smart center calculation (polygon centroid or bbox center)
            center_x, center_y = item.center
            
            # Find which section contains this center point
            section = self.config.find_section_by_position(center_x, center_y)
            item.section_id = section.section_id if section else None
    
    def _find_misplaced_items(self, detected_items: List[DetectedItem]) -> List[MisplacedItem]:
        """Find misplaced items using geometric containment logic with polygon centroids"""
        misplaced_items = []
        
        for item in detected_items:
            # Get sections where this item should be placed
            expected_sections = self.config.get_sections_for_item(item.class_name)
            
            if not expected_sections:
                continue  # Item not in planogram, skip
            
            # Use the DetectedItem's smart center calculation (polygon centroid or bbox center)
            center_x, center_y = item.center
            
            # Check if item's center is within ANY of its expected sections
            item_in_expected_section = False
            correct_section_id = None
            
            for section in expected_sections:
                # Check if center point is within this section's boundaries
                if self._point_in_section(center_x, center_y, section):
                    item_in_expected_section = True
                    correct_section_id = section.section_id
                    break
            
            # If the item's center is not in any expected section, it's misplaced
            if not item_in_expected_section:
                # Find the closest expected section for reporting purposes
                closest_section = self._find_closest_expected_section(center_x, center_y, expected_sections)
                
                misplaced = MisplacedItem(
                    detected_item=item,
                    expected_section=closest_section.section_id if closest_section else "Unknown",
                    actual_section=item.section_id,  # Where it currently is (could be None)
                    distance_from_expected=0.0  # Not using distance anymore, but keeping for compatibility
                )
                misplaced_items.append(misplaced)
        
        return misplaced_items
    
    def _point_in_section(self, x: float, y: float, section: PlanogramSection) -> bool:
        """
        Check if a point is within a section's boundaries
        
        Args:
            x: X coordinate of the point
            y: Y coordinate of the point
            section: PlanogramSection to check against
            
        Returns:
            True if point is within section boundaries, False otherwise
        """
        bbox = section.position
        return bbox.x1 <= x <= bbox.x2 and bbox.y1 <= y <= bbox.y2
    
    def _find_closest_expected_section(self, x: float, y: float, 
                                     expected_sections: List[PlanogramSection]) -> Optional[PlanogramSection]:
        """
        Find the closest expected section to a given point
        
        Args:
            x: X coordinate of the point
            y: Y coordinate of the point
            expected_sections: List of sections where the item should be
            
        Returns:
            The closest expected section, or None if no sections provided
        """
        if not expected_sections:
            return None
        
        min_distance = float('inf')
        closest_section = None
        
        for section in expected_sections:
            # Calculate distance from point to section center
            section_center_x = (section.position.x1 + section.position.x2) / 2
            section_center_y = (section.position.y1 + section.position.y2) / 2
            
            distance = ((x - section_center_x) ** 2 + (y - section_center_y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_section = section
        
        return closest_section
    
    def _calculate_detailed_inventory_status(
        self, 
        detected_items: List[DetectedItem], 
        misplaced_items: List[MisplacedItem]
    ) -> List[DetailedInventoryStatus]:
        """Calculate detailed inventory status for each section with item type breakdown"""
        detailed_status = []
        
        # Count detected items by section and type
        section_item_counts = {}
        for item in detected_items:
            if item.section_id:
                if item.section_id not in section_item_counts:
                    section_item_counts[item.section_id] = {}
                item_type = item.class_name
                section_item_counts[item.section_id][item_type] = section_item_counts[item.section_id].get(item_type, 0) + 1
        
        # Count misplaced items by their expected sections and types
        misplaced_counts = {}
        for misplaced in misplaced_items:
            expected_section = misplaced.expected_section
            item_type = misplaced.detected_item.class_name
            
            if expected_section not in misplaced_counts:
                misplaced_counts[expected_section] = {}
            misplaced_counts[expected_section][item_type] = misplaced_counts[expected_section].get(item_type, 0) + 1
        
        # Create detailed status for each configured section
        for section in self.config.sections:
            section_id = section.section_id
            
            # Build expected items dict (distribute expected counts among item types)
            expected_items = {}
            expected_visible_items = {}
            total_expected_types = len(section.expected_items)
            if total_expected_types > 0:
                base_count = section.expected_count // total_expected_types
                remainder = section.expected_count % total_expected_types
                
                base_visible_count = section.expected_visible_count // total_expected_types
                visible_remainder = section.expected_visible_count % total_expected_types
                
                for i, item_type in enumerate(section.expected_items):
                    expected_items[item_type] = base_count + (1 if i < remainder else 0)
                    expected_visible_items[item_type] = base_visible_count + (1 if i < visible_remainder else 0)
            
            # Get detected items in this section
            detected_items_dict = section_item_counts.get(section_id, {})
            
            # Get misplaced items that belong to this section
            misplaced_items_dict = misplaced_counts.get(section_id, {})
            
            detailed_inv_status = DetailedInventoryStatus(
                section_id=section_id,
                section_name=section.name,
                expected_items=expected_items,
                expected_visible_items=expected_visible_items,
                detected_items=detected_items_dict,
                misplaced_items=misplaced_items_dict,
            )
            
            detailed_status.append(detailed_inv_status)
        
        return detailed_status
    
    def _generate_tasks(
        self,
        detailed_inventory: List[DetailedInventoryStatus],
        misplaced_items: List[MisplacedItem]
    ) -> List[Task]:
        """Generate tasks based on detailed inventory and misplaced items"""
        tasks = []
        task_counter = 1

        # Tasks for misplaced items (relocate)
        for item in misplaced_items:
            task = Task(
                task_id=f"RELOCATE_{task_counter:03d}",
                description=f"Move {item.detected_item.class_name} from {item.actual_section or 'unknown'} to {item.expected_section}",
                section_id=item.expected_section,
                priority="Medium",
                task_type="Relocate",
                estimated_time=5
            )
            tasks.append(task)
            task_counter += 1

        # Tasks from detailed inventory breakdown (restock, check, etc.)
        for section_status in detailed_inventory:
            section_id = section_status.section_id
            section_name = section_status.section_name
            
            for item_breakdown in section_status.get_item_breakdown():
                item_type = item_breakdown['item_type']
                status = item_breakdown['availability_status']
                
                if status == "Sold Out" or status == "Low Stock":
                    task = Task(
                        task_id=f"RESTOCK_{task_counter:03d}",
                        description=f"Restock {item_type} in {section_name} ({status})",
                        section_id=section_id,
                        priority="High" if status == "Sold Out" else "Medium",
                        task_type="Restock",
                        estimated_time=10
                    )
                    tasks.append(task)
                    task_counter += 1
                
                elif status == "Misplaced Only" or status == "Partially Misplaced":
                    task = Task(
                        task_id=f"CHECK_{task_counter:03d}",
                        description=f"Check for misplaced {item_type} for section {section_name}",
                        section_id=section_id,
                        priority="Medium",
                        task_type="Check",
                        estimated_time=7
                    )
                    tasks.append(task)
                    task_counter += 1

                elif item_breakdown.get('availability_status') == "Overstock":
                    task = Task(
                        task_id=f"REMOVE_{task_counter:03d}",
                        description=f"Remove excess {item_type} from {section_name}",
                        section_id=section_id,
                        priority="Low",
                        task_type="Remove",
                        estimated_time=5
                    )
                    tasks.append(task)
                    task_counter += 1

                elif item_breakdown.get('availability_status') == "Unexpected Item":
                    task = Task(
                        task_id=f"REMOVE_{task_counter:03d}",
                        description=f"Remove unexpected item {item_type} from {section_name}",
                        section_id=section_id,
                        priority="Medium",
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
        """Create an annotated image showing detected items only"""
        # Create a copy of the original image for annotation
        annotated = original_image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font, fallback to default if not available
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Color scheme for different classes
        class_colors = {
            'bottled_drinks': '#FF6B6B',      # Red
            'canned_drinks': '#4ECDC4',       # Teal
            'large_plates': '#45B7D1',        # Blue
            'salads_bowls': '#96CEB4',        # Green
            'sandwiches': '#FFEAA7',          # Yellow
            'small_plates': '#DDA0DD',        # Plum
            'wraps': '#98D8C8',               # Mint
            'yogurt_cups_large': '#F7DC6F',   # Light yellow
            'yogurt_cups_small': '#BB8FCE'    # Light purple
        }
        
        # Draw detected items
        for item in detected_items:
            # Convert from reference coordinates to display coordinates
            display_bbox = CoordinateSystem.reference_to_original(item.bbox, original_image)
            
            # Use class-specific color for all items
            color = class_colors.get(item.class_name, '#888888')
            width = 2
            
            # Create label
            label = f"{item.class_name} ({item.confidence:.2f})"
            
            # Handle mask visualization if available
            if item.mask is not None or item.mask_polygon:
                # Semi-transparent color for mask overlay
                mask_color = (*self._hex_to_rgb(color), 100)  # Semi-transparent
                
                try:
                    # Try polygon-based mask first (more efficient)
                    if item.mask_polygon:
                        # Convert polygon coordinates from reference to display
                        display_polygon = []
                        for point in item.mask_polygon:
                            if len(point) >= 2:
                                # Transform point from reference to original coordinates
                                ref_bbox_point = BoundingBox(point[0], point[1], point[0], point[1])
                                display_point = CoordinateSystem.reference_to_original(ref_bbox_point, original_image)
                                display_polygon.append((int(display_point.x1), int(display_point.y1)))
                        
                        if display_polygon:
                            # Create a mask overlay
                            mask_overlay = Image.new('RGBA', annotated.size, (0, 0, 0, 0))
                            mask_draw = ImageDraw.Draw(mask_overlay)
                            
                            # Draw filled polygon for mask
                            mask_draw.polygon(display_polygon, fill=mask_color)
                            
                            # Composite the mask overlay onto the annotated image
                            annotated = Image.alpha_composite(annotated.convert('RGBA'), mask_overlay).convert('RGB')
                            draw = ImageDraw.Draw(annotated)
                            
                            # Draw polygon outline
                            draw.polygon(display_polygon, outline=color, width=width)
                        
                    else:
                        # Fallback to bounding box visualization
                        draw.rectangle(
                            [display_bbox.x1, display_bbox.y1, display_bbox.x2, display_bbox.y2],
                            outline=color,
                            width=width
                        )
                        
                except Exception as e:
                    print(f"⚠️ Error drawing mask for {item.class_name}: {e}")
                    # Fallback to bounding box
                    draw.rectangle(
                        [display_bbox.x1, display_bbox.y1, display_bbox.x2, display_bbox.y2],
                        outline=color,
                        width=width
                    )
            else:
                # Draw bounding box only
                draw.rectangle(
                    [display_bbox.x1, display_bbox.y1, display_bbox.x2, display_bbox.y2],
                    outline=color,
                    width=width
                )
            
            # Draw label with background
            if font:
                # Try multiple positions for label to avoid overlap
                label_positions = [
                    (display_bbox.x1, display_bbox.y1 - 25),  # Above
                    (display_bbox.x1, display_bbox.y2 + 5),   # Below
                    (display_bbox.x2 + 5, display_bbox.y1),   # Right
                    (max(0, display_bbox.x1 - 100), display_bbox.y1)  # Left
                ]
                
                label_placed = False
                for label_x, label_y in label_positions:
                    # Check if this position is within image bounds
                    if label_x >= 0 and label_y >= 0:
                        # Draw label background for better visibility
                        try:
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
                        except:
                            # Fallback for older PIL versions
                            draw.text((label_x, label_y), label, fill=color, font=font)
                            label_placed = True
                            break
                
                # If no position worked, place it at the original position
                if not label_placed:
                    label_x = display_bbox.x1
                    label_y = display_bbox.y1 - 25
                    try:
                        label_bbox = draw.textbbox((label_x, label_y), label, font=font)
                        draw.rectangle(
                            [label_bbox[0] - 2, label_bbox[1] - 2, label_bbox[2] + 2, label_bbox[3] + 2],
                            fill="white",
                            outline=color,
                            width=1
                        )
                    except:
                        pass
                    draw.text((label_x, label_y), label, fill=color, font=font)
        
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
        return AnalysisResults.create_empty()
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) 