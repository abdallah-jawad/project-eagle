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
            image: Input image as numpy array (H,W,C)
            
        Returns:
            Preprocessed image ready for inference
        """
        # Resize image to model input size
        input_height, input_width = self.input_shape[2:]
        image = cv2.resize(image, (input_width, input_height))
        
        # Normalize pixel values to [0,1]
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension and ensure NCHW format
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, 0)
        
        return image
        
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
        
        # YOLOv8 output format: [batch, num_detections, 6]
        # Each detection is [x1, y1, x2, y2, confidence, class_id]
        for detection in output[0]:  # Take first batch
            if len(detection) >= 6:  # Ensure we have all required values
                # Extract values and convert to Python scalars
                x1, y1, x2, y2 = map(float, detection[:4])
                confidence = float(detection[4])
                class_id = int(detection[5])
                
                # Get class name
                class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"unknown_{class_id}"
                
                # Only add detections with confidence above threshold
                if confidence > 0.25:  # You can adjust this threshold
                    results.append(DetectionResult(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2)
                    ))
            
        return results
