import io
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

class PlanogramAnalyzer:
    """Main class for analyzing planogram images and detecting compliance issues"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config: Optional[PlanogramConfig] = None
        self.yolo_model = None  # TODO: Load YOLO model
        
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
    
    def analyze_image(self, image_data: bytes, target_size: tuple = (1080, 1440)) -> Dict[str, Any]:
        """
        Main analysis function that processes an image and returns comprehensive results
        
        Args:
            image_data: Raw image bytes
            target_size: Target size to resize image for analysis (width, height)
        """
        if not self.config:
            return self._create_empty_results("No planogram configuration loaded")
        
        try:
            # Convert bytes to PIL Image
            original_image = Image.open(io.BytesIO(image_data))
            
            # Resize image for analysis to normalize coordinate system
            image = self._resize_image_for_analysis(original_image, target_size)
            
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
        Run YOLO object detection on the image
        TODO: Replace with actual YOLO implementation
        """
        # Mock detection results for demo purposes
        # In real implementation, this would use your trained YOLO model
        detected_items = []
        
        # Sample detections for demonstration (includes misplaced items for demo)
        sample_detections = [
            # CORRECTLY PLACED ITEMS
            # Water bottles (WATER_SECTION: x=54-275, y=55-357)
            {'class_id': 0, 'class_name': 'water_bottle', 'confidence': 0.90, 'bbox': [80, 120, 120, 180]},
            {'class_id': 0, 'class_name': 'bottle', 'confidence': 0.85, 'bbox': [150, 200, 190, 260]},
            
            # Canned drinks (CANNED_DRINKS: x=288-470, y=184-351)  
            {'class_id': 1, 'class_name': 'can', 'confidence': 0.88, 'bbox': [320, 220, 360, 270]},
            {'class_id': 1, 'class_name': 'soda_can', 'confidence': 0.82, 'bbox': [380, 250, 420, 300]},
            
            # Yogurt cups (YOGURT_SECTION: x=455-1042, y=154-355)
            {'class_id': 2, 'class_name': 'yogurt', 'confidence': 0.91, 'bbox': [500, 180, 550, 220]},
            {'class_id': 2, 'class_name': 'dessert_cup', 'confidence': 0.87, 'bbox': [650, 200, 700, 240]},
            {'class_id': 2, 'class_name': 'yogurt', 'confidence': 0.89, 'bbox': [800, 170, 850, 210]},
            
            # Prepared salads (PREPARED_SALADS: x=34-1031, y=384-734)
            {'class_id': 3, 'class_name': 'salad_bowl', 'confidence': 0.92, 'bbox': [100, 450, 180, 520]},
            {'class_id': 3, 'class_name': 'prepared_meal', 'confidence': 0.85, 'bbox': [300, 500, 380, 570]},
            {'class_id': 3, 'class_name': 'salad_bowl', 'confidence': 0.88, 'bbox': [500, 480, 580, 550]},
            {'class_id': 3, 'class_name': 'prepared_meal', 'confidence': 0.90, 'bbox': [700, 520, 780, 590]},
            
            # Wraps (WRAP_SECTION: x=103-368, y=792-1104) 
            {'class_id': 4, 'class_name': 'wrap', 'confidence': 0.86, 'bbox': [140, 850, 190, 920]},
            {'class_id': 4, 'class_name': 'sandwich_wrap', 'confidence': 0.83, 'bbox': [250, 900, 300, 970]},
            
            # Sandwiches (SANDWICH_SECTION: x=378-602, y=795-1103)
            {'class_id': 5, 'class_name': 'sandwich', 'confidence': 0.89, 'bbox': [420, 850, 480, 920]},
            {'class_id': 5, 'class_name': 'boxed_sandwich', 'confidence': 0.84, 'bbox': [500, 950, 560, 1020]},
            
            # Protein plates (PROTEIN_MEALS: x=621-970, y=765-1112)
            {'class_id': 6, 'class_name': 'protein_plate', 'confidence': 0.87, 'bbox': [680, 820, 750, 890]},
            {'class_id': 6, 'class_name': 'meal_container', 'confidence': 0.91, 'bbox': [800, 900, 870, 970]},
            
            # MISPLACED ITEMS (intentionally in wrong sections for demo)
            # Water bottle in CANNED_DRINKS section (should be in WATER_SECTION)
            {'class_id': 0, 'class_name': 'water_bottle', 'confidence': 0.88, 'bbox': [350, 230, 390, 290]},
            
            # Yogurt in WATER_SECTION (should be in YOGURT_SECTION)
            {'class_id': 2, 'class_name': 'yogurt', 'confidence': 0.85, 'bbox': [200, 280, 250, 330]},
            
            # Can in YOGURT_SECTION (should be in CANNED_DRINKS)
            {'class_id': 1, 'class_name': 'can', 'confidence': 0.83, 'bbox': [950, 190, 990, 240]},
            
            # Sandwich in WRAP_SECTION (should be in SANDWICH_SECTION)
            {'class_id': 5, 'class_name': 'sandwich', 'confidence': 0.80, 'bbox': [180, 1000, 240, 1060]},
            
            # Wrap in PROTEIN_MEALS section (should be in WRAP_SECTION)
            {'class_id': 4, 'class_name': 'wrap', 'confidence': 0.78, 'bbox': [720, 1000, 780, 1070]},
            
            # Salad bowl in YOGURT_SECTION (should be in PREPARED_SALADS)
            {'class_id': 3, 'class_name': 'salad_bowl', 'confidence': 0.82, 'bbox': [600, 280, 680, 340]},
            
            # Protein plate in PREPARED_SALADS (should be in PROTEIN_MEALS)
            {'class_id': 6, 'class_name': 'protein_plate', 'confidence': 0.79, 'bbox': [850, 600, 920, 670]},
        ]
        
        for detection in sample_detections:
            if detection['confidence'] >= confidence_threshold:
                bbox = BoundingBox(*detection['bbox'])
                item = DetectedItem(
                    class_id=detection['class_id'],
                    class_name=detection['class_name'],
                    confidence=detection['confidence'],
                    bbox=bbox
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
        """Create an annotated image showing detections and issues"""
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
        
        # Draw bounding boxes for detected items
        for item in detected_items:
            bbox = item.bbox
            
            # Choose color based on whether item is misplaced
            if item in misplaced_item_objects:
                color = "red"  # Misplaced items in red
                width = 3
            else:
                color = "green"  # Correctly placed items in green
                width = 2
            
            # Draw bounding box
            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline=color,
                width=width
            )
            
            # Draw label
            label = f"{item.class_name} ({item.confidence:.2f})"
            draw.text(
                (bbox.x1, bbox.y1 - 20),
                label,
                fill=color,
                font=font
            )
        
        # Draw planogram section boundaries (optional)
        for section in self.config.sections:
            bbox = section.position
            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline="blue",
                width=1
            )
            
            # Section label
            draw.text(
                (bbox.x1, bbox.y1 + 5),
                section.section_id,
                fill="blue",
                font=font
            )
        
        return annotated
    
    def _resize_image_for_analysis(self, image: Image.Image, target_size: tuple) -> Image.Image:
        """
        Resize image for analysis while maintaining aspect ratio
        
        Args:
            image: Original PIL Image
            target_size: Target (width, height)
            
        Returns:
            Resized PIL Image normalized to target_size
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