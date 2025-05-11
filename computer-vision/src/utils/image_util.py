import cv2
from typing import List
from .inference import DetectionResult

def draw_detections(image: cv2.Mat, detections: List[DetectionResult]) -> cv2.Mat:
    """
    Draw bounding boxes and labels for detections on the image.
    
    Args:
        image: Input image as OpenCV Mat
        detections: List of DetectionResult objects containing detection information
        
    Returns:
        Image with drawn bounding boxes and labels
    """
    # Create a copy of the image for visualization
    vis_image = image.copy()
    
    # Colors for different classes
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
    
    # Draw each detection
    for i, detection in enumerate(detections):
        # Get bounding box coordinates (pixel values)
        x1, y1, x2, y2 = detection.bbox
        
        # Convert to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Get color for this class
        color = colors[detection.class_id % len(colors)]
        
        # Draw rectangle
        cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
        
        # Add label with class name and confidence
        label = f"{detection.class_name} ({detection.confidence:.2f})"
        label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        y1_label = max(y1, label_size[1])
        
        # Draw label background
        cv2.rectangle(vis_image, 
                     (x1, y1_label - label_size[1] - baseline),
                     (x1 + label_size[0], y1_label + baseline),
                     color, cv2.FILLED)
        
        # Draw label text
        cv2.putText(vis_image, label, (x1, y1_label),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    return vis_image
