import numpy as np
import onnxruntime
import cv2
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
from utils import setup_logging

logger = setup_logging()

# COCO dataset class names
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
    'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

@dataclass
class DetectionResult:
    """Data model for object detection results"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)

class InferenceEngine:
    """Handles ML model inference for object detection"""
    
    def __init__(self, model_path: str = "../model/yolov8x.onnx"):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the ONNX model file
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        # Initialize ONNX Runtime session
        self.session = onnxruntime.InferenceSession(
            str(self.model_path),
            providers=['CPUExecutionProvider']
        )
        
        # Get model metadata
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        logger.info(f"Model loaded successfully from {model_path}")
        
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image as numpy array (H,W,C) in BGR format
            
        Returns:
            Preprocessed image ready for inference
        """
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get dimensions from model input shape
        input_height, input_width = 640, 640  # YOLOv8 default input size
        
        # Calculate scaling factors
        scale = min(input_height / image.shape[0], input_width / image.shape[1])
        new_height = int(image.shape[0] * scale)
        new_width = int(image.shape[1] * scale)
        
        # Resize image maintaining aspect ratio
        resized = cv2.resize(image, (new_width, new_height))
        
        # Create black canvas of target size
        canvas = np.zeros((input_height, input_width, 3), dtype=np.uint8)
        
        # Calculate offset to center the image
        y_offset = (input_height - new_height) // 2
        x_offset = (input_width - new_width) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
        
        # Normalize pixel values
        preprocessed = canvas.astype(np.float32) / 255.0
        
        # Transpose from HWC to CHW format
        preprocessed = preprocessed.transpose(2, 0, 1)
        
        # Add batch dimension
        preprocessed = np.expand_dims(preprocessed, axis=0)
        
        return preprocessed
        
    def run_inference(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Run inference on an image and return detection results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of DetectionResult objects containing inference results
        """
        try:
            # Preprocess image
            processed_image = self.preprocess(image)
            
            # Run inference
            outputs = self.session.run(None, {self.input_name: processed_image})

            # Post-process results
            detections = self.postprocess(outputs[0])
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            raise
            
    def postprocess(self, output: np.ndarray) -> List[DetectionResult]:
        """
        Post-process model output to get detection results.
        
        Args:
            output: Raw model output
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        
        # YOLOv8 output format: [batch, num_classes+4, num_anchors]
        # First 4 values are [cx, cy, w, h], rest are class probabilities
        predictions = output[0]  # Take first batch
        
        num_classes = predictions.shape[0] - 4  # Subtract box coordinates
        scores = predictions[4:]  # Class scores
        boxes = predictions[:4]   # Box coordinates
        
        # Get class indices and scores
        class_scores = np.max(scores, axis=0)  # Max score for each detection
        class_ids = np.argmax(scores, axis=0)   # Class ID with max score
        
        # Filter by confidence threshold
        mask = class_scores > 0.25
        
        if np.any(mask):
            # Get filtered detections
            filtered_boxes = boxes[:, mask]
            filtered_scores = class_scores[mask]
            filtered_class_ids = class_ids[mask]
            
            # Convert centerx, centery, width, height to x1,y1,x2,y2
            x = filtered_boxes[0]  # center x
            y = filtered_boxes[1]  # center y
            w = filtered_boxes[2]  # width
            h = filtered_boxes[3]  # height
            
            # Calculate corners
            x1 = x - w/2  # top left x
            y1 = y - h/2  # top left y
            x2 = x + w/2  # bottom right x
            y2 = y + h/2  # bottom right y
            
            # Create detection results
            for i in range(len(filtered_scores)):
                class_id = int(filtered_class_ids[i])
                class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"unknown_{class_id}"
                
                # Clip coordinates to 0-1 range
                bbox = (
                    float(max(0.0, min(1.0, x1[i]))),
                    float(max(0.0, min(1.0, y1[i]))),
                    float(max(0.0, min(1.0, x2[i]))),
                    float(max(0.0, min(1.0, y2[i])))
                )
                
                results.append(DetectionResult(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(filtered_scores[i]),
                    bbox=bbox
                ))
                
                logger.debug(f"Detection: {class_name} (conf: {filtered_scores[i]:.2f}) at bbox: {bbox}")
        
        logger.info(f"Found {len(results)} detections above confidence threshold")
        return results
