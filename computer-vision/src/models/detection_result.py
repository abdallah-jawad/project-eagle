from dataclasses import dataclass
from typing import Tuple

@dataclass
class DetectionResult:
    """Data model for object detection results
    
    Attributes:
        class_id: Integer ID of the detected class
        class_name: String name of the detected class
        confidence: Float confidence score of the detection (0-1)
        bbox: Tuple of (x1, y1, x2, y2) coordinates representing the bounding box
    """
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2) 