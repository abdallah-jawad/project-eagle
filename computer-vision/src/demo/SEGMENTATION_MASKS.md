# Segmentation Masks in Planogram Vision

This document describes the segmentation mask functionality that has been added to the planogram vision system.

## Overview

The inference system now supports segmentation masks in addition to bounding box detections. This provides more precise object boundaries and enables advanced analysis capabilities.

## What's New

### 1. Enhanced Inference Results

The `infer()` function now returns additional mask data for each detection:

```python
detection = {
    'class_id': int,
    'class_name': str,
    'confidence': float,
    'bbox': [x1, y1, x2, y2],
    'mask': numpy.ndarray,  # Binary mask (height, width)
    'mask_polygon': List[List[float]]  # Polygon coordinates [[x1, y1], [x2, y2], ...]
}
```

### 2. Updated DetectedItem Model

The `DetectedItem` class now includes mask data:

```python
@dataclass
class DetectedItem:
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    section_id: Optional[str] = None
    mask: Optional[np.ndarray] = None  # Binary segmentation mask
    mask_polygon: Optional[List[List[float]]] = None  # Polygon coordinates
```

### 3. New Helper Methods

The `ModelInference` class now includes utility methods for mask analysis:

- `extract_masked_object()`: Extract object pixels using the mask
- `calculate_mask_area()`: Calculate mask area in pixels
- `get_mask_perimeter()`: Calculate mask perimeter using polygon coordinates

## Usage Examples

### Basic Usage

```python
from backend.inference import ModelInference

# Initialize model
inference = ModelInference()

# Run inference
detections = inference.infer(image, confidence_threshold=0.5)

# Process results
for detection in detections:
    print(f"Class: {detection['class_name']}")
    print(f"Confidence: {detection['confidence']:.3f}")
    
    if detection['mask'] is not None:
        mask = detection['mask']
        polygon = detection['mask_polygon']
        
        print(f"Mask shape: {mask.shape}")
        print(f"Polygon points: {len(polygon)}")
        print(f"Mask area: {np.sum(mask)} pixels")
```

### Mask Analysis

```python
# Calculate mask metrics
for detection in detections:
    if detection['mask'] is not None:
        mask = detection['mask']
        polygon = detection['mask_polygon']
        
        # Calculate area
        area = inference.calculate_mask_area(mask)
        print(f"Area: {area:.1f} pixels")
        
        # Calculate perimeter
        perimeter = inference.get_mask_perimeter(polygon)
        print(f"Perimeter: {perimeter:.1f} pixels")
        
        # Extract masked object
        image_array = np.array(image)
        masked_object = inference.extract_masked_object(image_array, mask)
        print(f"Masked object shape: {masked_object.shape}")
```

### Using with Planogram Analyzer

```python
from backend.planogram_analyzer import PlanogramAnalyzer

# Initialize analyzer
analyzer = PlanogramAnalyzer()
analyzer.load_planogram_config('your_config.json')

# Analyze image (now includes masks!)
results = analyzer.analyze_image(image)

# Access detected items with masks
detected_items_df = results['detected_items']

for _, item in detected_items_df.iterrows():
    print(f"Item: {item['class_name']}")
    print(f"Has mask: {item['has_mask']}")
    print(f"Mask area: {item['mask_area']:.1f}")
    print(f"Mask perimeter: {item['mask_perimeter']:.1f}")
```

## Data Structure Details

### Binary Mask

The `mask` field contains a binary numpy array where:
- `1` indicates object pixels
- `0` indicates background pixels
- Shape: `(height, width)`
- Data type: `uint8`

### Polygon Coordinates

The `mask_polygon` field contains a list of `[x, y]` coordinate pairs that define the object boundary:
- Format: `[[x1, y1], [x2, y2], [x3, y3], ...]`
- Points are ordered clockwise around the object
- Can be used for drawing outlines or calculating perimeter

## Benefits

1. **Precise Boundaries**: Masks provide exact object boundaries instead of rectangular bounding boxes
2. **Better Overlap Detection**: More accurate detection of overlapping objects
3. **Area Calculations**: Precise area measurements for each detected object
4. **Improved Visualizations**: Better visual representations with object outlines and mask overlays
5. **Advanced Analysis**: Enables more sophisticated geometric analysis
6. **Enhanced Annotations**: Automatic drawing of segmentation masks on annotated images

## Annotation Features

The system now automatically draws segmentation masks on annotated images:

### Visual Elements
- **Mask Overlays**: Semi-transparent colored overlays showing object boundaries
- **Polygon Outlines**: Precise object boundaries drawn as colored polygons
- **Color Coding**: 
  - Green masks for correctly placed items
  - Red masks for misplaced items
  - Blue outlines for planogram sections
- **Enhanced Labels**: Include confidence scores and mask area information
- **Background Labels**: White backgrounds on labels for better visibility

### Drawing Methods
1. **Polygon-based**: Uses polygon coordinates for efficient drawing
2. **Binary Mask Overlay**: Fallback method using binary mask data
3. **Bounding Box Fallback**: Automatic fallback if mask drawing fails

### Example Usage
```python
# The annotation is automatically created during analysis
results = analyzer.analyze_image(image)
annotated_image = results['annotated_image']

# Or manually create annotations
annotated_image = analyzer._create_annotated_image(
    image, detected_items, misplaced_items
)
```

## Testing

Run the test script to verify the functionality:

```bash
cd computer-vision/src/demo
python test_segmentation.py
```

Or run the example script:

```bash
python segmentation_example.py
```

## Requirements

The segmentation mask functionality requires:
- Ultralytics YOLO model with segmentation capabilities
- NumPy for array operations
- PIL for image processing
- Matplotlib for visualization (optional)

## Model Compatibility

This functionality works with YOLO models that support instance segmentation, such as:
- YOLOv8-seg models
- Custom trained segmentation models
- Other Ultralytics-compatible segmentation models

## Performance Considerations

- Mask processing adds minimal overhead to inference
- Binary masks are memory-efficient
- Polygon coordinates provide compact boundary representation
- All operations are optimized for numpy arrays 