from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from PIL import Image
import numpy as np

@dataclass
class BoundingBox:
    """Represents a bounding box for detected objects"""
    x1: float
    y1: float
    x2: float
    y2: float
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get the center point of the bounding box"""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    @property
    def area(self) -> float:
        """Calculate the area of the bounding box"""
        return (self.x2 - self.x1) * (self.y2 - self.y1)
    
    def iou(self, other: 'BoundingBox') -> float:
        """Calculate Intersection over Union with another bounding box"""
        # Calculate intersection
        x1_inter = max(self.x1, other.x1)
        y1_inter = max(self.y1, other.y1)
        x2_inter = min(self.x2, other.x2)
        y2_inter = min(self.y2, other.y2)
        
        if x1_inter < x2_inter and y1_inter < y2_inter:
            intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        else:
            intersection = 0.0
        
        # Calculate union
        union = self.area + other.area - intersection
        
        return intersection / union if union > 0 else 0.0

@dataclass
class DetectedItem:
    """Represents a detected item from YOLO model with segmentation masks"""
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    section_id: Optional[str] = None
    mask: Optional[np.ndarray] = None  # Binary segmentation mask
    mask_polygon: Optional[List[List[float]]] = None  # Polygon coordinates
    
    @property
    def center(self) -> Tuple[float, float]:
        """
        Get the center point of the detected item.
        Uses polygon centroid if available, otherwise falls back to bounding box center.
        
        Returns:
            Tuple of (center_x, center_y) coordinates
        """
        # Use polygon centroid if available and valid
        if self.mask_polygon and len(self.mask_polygon) >= 3:
            return self._calculate_polygon_centroid()
        else:
            # Fall back to bounding box center
            return self.bbox.center
    
    def _calculate_polygon_centroid(self) -> Tuple[float, float]:
        """
        Calculate the centroid (center point) of the mask polygon
        
        Returns:
            Tuple of (center_x, center_y) coordinates
        """
        if not self.mask_polygon or len(self.mask_polygon) < 3:
            return self.bbox.center
        
        # Calculate centroid using arithmetic mean of all points
        total_x = 0.0
        total_y = 0.0
        
        for point in self.mask_polygon:
            if len(point) >= 2:
                total_x += point[0]
                total_y += point[1]
        
        num_points = len(self.mask_polygon)
        centroid_x = total_x / num_points
        centroid_y = total_y / num_points
        
        return centroid_x, centroid_y
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        center_x, center_y = self.center  # Use the smart center calculation
        
        result = {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': self.confidence,
            'x1': self.bbox.x1,
            'y1': self.bbox.y1,
            'x2': self.bbox.x2,
            'y2': self.bbox.y2,
            'center_x': center_x,
            'center_y': center_y,
            'section_id': self.section_id,
            'has_mask': self.mask is not None,
            'mask_area': self.calculate_mask_area() if self.mask is not None else 0.0,
            'mask_perimeter': self.calculate_mask_perimeter() if self.mask_polygon else 0.0
        }
        return result
    
    def calculate_mask_area(self) -> float:
        """Calculate the area of the segmentation mask in pixels"""
        if self.mask is None:
            return 0.0
        return float(np.sum(self.mask))
    
    def calculate_mask_perimeter(self) -> float:
        """Calculate the perimeter of the mask using polygon coordinates"""
        if not self.mask_polygon or len(self.mask_polygon) < 3:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(self.mask_polygon)):
            p1 = self.mask_polygon[i]
            p2 = self.mask_polygon[(i + 1) % len(self.mask_polygon)]
            
            # Calculate Euclidean distance
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            perimeter += np.sqrt(dx*dx + dy*dy)
        
        return perimeter

@dataclass
class PlanogramSection:
    """Represents a section in the planogram"""
    section_id: str
    name: str
    expected_items: List[str]  # List of expected class names
    expected_count: int
    position: BoundingBox  # Expected position on shelf
    priority: str = "Medium"  # High, Medium, Low
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for configuration"""
        return {
            'section_id': self.section_id,
            'name': self.name,
            'expected_items': self.expected_items,
            'expected_count': self.expected_count,
            'position': {
                'x1': self.position.x1,
                'y1': self.position.y1,
                'x2': self.position.x2,
                'y2': self.position.y2
            },
            'priority': self.priority
        }

@dataclass
class MisplacedItem:
    """Represents an item that is not in its correct section"""
    detected_item: DetectedItem
    expected_section: str
    actual_section: Optional[str]
    distance_from_expected: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'item_class': self.detected_item.class_name,
            'confidence': self.detected_item.confidence,
            'expected_section': self.expected_section,
            'actual_section': self.actual_section or 'Unknown',
            'distance_from_expected': round(self.distance_from_expected, 2),
            'center_x': self.detected_item.bbox.center[0],
            'center_y': self.detected_item.bbox.center[1]
        }

@dataclass
class InventoryStatus:
    """Represents inventory status for a section"""
    section_id: str
    section_name: str
    expected_count: int
    detected_count: int
    status: str  # "In Stock", "Low Stock", "Out of Stock", "Overstock"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'section_id': self.section_id,
            'section_name': self.section_name,
            'expected_count': self.expected_count,
            'detected_count': self.detected_count,
            'difference': self.detected_count - self.expected_count,
            'status': self.status
        }

@dataclass
class DetailedInventoryStatus:
    """Represents detailed inventory status for a section with item type breakdown"""
    section_id: str
    section_name: str
    expected_items: Dict[str, int]  # {item_type: expected_count}
    detected_items: Dict[str, int]  # {item_type: detected_count}
    misplaced_items: Dict[str, int]  # {item_type: count_found_elsewhere}
    status: str  # Overall section status
    item_statuses: Dict[str, str]  # {item_type: status}
    
    @property
    def total_expected(self) -> int:
        """Total expected items in section"""
        return sum(self.expected_items.values())
    
    @property
    def total_detected(self) -> int:
        """Total detected items in section"""
        return sum(self.detected_items.values())
    
    @property
    def total_misplaced(self) -> int:
        """Total items found elsewhere that belong to this section"""
        return sum(self.misplaced_items.values())
    
    def get_item_breakdown(self) -> List[Dict[str, Any]]:
        """Get detailed breakdown for each expected item type"""
        breakdown = []
        all_item_types = set(self.expected_items.keys()) | set(self.detected_items.keys()) | set(self.misplaced_items.keys())
        
        for item_type in all_item_types:
            expected = self.expected_items.get(item_type, 0)
            detected = self.detected_items.get(item_type, 0)
            misplaced = self.misplaced_items.get(item_type, 0)
            status = self.item_statuses.get(item_type, "Unknown")
            
            # Determine if item is truly sold out vs just misplaced
            available_total = detected + misplaced
            if expected > 0:
                if available_total == 0:
                    availability_status = "Sold Out"
                elif detected == 0 and misplaced > 0:
                    availability_status = "Misplaced Only"
                elif detected < expected and available_total >= expected:
                    availability_status = "Partially Misplaced"
                else:
                    availability_status = "Available"
            else:
                availability_status = "Not Expected"
            
            breakdown.append({
                'item_type': item_type,
                'expected': expected,
                'detected_in_section': detected,
                'found_elsewhere': misplaced,
                'total_available': available_total,
                'status': status,
                'availability_status': availability_status,
                'shortage': max(0, expected - available_total),
                'surplus': max(0, available_total - expected)
            })
        
        return breakdown
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'section_id': self.section_id,
            'section_name': self.section_name,
            'total_expected': self.total_expected,
            'total_detected': self.total_detected,
            'total_misplaced': self.total_misplaced,
            'total_available': self.total_detected + self.total_misplaced,
            'status': self.status,
            'item_breakdown': self.get_item_breakdown()
        }

@dataclass
class ItemAvailabilityStatus:
    """Represents the availability status of a specific item type across all sections"""
    item_type: str
    total_expected: int
    total_detected: int
    correctly_placed: int
    misplaced: int
    sections_with_shortages: List[str]
    sections_with_surplus: List[str]
    overall_status: str  # "Available", "Shortage", "Surplus", "Sold Out"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'item_type': self.item_type,
            'total_expected': self.total_expected,
            'total_detected': self.total_detected,
            'correctly_placed': self.correctly_placed,
            'misplaced': self.misplaced,
            'total_available': self.total_detected,
            'shortage': max(0, self.total_expected - self.total_detected),
            'surplus': max(0, self.total_detected - self.total_expected),
            'overall_status': self.overall_status,
            'sections_with_shortages': ', '.join(self.sections_with_shortages),
            'sections_with_surplus': ', '.join(self.sections_with_surplus)
        }

@dataclass
class Task:
    """Represents a task that needs to be completed"""
    task_id: str
    description: str
    section_id: str
    priority: str  # High, Medium, Low
    task_type: str  # "Restock", "Remove", "Relocate", "Check"
    estimated_time: int  # in minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'task_id': self.task_id,
            'description': self.description,
            'section_id': self.section_id,
            'priority': self.priority,
            'task_type': self.task_type,
            'estimated_time': self.estimated_time
        }

@dataclass
class AnalysisResults:
    """Contains all results from planogram analysis"""
    detected_items: pd.DataFrame
    misplaced_items: pd.DataFrame
    inventory_status: pd.DataFrame
    detailed_inventory_status: pd.DataFrame
    item_availability_status: pd.DataFrame
    tasks: pd.DataFrame
    annotated_image: Optional[Image.Image]
    
    @classmethod
    def create_empty(cls) -> 'AnalysisResults':
        """Create empty results structure"""
        return cls(
            detected_items=pd.DataFrame(),
            misplaced_items=pd.DataFrame(),
            inventory_status=pd.DataFrame(),
            detailed_inventory_status=pd.DataFrame(),
            item_availability_status=pd.DataFrame(),
            tasks=pd.DataFrame(),
            annotated_image=None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'detected_items': self.detected_items,
            'misplaced_items': self.misplaced_items,
            'inventory_status': self.inventory_status,
            'detailed_inventory_status': self.detailed_inventory_status,
            'item_availability_status': self.item_availability_status,
            'tasks': self.tasks,
            'annotated_image': self.annotated_image
        }

class PlanogramMetrics:
    """Utility class for calculating planogram metrics"""
    
    @staticmethod
    def calculate_compliance_score(
        expected_sections: List[PlanogramSection],
        detected_items: List[DetectedItem],
        misplaced_items: List[MisplacedItem]
    ) -> float:
        """Calculate overall compliance score (0-100)"""
        if not expected_sections:
            return 0.0
        
        total_expected = sum(section.expected_count for section in expected_sections)
        total_detected = len(detected_items)
        total_misplaced = len(misplaced_items)
        
        if total_expected == 0:
            return 100.0 if total_detected == 0 else 0.0
        
        # Score based on correct placement and inventory accuracy
        placement_score = max(0, (total_detected - total_misplaced) / total_detected * 100) if total_detected > 0 else 0
        inventory_score = min(100, total_detected / total_expected * 100)
        
        # Weighted average
        return (placement_score * 0.6 + inventory_score * 0.4)
    
    @staticmethod
    def determine_inventory_status(expected: int, detected: int) -> str:
        """Determine inventory status based on expected vs detected counts"""
        if detected == 0:
            return "Out of Stock"
        elif detected < expected * 0.5:
            return "Low Stock"
        elif detected > expected * 1.2:
            return "Overstock"
        else:
            return "In Stock" 