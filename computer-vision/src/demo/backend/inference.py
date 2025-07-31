import os
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple
from ultralytics import YOLO

class ModelInference:
    """Model inference layer for planogram analysis"""
    
    
    def __init__(self):
        """
        Initialize model inference layer
        
        Args:
            weights_path: Path to model weights file (optional, uses default if not provided)
        """
        self.model = None
        # Use relative path from current file location (cross-platform compatible)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        demo_dir = os.path.dirname(current_dir)  # Go up one level to demo directory
        self.weights_path = os.path.join(demo_dir, "weights", "pick-instance-seg-v11-1.3-L.pt")
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the model from weights file"""
        try:
            # Load the model using Ultralytics
            self.model = YOLO(self.weights_path)
            print(f"✅ Model loaded successfully from: {self.weights_path}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def infer(self, image: Image.Image, confidence_threshold: float = 0.5, 
              iou_threshold: float = 0.4) -> List[Dict[str, Any]]:
        """
        Run inference on the provided image with segmentation masks
        
        Args:
            image: PIL Image to analyze
            confidence_threshold: Minimum confidence score for detections
            iou_threshold: IoU threshold for non-maximum suppression
            
        Returns:
            List of detection dictionaries with format:
            {
                'class_id': int,
                'class_name': str,
                'confidence': float,
                'bbox': [x1, y1, x2, y2],
                'mask': numpy.ndarray,  # Binary mask (height, width)
                'mask_polygon': List[List[float]]  # Polygon coordinates [[x1, y1], [x2, y2], ...]
            }
        """
        if self.model is None:
            print("⚠️ Model not loaded, returning empty results")
            return []
        
        try:
            # Run inference using Ultralytics
            results = self.model(image, 
                               conf=confidence_threshold,
                               iou=iou_threshold,
                               verbose=False)
            
            # Process results
            detections = []
            
            # Process the first result (single image)
            if len(results) > 0:
                result = results[0]
                
                # Get bounding boxes, confidences, and classes
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2 format
                    confidences = result.boxes.conf.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy()
                    
                    # Get class names
                    names = result.names
                    
                    # Get segmentation masks if available
                    masks_data = None
                    masks_xy = None
                    if result.masks is not None:
                        try:
                            masks_data = result.masks.data.cpu().numpy()  # Binary masks
                            masks_xy = result.masks.xy  # Polygon coordinates
                            print(f"🎭 Found {len(masks_data)} segmentation masks")
                        except Exception as e:
                            print(f"⚠️ Error processing masks: {e}")
                            masks_data = None
                            masks_xy = None
                    
                    # Create detection dictionaries
                    for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                        class_id = int(cls)
                        class_name = names.get(class_id, f'unknown_class_{class_id}')
                        
                        detection = {
                            'class_id': class_id,
                            'class_name': class_name,
                            'confidence': float(conf),
                            'bbox': [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
                        }
                        
                        # Add mask data if available
                        if masks_data is not None and i < len(masks_data):
                            try:
                                # Binary mask
                                detection['mask'] = masks_data[i].astype(np.uint8)
                                
                                # Polygon coordinates
                                if masks_xy is not None and i < len(masks_xy):
                                    # Convert polygon to list of [x, y] coordinates
                                    polygon = masks_xy[i]
                                    # Handle both tensor and numpy array cases
                                    if hasattr(polygon, 'cpu'):
                                        polygon = polygon.cpu().numpy()
                                    elif not isinstance(polygon, np.ndarray):
                                        polygon = np.array(polygon)
                                    detection['mask_polygon'] = polygon.tolist()
                                else:
                                    detection['mask_polygon'] = []
                                
                                print(f"  📐 Instance {i}: mask shape {detection['mask'].shape}, "
                                      f"polygon points: {len(detection['mask_polygon'])}")
                            except Exception as e:
                                print(f"⚠️ Error processing mask for instance {i}: {e}")
                                detection['mask'] = None
                                detection['mask_polygon'] = []
                        else:
                            detection['mask'] = None
                            detection['mask_polygon'] = []
                        
                        detections.append(detection)
            
            print(f"🔍 Inference completed: {len(detections)} detections found")
            
            # Print detections for debugging
            if detections:
                print("📋 Detections found:")
                for i, detection in enumerate(detections):
                    mask_info = ""
                    if detection['mask'] is not None:
                        mask_info = f", Mask: {detection['mask'].shape}, Polygon points: {len(detection['mask_polygon'])}"
                    
                    print(f"  {i+1}. {detection['class_name']} (ID: {detection['class_id']}) - "
                          f"Confidence: {detection['confidence']:.3f}, "
                          f"BBox: {detection['bbox']}{mask_info}")
            else:
                print("📋 No detections found")
                
            return detections
            
        except Exception as e:
            print(f"❌ Error during inference: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if self.model is None:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'weights_path': self.weights_path,
            'model_type': 'Ultralytics YOLO'
        }
        
        # Add class names if available
        if hasattr(self.model, 'names'):
            info['classes'] = self.model.names
        
        return info
    
    def is_ready(self) -> bool:
        """Check if the model is loaded and ready for inference"""
        return self.model is not None
    
    def extract_masked_object(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Extract object pixels using the segmentation mask
        
        Args:
            image: Original image as numpy array (H, W, C)
            mask: Binary mask as numpy array (H, W)
            
        Returns:
            Masked object as numpy array with same shape as input image
        """
        if mask is None:
            return image
        
        # Ensure mask is the right shape and type
        mask = mask.astype(np.uint8)
        
        # Apply mask to image (multiply each channel)
        masked_object = image * mask[:, :, np.newaxis]
        
        return masked_object
    
    def calculate_mask_area(self, mask: np.ndarray) -> float:
        """
        Calculate the area of a segmentation mask
        
        Args:
            mask: Binary mask as numpy array
            
        Returns:
            Area in pixels
        """
        if mask is None:
            return 0.0
        
        return float(np.sum(mask))
    
    def get_mask_perimeter(self, mask_polygon: List[List[float]]) -> float:
        """
        Calculate the perimeter of a mask using polygon coordinates
        
        Args:
            mask_polygon: List of [x, y] coordinates
            
        Returns:
            Perimeter in pixels
        """
        if not mask_polygon or len(mask_polygon) < 3:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(mask_polygon)):
            p1 = mask_polygon[i]
            p2 = mask_polygon[(i + 1) % len(mask_polygon)]
            
            # Calculate Euclidean distance
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            perimeter += np.sqrt(dx*dx + dy*dy)
        
        return perimeter 