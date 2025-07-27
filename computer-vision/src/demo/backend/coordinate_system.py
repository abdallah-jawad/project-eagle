"""
Coordinate System Manager for Planogram Application

This module provides consistent coordinate transformations across:
1. Configuration creation (drawing interface)
2. YOLO inference results
3. Section assignment
4. Display/annotation

All coordinates are stored in a normalized format and transformed as needed.
"""

from typing import Tuple, Dict, Any
from PIL import Image
from .models import BoundingBox

class CoordinateSystem:
    """
    Manages coordinate transformations for the planogram application.
    
    Establishes a consistent coordinate system where:
    - All stored coordinates are normalized to the "reference image" format
    - Reference format: 1080x1440 with aspect-ratio preserved centering
    - All transformations are handled through this class
    """
    
    # Standard reference dimensions for consistency
    REFERENCE_WIDTH = 1080
    REFERENCE_HEIGHT = 1440
    
    @classmethod
    def get_reference_dimensions(cls) -> Tuple[int, int]:
        """Get the standard reference dimensions"""
        return cls.REFERENCE_WIDTH, cls.REFERENCE_HEIGHT
    
    @classmethod
    def image_to_reference_transform(cls, image: Image.Image) -> Dict[str, Any]:
        """
        Calculate transformation parameters from original image to reference format.
        
        Args:
            image: Original PIL Image
            
        Returns:
            Dictionary with transformation parameters:
            {
                'scale': float,          # Scaling factor applied
                'offset_x': int,         # X offset for centering
                'offset_y': int,         # Y offset for centering
                'scaled_width': int,     # Width after scaling
                'scaled_height': int,    # Height after scaling
            }
        """
        original_width, original_height = image.size
        
        # Calculate scaling factor (same as annotator logic)
        scale_w = cls.REFERENCE_WIDTH / original_width
        scale_h = cls.REFERENCE_HEIGHT / original_height
        scale = min(scale_w, scale_h)  # Maintain aspect ratio
        
        # Calculate scaled dimensions
        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)
        
        # Calculate centering offsets
        offset_x = (cls.REFERENCE_WIDTH - scaled_width) // 2
        offset_y = (cls.REFERENCE_HEIGHT - scaled_height) // 2
        
        return {
            'scale': scale,
            'offset_x': offset_x,
            'offset_y': offset_y,
            'scaled_width': scaled_width,
            'scaled_height': scaled_height,
            'original_width': original_width,
            'original_height': original_height
        }
    
    @classmethod
    def original_to_reference(cls, bbox: BoundingBox, image: Image.Image) -> BoundingBox:
        """
        Convert coordinates from original image space to reference space.
        
        Args:
            bbox: BoundingBox in original image coordinates
            image: Original PIL Image for transformation calculation
            
        Returns:
            BoundingBox in reference coordinate system
        """
        transform = cls.image_to_reference_transform(image)
        
        # Apply scaling and offset
        x1 = int(bbox.x1 * transform['scale']) + transform['offset_x']
        y1 = int(bbox.y1 * transform['scale']) + transform['offset_y']
        x2 = int(bbox.x2 * transform['scale']) + transform['offset_x']
        y2 = int(bbox.y2 * transform['scale']) + transform['offset_y']
        
        return BoundingBox(x1, y1, x2, y2)
    
    @classmethod
    def reference_to_original(cls, bbox: BoundingBox, image: Image.Image) -> BoundingBox:
        """
        Convert coordinates from reference space back to original image space.
        
        Args:
            bbox: BoundingBox in reference coordinates
            image: Original PIL Image for transformation calculation
            
        Returns:
            BoundingBox in original image coordinate system
        """
        transform = cls.image_to_reference_transform(image)
        
        # Remove offset and reverse scaling
        x1 = (bbox.x1 - transform['offset_x']) / transform['scale']
        y1 = (bbox.y1 - transform['offset_y']) / transform['scale']
        x2 = (bbox.x2 - transform['offset_x']) / transform['scale']
        y2 = (bbox.y2 - transform['offset_y']) / transform['scale']
        
        return BoundingBox(int(x1), int(y1), int(x2), int(y2))
    
    @classmethod
    def canvas_to_reference(cls, canvas_coords: Dict[str, int], 
                           canvas_size: Tuple[int, int], 
                           original_image: Image.Image) -> BoundingBox:
        """
        Convert coordinates from drawing canvas to reference system.
        
        Args:
            canvas_coords: Dictionary with x1, y1, x2, y2 in canvas coordinates
            canvas_size: (width, height) of the drawing canvas
            original_image: Original image that was displayed on canvas
            
        Returns:
            BoundingBox in reference coordinate system
        """
        canvas_width, canvas_height = canvas_size
        original_width, original_height = original_image.size
        
        # First convert canvas coordinates to original image coordinates
        scale_x = original_width / canvas_width
        scale_y = original_height / canvas_height
        
        orig_x1 = canvas_coords['x1'] * scale_x
        orig_y1 = canvas_coords['y1'] * scale_y
        orig_x2 = canvas_coords['x2'] * scale_x
        orig_y2 = canvas_coords['y2'] * scale_y
        
        # Create bbox in original coordinates
        orig_bbox = BoundingBox(int(orig_x1), int(orig_y1), int(orig_x2), int(orig_y2))
        
        # Convert to reference coordinates
        return cls.original_to_reference(orig_bbox, original_image)
    
    @classmethod
    def normalize_detection_coordinates(cls, detections: list, analysis_image: Image.Image) -> list:
        """
        Normalize YOLO detection coordinates to reference system.
        
        Args:
            detections: List of detection dictionaries from YOLO
            analysis_image: The image that was analyzed (original size)
            
        Returns:
            List of detections with coordinates normalized to reference system
        """
        normalized_detections = []
        
        for detection in detections:
            # Create BoundingBox from YOLO coordinates (already in original image space)
            bbox_coords = detection['bbox']
            orig_bbox = BoundingBox(
                int(bbox_coords[0]), int(bbox_coords[1]), 
                int(bbox_coords[2]), int(bbox_coords[3])
            )
            
            # Convert to reference coordinates
            ref_bbox = cls.original_to_reference(orig_bbox, analysis_image)
            
            # Create normalized detection
            normalized_detection = detection.copy()
            normalized_detection['bbox'] = [ref_bbox.x1, ref_bbox.y1, ref_bbox.x2, ref_bbox.y2]
            normalized_detection['original_bbox'] = bbox_coords  # Keep original for reference
            
            # Handle mask coordinates if present
            if 'mask_polygon' in detection and detection['mask_polygon']:
                normalized_polygon = []
                transform = cls.image_to_reference_transform(analysis_image)
                
                for point in detection['mask_polygon']:
                    if len(point) >= 2:
                        # Convert polygon points to reference coordinates
                        ref_x = int(point[0] * transform['scale']) + transform['offset_x']
                        ref_y = int(point[1] * transform['scale']) + transform['offset_y']
                        normalized_polygon.append([ref_x, ref_y])
                
                normalized_detection['mask_polygon'] = normalized_polygon
                normalized_detection['original_mask_polygon'] = detection['mask_polygon']
            
            normalized_detections.append(normalized_detection)
        
        return normalized_detections
    
    @classmethod
    def get_display_coordinates(cls, bbox: BoundingBox, display_image: Image.Image) -> BoundingBox:
        """
        Convert reference coordinates to display coordinates for annotation.
        
        Args:
            bbox: BoundingBox in reference coordinates
            display_image: The image being displayed/annotated
            
        Returns:
            BoundingBox in display image coordinates
        """
        # If display image is already in reference format, return as-is
        if display_image.size == (cls.REFERENCE_WIDTH, cls.REFERENCE_HEIGHT):
            return bbox
        
        # Otherwise, convert from reference to display coordinates
        return cls.reference_to_original(bbox, display_image) 