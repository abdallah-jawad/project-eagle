# 🎯 Interactive Section Drawing Tool

An interactive utility for visually drawing planogram section boundaries and automatically generating configuration files.

## 🚀 Quick Start

### 1. Install Dependencies (if needed)
```bash
pip install matplotlib numpy
# These should already be in requirements.txt
```

### 2. Run the Tool
```bash
python draw_sections.py
# Uses default image: config/images/planogram_demo.jpeg

# Or specify custom image:
python draw_sections.py path/to/your/image.jpg
```

## 🎮 How to Use

### **Interactive Interface**
1. **Draw Sections**: Click and drag to create rectangular boundaries
2. **Visual Labels**: Each section gets numbered automatically (#1, #2, etc.)
3. **Real-time Coordinates**: See coordinates printed as you draw

### **Control Buttons**
- **🎯 Finish Drawing**: Display summary of all drawn sections
- **💾 Save Config**: Convert sections to JSON configuration file
- **🧹 Clear All**: Remove all drawn sections
- **↶ Undo Last**: Remove the most recent section

### **Drawing Process**
1. Load your planogram image
2. Click and drag to draw section boundaries
3. Each section gets a unique ID and coordinates
4. Click "Finish Drawing" to see summary
5. Click "Save Config" to create configuration file

## 📊 Features

### **Automatic Normalization**
- **Resizes images** to 1080×1440 (3:4 aspect ratio)
- **Maintains aspect ratio** with white padding if needed
- **Consistent coordinates** regardless of input image size

### **Interactive Drawing**
- **Visual feedback** while drawing rectangles
- **Numbered labels** for easy identification
- **Real-time coordinate display** in console
- **Minimum size filtering** (ignores tiny rectangles)

### **Configuration Generation**
- **Automatic JSON creation** with proper schema
- **Interactive metadata entry** (store name, ID, etc.)
- **Section configuration** (name, items, count, priority)
- **Ready-to-use config files** for planogram demo

## 🔧 Generated Configuration Format

```json
{
  "metadata": {
    "name": "Your Store Name",
    "store_id": "YOUR_STORE_ID",
    "created_date": "2024-01-01",
    "version": "1.0",
    "description": "Custom planogram with X sections"
  },
  "planogram_image_path": "config/images/your_image.jpg",
  "sections": [
    {
      "section_id": "SECTION_01",
      "name": "Section Name",
      "expected_items": ["item1", "item2"],
      "expected_count": 5,
      "position": {
        "x1": 100,
        "y1": 200,
        "x2": 300,
        "y2": 400
      },
      "priority": "High"
    }
  ]
}
```

## 📝 Configuration Process

When you click "Save Config", the tool will prompt for:

### **Store Information**
- **Store Name**: Descriptive name for your store
- **Store ID**: Unique identifier (used for filename)

### **For Each Section**
- **Section Name**: Descriptive name (e.g., "Water Bottles")
- **Expected Items**: Comma-separated list of item types
- **Expected Count**: Number of items expected in this section
- **Priority**: High/Medium/Low priority level

## 💡 Tips & Best Practices

### **Drawing Sections**
- **Start from top-left** and work systematically
- **Draw tight boundaries** around product areas
- **Avoid overlapping** sections when possible
- **Use consistent section sizes** for similar product types

### **Section Organization**
- **Group similar items** in adjacent sections
- **Consider shelf layout** (top, middle, bottom)
- **Match business priorities** with priority levels
- **Use descriptive names** for easy identification

### **Image Preparation**
- **Good lighting** for clear visibility
- **Straight angles** for easier boundary drawing
- **High resolution** for better precision
- **Clear product visibility** for accurate sectioning

## 📂 Output Files

Generated configurations are saved to:
```
config/planograms/{store_id}_custom.json
```

You can then use these files directly in your planogram demo!

## 🛠️ Troubleshooting

### **Import Errors**
```
pip install matplotlib numpy
```

### **Image Not Found**
- Check image path is correct
- Ensure image file exists
- Supported formats: JPG, JPEG, PNG

### **Small/Missing Sections**
- Draw larger rectangles (minimum 5×5 pixels)
- Click "Undo Last" to remove unwanted sections
- Use "Clear All" to start over

## 🎯 Example Workflow

1. **Prepare Image**: Take/get clear planogram photo
2. **Run Tool**: `python draw_sections.py my_image.jpg`
3. **Draw Sections**: Click and drag to create boundaries
4. **Review**: Click "Finish Drawing" to see coordinates
5. **Save**: Click "Save Config" and enter section details
6. **Use**: Load new config in your planogram demo

## 🔗 Integration

Generated configuration files work directly with:
- **Planogram Demo App** (`app.py`)
- **PlanogramAnnotator** (automatic boundary display)
- **PlanogramAnalyzer** (detection analysis)

Your custom configurations will appear in the demo's configuration dropdown automatically!

---

**Happy Section Drawing! 🎨📊** 