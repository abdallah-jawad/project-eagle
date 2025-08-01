import numpy as np
import onnxruntime
import cv2
from pathlib import Path
from typing import List, Tuple
from utils import setup_logging
from models.detection_result import DetectionResult
from constants.coco_classes import COCO_CLASSES

logger = setup_logging()

class InferenceEngine:
    """Handles ML model inference for object detection"""
    
    def __init__(self, model_path: str = "../model/yolov8x.onnx", use_gpu: bool = True):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the ONNX model file
            use_gpu: Whether to use GPU for inference. If False, will use CPU.
                   If True but GPU is not available, will fall back to CPU.
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        # Set up providers based on use_gpu parameter
        if use_gpu:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            logger.info("Attempting to use CUDA for GPU acceleration")
            self.device = "GPU"
        else:
            providers = ['CPUExecutionProvider']
            self.device = "CPU"
            
        try:
            # Initialize ONNX Runtime session
            self.session = onnxruntime.InferenceSession(
                str(self.model_path),
                providers=providers
            )
            
            # Log which provider is being used
            actual_provider = self.session.get_providers()[0]
            logger.info(f"Using provider: {actual_provider}")
            logger.info(f"Inference device: {'GPU' if 'CUDA' in actual_provider else 'CPU'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize inference session: {str(e)}")
            if use_gpu:
                logger.warning("GPU initialization failed, falling back to CPU")
                self.session = onnxruntime.InferenceSession(
                    str(self.model_path),
                    providers=['CPUExecutionProvider']
                )
                self.device = "CPU"
            else:
                raise
        
        # Get model metadata
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        logger.info(f"Model loaded successfully from {model_path}")
        
    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, int, int, float, int, int]:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image as numpy array (H,W,C) in BGR format
            
        Returns:
            Tuple containing:
            - Preprocessed image ready for inference
            - Original image height
            - Original image width
            - Scale used for resizing
            - x_offset (padding left)
            - y_offset (padding top)
        """
        original_height, original_width = image.shape[:2]
        input_height, input_width = 640, 640
        scale = min(input_height / original_height, input_width / original_width)
        new_height = int(original_height * scale)
        new_width = int(original_width * scale)
        resized = cv2.resize(image, (new_width, new_height))
        canvas = np.zeros((input_height, input_width, 3), dtype=np.uint8)
        y_offset = (input_height - new_height) // 2
        x_offset = (input_width - new_width) // 2
        canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
        preprocessed = canvas.astype(np.float32) / 255.0
        preprocessed = preprocessed.transpose(2, 0, 1)
        preprocessed = np.expand_dims(preprocessed, axis=0)
        return preprocessed, original_height, original_width, scale, x_offset, y_offset
        
    def run_inference(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Run inference on an image and return detection results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of DetectionResult objects containing inference results
        """
        try:
            # Preprocess image and get original dimensions and letterbox info
            processed_image, original_height, original_width, scale, x_offset, y_offset = self.preprocess(image)
            
            # Run inference
            outputs = self.session.run(None, {self.input_name: processed_image})

            # Post-process results
            detections = self.postprocess(outputs[0], original_height, original_width, scale, x_offset, y_offset)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            raise
            
    def postprocess(self, output: np.ndarray, original_height: int, original_width: int, scale: float, x_offset: int, y_offset: int) -> List[DetectionResult]:
        """
        Post-process model output to get detection results.
        
        Args:
            output: Raw model output
            original_height: Original image height
            original_width: Original image width
            scale: Scale used for resizing
            x_offset: Padding left
            y_offset: Padding top
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        
        # YOLOv8 output format: [batch, num_classes+4, num_anchors]
        # First 4 values are [cx, cy, w, h], rest are class probabilities
        predictions = output[0]  # Take first batch
        
        # Reshape predictions to [num_anchors, num_classes+4]
        predictions = predictions.T
        
        # Extract boxes and scores
        boxes = predictions[:, :4]  # [num_anchors, 4] - (cx, cy, w, h)
        scores = predictions[:, 4:]  # [num_anchors, num_classes]
        
        # Get class indices and scores
        class_scores = np.max(scores, axis=1)  # Max score for each detection
        class_ids = np.argmax(scores, axis=1)   # Class ID with max score
        
        # Filter by confidence threshold
        mask = class_scores > 0.25
        
        if np.any(mask):
            # Get filtered detections
            filtered_boxes = boxes[mask]
            filtered_scores = class_scores[mask]
            filtered_class_ids = class_ids[mask]
            
            # Convert centerx, centery, width, height to x1,y1,x2,y2
            x = filtered_boxes[:, 0]  # center x
            y = filtered_boxes[:, 1]  # center y
            w = filtered_boxes[:, 2]  # width
            h = filtered_boxes[:, 3]  # height
            
            # Calculate corners
            x1 = x - w/2  # top left x
            y1 = y - h/2  # top left y
            x2 = x + w/2  # bottom right x
            y2 = y + h/2  # bottom right y
            
            # Remove padding and scale back to original image size
            x1 = (x1 - x_offset) / scale
            y1 = (y1 - y_offset) / scale
            x2 = (x2 - x_offset) / scale
            y2 = (y2 - y_offset) / scale
            
            # Clip to image size
            x1 = np.clip(x1, 0, original_width)
            y1 = np.clip(y1, 0, original_height)
            x2 = np.clip(x2, 0, original_width)
            y2 = np.clip(y2, 0, original_height)
            
            # Create detection results
            for i in range(len(filtered_scores)):
                class_id = int(filtered_class_ids[i])
                class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"unknown_{class_id}"
                
                # Use pixel coordinates directly
                bbox = (
                    float(x1[i]),
                    float(y1[i]),
                    float(x2[i]),
                    float(y2[i])
                )
                
                results.append(DetectionResult(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(filtered_scores[i]),
                    bbox=bbox
                ))
        
        return results
