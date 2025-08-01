import streamlit as st
import json
import os
import pandas as pd
from PIL import Image, ImageDraw
import numpy as np
from typing import List, Dict, Tuple, Optional
from .coordinate_system import CoordinateSystem
from .config import DeploymentConfig

# Import the drawable canvas component
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.error("streamlit-drawable-canvas not installed. Please run: pip install streamlit-drawable-canvas")

class StreamlitPlanogramDrawer:
    """
    Streamlit-compatible planogram section drawer using streamlit-drawable-canvas
    """
    
    def __init__(self, image: Image.Image, image_path: str = None):
        # If image_path is provided and exists, load the image from the path
        # This ensures we have a fresh PIL Image object for deployment scenarios
        if image_path and os.path.exists(image_path):
            try:
                self.image = Image.open(image_path)
                st.info(f"🔍 Loaded image from path: {image_path}")
            except Exception as e:
                st.warning(f"⚠️ Could not load image from path {image_path}: {e}")
                self.image = image  # Fallback to original image
        else:
            self.image = image
            
        self.image_path = image_path
        self.sections = []
        
    def draw_sections_interactive(self) -> List[Dict]:
        """
        Interactive section drawing using streamlit-drawable-canvas
        """
        if not CANVAS_AVAILABLE:
            return []
            
        # Fixed drawing settings - no sidebar controls
        drawing_mode = "rect"
        stroke_width = 2
        stroke_color = "#FF0000"  # Red
        fill_color = "rgba(255, 0, 0, 0.1)"  # Light red fill
        
        # Calculate canvas dimensions - make it much bigger
        max_canvas_width = 1200  # Increased significantly
        max_canvas_height = 900  # Increased significantly
        
        image_width, image_height = self.image.size
        aspect_ratio = image_width / image_height
        
        if aspect_ratio > max_canvas_width / max_canvas_height:
            canvas_width = max_canvas_width
            canvas_height = int(max_canvas_width / aspect_ratio)
        else:
            canvas_height = max_canvas_height
            canvas_width = int(max_canvas_height * aspect_ratio)
        
        # Center the canvas
        col1, col2, col3 = st.columns([1, 4, 1])  # Made middle column bigger
        with col2:
            # Create the interactive canvas
            # Always use the PIL Image object - streamlit-drawable-canvas expects this
            background_image = self.image
            
            # Debug info for deployment troubleshooting
            if self.image_path:
                st.info(f"🔍 Image loaded from path: {self.image_path}")
                st.info(f"🔍 File exists: {os.path.exists(self.image_path)}")
            else:
                st.info("🔍 Using original PIL Image object")
            
            canvas_result = st_canvas(
                fill_color=fill_color,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_image=background_image,
                update_streamlit=True,
                height=canvas_height,
                width=canvas_width,
                drawing_mode=drawing_mode,
                key="planogram_canvas",
                display_toolbar=True
            )
        
        # Process the drawn objects
        drawn_sections = []
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])
            
            # Filter for rectangles only
            rectangles = [obj for obj in objects if obj.get("type") == "rect"]
            
            if rectangles:
                for i, rect in enumerate(rectangles):
                    # Extract canvas coordinates
                    canvas_coords = {
                        'x1': rect["left"],
                        'y1': rect["top"],
                        'x2': rect["left"] + rect["width"],
                        'y2': rect["top"] + rect["height"]
                    }
                    
                    # Convert to reference coordinate system using CoordinateSystem
                    ref_bbox = CoordinateSystem.canvas_to_reference(
                        canvas_coords, 
                        (canvas_width, canvas_height), 
                        self.image
                    )
                    
                    # Store for configuration in reference coordinates
                    drawn_sections.append({
                        "index": i,
                        "coordinates": {"x1": ref_bbox.x1, "y1": ref_bbox.y1, "x2": ref_bbox.x2, "y2": ref_bbox.y2},
                        "canvas_object": rect
                    })
        
        return drawn_sections

def create_planogram_drawing_interface(image: Image.Image, available_items: List[str], image_path: str = None) -> List[Dict]:
    """
    Create a complete planogram drawing interface with interactive canvas
    
    Args:
        image: The planogram image to draw on
        available_items: List of available item types
        image_path: Optional file path to the image (preferred for canvas)
        
    Returns:
        List of section configurations
    """
    if not CANVAS_AVAILABLE:
        return []
    
    drawer = StreamlitPlanogramDrawer(image, image_path)
    
    # Get drawn sections from interactive canvas
    drawn_sections = drawer.draw_sections_interactive()
    
    # Section configuration
    if drawn_sections:
        st.markdown("### Configure Sections")
        
        # Initialize or get existing configurations
        if 'section_configs' not in st.session_state:
            st.session_state.section_configs = {}
        
        configured_sections = []
        
        for i, section in enumerate(drawn_sections):
            section_key = f"section_{i}"
            
            with st.expander(f"Section {i+1}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    section_id = st.text_input(
                        "Section ID", 
                        value=st.session_state.section_configs.get(f"{section_key}_id", f"SECTION_{i+1:02d}"),
                        key=f"section_id_{i}"
                    )
                    
                    section_name = st.text_input(
                        "Section Name", 
                        value=st.session_state.section_configs.get(f"{section_key}_name", f"Section {i+1}"),
                        key=f"section_name_{i}"
                    )
                    
                    # Expected items
                    expected_items = st.multiselect(
                        "Items in this section",
                        available_items,
                        default=st.session_state.section_configs.get(f"{section_key}_items", []),
                        key=f"section_items_{i}"
                    )
                
                with col2:
                    expected_count = st.number_input(
                        "Expected count", 
                        min_value=1, 
                        value=st.session_state.section_configs.get(f"{section_key}_count", 1),
                        key=f"section_count_{i}"
                    )
                    
                    expected_visible_count = st.number_input(
                        "Expected visible count", 
                        min_value=1, 
                        max_value=expected_count,
                        value=st.session_state.section_configs.get(f"{section_key}_visible_count", min(expected_count, 1)),
                        help="How many items you expect to be visible (considering occlusion)",
                        key=f"section_visible_count_{i}"
                    )
                    
                    priority = st.selectbox(
                        "Priority", 
                        ["High", "Medium", "Low"], 
                        index=["High", "Medium", "Low"].index(
                            st.session_state.section_configs.get(f"{section_key}_priority", "Medium")
                        ),
                        key=f"section_priority_{i}"
                    )
                
                # Store in session state
                st.session_state.section_configs[f"{section_key}_id"] = section_id
                st.session_state.section_configs[f"{section_key}_name"] = section_name
                st.session_state.section_configs[f"{section_key}_priority"] = priority
                st.session_state.section_configs[f"{section_key}_items"] = expected_items
                st.session_state.section_configs[f"{section_key}_count"] = expected_count
                st.session_state.section_configs[f"{section_key}_visible_count"] = expected_visible_count
                
                # Add to configured sections if all required fields are filled
                if section_id and section_name and expected_items:
                    coords = section["coordinates"]
                    configured_sections.append({
                        "section_id": section_id,
                        "name": section_name,
                        "coordinates": coords,
                        "expected_items": expected_items,
                        "expected_count": expected_count,
                        "expected_visible_count": expected_visible_count,
                        "priority": priority
                    })
        
        return configured_sections
    
    else:
        st.info("Draw rectangles on the image above to define sections")
        return []

def generate_planogram_config(
    sections: List[Dict], 
    image: Image.Image, 
    config_name: str, 
    store_id: str, 
    description: str
) -> Dict:
    """
    Generate planogram configuration from sections
    
    Args:
        sections: List of section configurations
        image: The planogram image
        config_name: Name of the configuration
        store_id: Store identifier
        description: Configuration description
        
    Returns:
        Configuration dictionary
    """
    config_data = {
        "metadata": {
            "name": config_name,
            "store_id": store_id,
            "created_date": "2024-01-01",
            "version": "1.0",
            "description": description
        },
        "planogram_image_path": os.path.join(DeploymentConfig.get_images_dir(), f"{store_id.lower()}_planogram.jpg"),
        "sections": []
    }
    
    # Convert sections to config format
    for section in sections:
        section_config = {
            "section_id": section["section_id"],
            "name": section["name"],
            "expected_items": section["expected_items"],
            "expected_count": section["expected_count"],
            "expected_visible_count": section["expected_visible_count"],
            "position": section["coordinates"],
            "priority": section["priority"]
        }
        config_data["sections"].append(section_config)
    
    return config_data

def save_planogram_config(config_data: Dict, image: Image.Image) -> Tuple[str, str]:
    """
    Save planogram configuration and image
    
    Args:
        config_data: Configuration data
        image: Planogram image
        
    Returns:
        Tuple of (config_file_path, image_file_path)
    """
    store_id = config_data["metadata"]["store_id"]
    
    # Save configuration file
    config_dir = DeploymentConfig.get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, f"{store_id.lower()}_custom.json")
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Save planogram image
    image_dir = DeploymentConfig.get_images_dir()
    os.makedirs(image_dir, exist_ok=True)
    image_file = os.path.join(image_dir, f"{store_id.lower()}_planogram.jpg")
    
    image.save(image_file, 'JPEG')
    
    return config_file, image_file 