# 🎯 Planogram Configuration Creator Guide

This guide explains how to use the new planogram configuration creator in the demo application.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo Application
```bash
streamlit run app.py
```

### 3. Access the Configuration Creator
- Open the demo application in your browser
- Click on the **"🎯 Configuration"** tab
- You'll see the planogram configuration creator interface

## 📋 Step-by-Step Process

### Step 1: Upload Planogram Image
1. Click **"Choose a planogram image"** 
2. Select an image file (PNG, JPG, JPEG)
3. The image will be displayed for reference

### Step 2: Draw Sections
1. **Interactive Drawing Interface:**
   - Use coordinate inputs to define section boundaries
   - Preview the selected area in real-time
   - Each section gets a unique ID and coordinates

2. **Section Configuration:**
   - **Section ID:** Unique identifier (e.g., "WATER_SECTION")
   - **Section Name:** Human-readable name (e.g., "Water Bottles")
   - **Coordinates:** X1, Y1, X2, Y2 defining the section boundaries
   - **Expected Items:** Select from available item types
   - **Expected Count:** Number of items that should be in this section
   - **Priority:** High, Medium, or Low importance

3. **Available Item Types:**
   - `bottled_drinks` - Bottled beverages
   - `canned_drinks` - Canned beverages
   - `large_plates` - Large serving plates
   - `salads_bowls` - Salad bowls and containers
   - `sandwiches` - Sandwiches and boxed meals
   - `small_plates` - Small serving plates
   - `wraps` - Wraps and roll-ups
   - `yogurt_cups_large` - Large yogurt cups
   - `yogurt_cups_small` - Small yogurt cups

### Step 3: Generate Configuration
1. Fill in configuration details:
   - **Configuration Name:** Descriptive name for your planogram
   - **Store ID:** Unique store identifier
   - **Description:** Optional description

2. Click **"Generate Configuration"**
3. The system will:
   - Create a JSON configuration file
   - Save the planogram image
   - Display a preview of the configuration

## 📁 Generated Files

### Configuration File
- **Location:** `config/planograms/{store_id}_custom.json`
- **Format:** JSON with metadata and section definitions
- **Example:**
```json
{
  "metadata": {
    "name": "Custom Store Layout",
    "store_id": "STORE_CUSTOM",
    "created_date": "2024-01-01",
    "version": "1.0",
    "description": "Custom planogram configuration"
  },
  "planogram_image_path": "config/images/store_custom_planogram.jpg",
  "sections": [
    {
      "section_id": "WATER_SECTION",
      "name": "Water Bottles",
      "expected_items": ["bottled_drinks"],
      "expected_count": 4,
      "position": {"x1": 54, "y1": 55, "x2": 275, "y2": 357},
      "priority": "Medium"
    }
  ]
}
```

### Planogram Image
- **Location:** `config/images/{store_id}_planogram.jpg`
- **Format:** JPEG image of the uploaded planogram
- **Usage:** Reference image for the configuration

## 🔧 Using Your Configuration

### In the Analysis Tab
1. Go to the **"🔍 Analysis"** tab
2. Select your new configuration from the dropdown
3. Upload a store image to analyze
4. Compare against your custom planogram

### Configuration Management
- All configurations are automatically listed in the analysis tab
- You can create multiple configurations for different stores
- Each configuration is saved with a unique store ID

## 🎨 Drawing Tips

### Coordinate System
- **Origin:** Top-left corner (0, 0)
- **X-axis:** Horizontal (left to right)
- **Y-axis:** Vertical (top to bottom)
- **Units:** Pixels

### Section Planning
1. **Measure your image:** Note the image dimensions
2. **Plan sections:** Sketch out section boundaries
3. **Use preview:** Always preview before adding sections
4. **Test coordinates:** Start with small sections to test

### Best Practices
- **Unique IDs:** Use descriptive, unique section IDs
- **Realistic counts:** Set expected counts based on actual capacity
- **Priority levels:** Use priority to indicate importance
- **Item selection:** Select all relevant item types for each section

## 🐛 Troubleshooting

### Common Issues

**"No planogram configurations found"**
- Make sure you've created at least one configuration
- Check that the `config/planograms/` directory exists

**"Error saving configuration"**
- Ensure you have write permissions in the demo directory
- Check that all required fields are filled

**"Invalid coordinates"**
- Make sure X2 > X1 and Y2 > Y1
- Ensure coordinates are within image boundaries

**"Configuration not appearing in analysis"**
- Refresh the page after creating a configuration
- Check that the configuration file was saved correctly

### File Structure
```
computer-vision/src/demo/
├── app.py                          # Main demo application
├── backend/
│   ├── streamlit_drawer.py         # Drawing interface
│   ├── config.py                   # Configuration management
│   └── ...
├── config/
│   ├── planograms/                 # Configuration files
│   │   ├── sample_store.json
│   │   └── {store_id}_custom.json
│   └── images/                     # Planogram images
│       ├── planogram_demo.jpeg
│       └── {store_id}_planogram.jpg
└── requirements.txt                # Dependencies
```

## 🎯 Example Workflow

1. **Upload Image:** Upload a refrigerated display case image
2. **Draw Sections:**
   - Section 1: Water bottles (top shelf)
   - Section 2: Canned drinks (middle shelf)
   - Section 3: Yogurt cups (bottom shelf)
3. **Configure Items:**
   - Water section: `bottled_drinks`, count: 4
   - Canned section: `canned_drinks`, count: 6
   - Yogurt section: `yogurt_cups_large`, count: 8
4. **Generate:** Save as "Refrigerated Case Layout"
5. **Analyze:** Use the configuration to analyze store compliance

## 🔄 Integration with Analysis

The planogram configuration creator integrates seamlessly with the analysis system:

- **Automatic Loading:** Configurations appear in the analysis dropdown
- **Visual Comparison:** Compare uploaded images against your planogram
- **Compliance Scoring:** Get detailed compliance analysis
- **Task Generation:** Automatic task recommendations based on your configuration

This creates a complete workflow from planogram definition to compliance analysis! 