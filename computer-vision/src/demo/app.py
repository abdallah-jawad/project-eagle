import streamlit as st
import pandas as pd
from PIL import Image
import os
import json
import tempfile
import atexit
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from backend.planogram_analyzer import PlanogramAnalyzer
from backend.config import PlanogramConfig, DeploymentConfig
from backend.planogram_annotator import PlanogramAnnotator
from backend.streamlit_drawer import create_planogram_drawing_interface, generate_planogram_config, save_planogram_config

# Page configuration
st.set_page_config(
    page_title="Planogram Vision Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = PlanogramAnalyzer()
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Available item types
AVAILABLE_ITEMS = [
    "bottled_drinks", "canned_drinks", "large_plates", "salads_bowls", 
    "sandwiches", "small_plates", "wraps", "yogurt_cups_large", "yogurt_cups_small"
]

def create_planogram_config():
    """Component for creating planogram configurations"""
    st.header("🎯 Create New Planogram")
    
    # Add debug information for deployment troubleshooting
    with st.expander("🔧 Debug Information (Click to expand)"):
        st.write("**Environment Information:**")
        st.write(f"  - Current working directory: `{os.getcwd()}`")
        st.write(f"  - Script directory: `{os.path.dirname(__file__)}`")
        st.write(f"  - Absolute script directory: `{os.path.dirname(os.path.abspath(__file__))}`")
        st.write(f"  - Platform: `{os.name}`")
        st.write(f"  - Python version: `{os.sys.version}`")
        
        # Check if config directories exist
        from backend.config import DeploymentConfig
        config_dir = DeploymentConfig.get_config_dir()
        images_dir = DeploymentConfig.get_images_dir()
        temp_dir = DeploymentConfig.get_temp_dir()
        
        st.write("**Directory Information:**")
        st.write(f"  - Config directory: `{config_dir}` (exists: {os.path.exists(config_dir)})")
        st.write(f"  - Images directory: `{images_dir}` (exists: {os.path.exists(images_dir)})")
        st.write(f"  - Temp directory: `{temp_dir}` (exists: {os.path.exists(temp_dir)})")
        
        # Check for base image
        base_image_path = os.path.join(os.path.dirname(__file__), "config", "planogram_image", "planogram_base.jpeg")
        st.write(f"  - Base image path: `{base_image_path}` (exists: {os.path.exists(base_image_path)})")
    
    # Check if interactive canvas is available (silently)
    try:
        from streamlit_drawable_canvas import st_canvas
        canvas_available = True
        st.success("✅ Canvas component is available")
    except ImportError as e:
        canvas_available = False
        st.error(f"⚠️ Drawing component not available: {e}")
        st.error("Please install: `pip install streamlit-drawable-canvas-fix`")
        return
    
    # Import PIL at the beginning to ensure it's available
    try:
        from PIL import Image, ImageDraw
    except ImportError as e:
        st.error(f"❌ PIL/Pillow not available: {e}")
        st.error("Please install: `pip install Pillow`")
        return
    
    # Use the base planogram image - handle both local and deployed environments
    base_image_path = os.path.join(
        os.path.dirname(__file__), 
        "config", 
        "planogram_image", 
        "planogram_base.jpeg"
    )
    
    # Try alternative paths for deployment if the primary path doesn't work
    image = None  # Initialize image variable
    if not os.path.exists(base_image_path):
        alternative_paths = [
            os.path.join(os.getcwd(), "config", "planogram_image", "planogram_base.jpeg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "planogram_image", "planogram_base.jpeg"),
            "config/planogram_image/planogram_base.jpeg",
            "./config/planogram_image/planogram_base.jpeg"
        ]
        
        # Try to find the image in alternative paths
        image_found = False
        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                base_image_path = alt_path
                st.success(f"✅ Found base image at: {base_image_path}")
                image_found = True
                break
        
        if not image_found:
            # If still not found, show debug information and create placeholder
            st.error(f"❌ Base planogram image not found")
            st.info("Debug information:")
            st.write(f"**Current working directory:** `{os.getcwd()}`")
            st.write(f"**Script directory:** `{os.path.dirname(__file__)}`")
            st.write(f"**Absolute script directory:** `{os.path.dirname(os.path.abspath(__file__))}`")
            st.write(f"**Tried paths:**")
            for path in [base_image_path] + alternative_paths:
                st.write(f"  - `{path}` (exists: {os.path.exists(path)})")
            st.info("Please ensure the planogram_base.jpeg file exists in the config/planogram_image/ directory.")
            
            # Create a fallback placeholder image for testing
            st.warning("⚠️ Creating a placeholder image for testing purposes...")
            try:
                # Create a simple placeholder image
                placeholder_image = Image.new('RGB', (800, 600), color='white')
                draw = ImageDraw.Draw(placeholder_image)
                draw.rectangle([50, 50, 750, 550], outline='black', width=2)
                draw.text((400, 300), "Placeholder\nPlanogram Image", fill='black', anchor='mm')
                
                # Save placeholder to temp directory
                temp_dir = DeploymentConfig.get_temp_dir()
                os.makedirs(temp_dir, exist_ok=True)
                placeholder_path = os.path.join(temp_dir, "placeholder_planogram.jpg")
                placeholder_image.save(placeholder_path, 'JPEG')
                
                base_image_path = placeholder_path
                image = placeholder_image
                st.success("✅ Created placeholder image for testing")
                
            except Exception as e:
                st.error(f"❌ Could not create placeholder image: {e}")
                return
    
    # Load the base image if we haven't already loaded it (either from original path or placeholder)
    if image is None:
        try:
            image = Image.open(base_image_path)
            st.success(f"✅ Loaded base image from: {base_image_path}")
        except Exception as e:
            st.error(f"❌ Error loading base image: {e}")
            return
    
    # Create temporary file in deployment-configured temp directory
    temp_dir = DeploymentConfig.get_temp_dir()
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=temp_dir) as tmp_file:
            image.save(tmp_file.name, 'JPEG')
            temp_image_path = tmp_file.name
    except Exception as e:
        # Fallback: use system temp directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file.name, 'JPEG')
            temp_image_path = tmp_file.name
    
    st.session_state.temp_image_path = temp_image_path
    st.session_state.uploaded_image = image
    
    # Use the drawing interface
    sections = create_planogram_drawing_interface(image, AVAILABLE_ITEMS, temp_image_path)
    
    # Configuration generation
    if sections:
        st.markdown("---")
        st.subheader("💾 Save Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            config_name = st.text_input("Configuration Name", value="My Planogram")
            store_id = st.text_input("Store ID", value="STORE_001")
        with col2:
            description = st.text_area("Description (optional)", value="")
        
        if st.button("🚀 Save Configuration", type="primary"):
            try:
                config_data = generate_planogram_config(
                    sections, image, config_name, store_id, description
                )
                
                config_file, image_file = save_planogram_config(config_data, image)
                
                st.success("✅ Configuration saved successfully!")
                st.info("Your configuration is now available in the Analysis tab.")
                
                # Clean up temp file
                if hasattr(st.session_state, 'temp_image_path'):
                    try:
                        os.unlink(st.session_state.temp_image_path)
                        delattr(st.session_state, 'temp_image_path')
                    except Exception as e:
                        st.warning(f"Could not clean up temporary file: {e}")
                        
            except Exception as e:
                st.error(f"Error saving configuration: {e}")

def main():
    st.title("🏪 Planogram Vision System Demo")
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["🔍 Analysis", "🎯 Configuration"])
    
    with tab1:
        st.markdown("Upload an image to analyze planogram compliance and detect misplaced items.")
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            
            # Planogram selection
            config_files = PlanogramConfig.list_available_configs()
            
            # Temporary debug info for cloud deployment
            if not config_files:
                st.warning("🔍 Debug: No config files found")
                from backend.config import DeploymentConfig
                config_dir = DeploymentConfig.get_config_dir()
                st.write(f"**Looking in:** `{config_dir}`")
                st.write(f"**Absolute path:** `{os.path.abspath(config_dir)}`")
                st.write(f"**Directory exists:** {os.path.exists(config_dir)}")
                if os.path.exists(config_dir):
                    try:
                        files = os.listdir(config_dir)
                        st.write(f"**Files found:** {files}")
                    except Exception as e:
                        st.write(f"**Error listing files:** {e}")
                        
                # Also check current working directory
                st.write(f"**Current working directory:** `{os.getcwd()}`")
                
                # List what's in the current directory
                try:
                    current_files = os.listdir(".")
                    st.write(f"**Files in current dir:** {current_files[:10]}...")  # Show first 10
                except Exception as e:
                    st.write(f"**Error listing current dir:** {e}")
                    
                st.info("💡 The app will automatically create the store_004.json configuration if it's missing.")
            
            if config_files:
                selected_config = st.selectbox(
                    "Select Planogram Configuration",
                    config_files,
                    key="planogram_config"
                )
                st.session_state.analyzer.load_planogram_config(selected_config)
                
                # Generate annotated planogram when configuration is selected
                if 'current_config' not in st.session_state or st.session_state.current_config != selected_config:
                    st.session_state.current_config = selected_config
                    if st.session_state.analyzer.config:
                        # Create annotated planogram for visual display
                        try:
                            annotator = PlanogramAnnotator(st.session_state.analyzer.config)
                            annotated_path = annotator.annotate_planogram_image()
                            st.session_state.annotated_planogram_path = annotated_path
                            st.success(f"✅ Loaded configuration: {st.session_state.analyzer.config.metadata.get('name', selected_config)}")
                        except Exception as e:
                            st.error(f"Error creating annotated planogram: {e}")
                            st.session_state.annotated_planogram_path = None
            else:
                st.warning("No planogram configurations found. Please create one first.")
            
            # Analysis settings (removed sliders - now hardcoded in backend)
            st.subheader("Analysis Settings")
            st.info("Detection parameters are optimized and set automatically.")

        # Main content area - Better balanced layout
        st.header("📤 Upload & Configuration")
        
        # Upload section
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of your store shelf/planogram to analyze"
        )
        
        if uploaded_file is not None:
            # Load the original image for analysis
            original_image = Image.open(uploaded_file)
            
            # Create a resized version for display
            display_image = _resize_image_for_display(original_image, max_width=600)
            
            # Two columns for image and planogram
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📸 Uploaded Image")
                st.image(display_image, caption="Uploaded Image", use_container_width=True)
                
                # Store original image in session state
                st.session_state.original_image = original_image
                
                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔍 Analyze Planogram", type="primary", use_container_width=True):
                        with st.spinner("Analyzing planogram..."):
                            # Run analysis with the original image
                            results = st.session_state.analyzer.analyze_image(original_image)
                            st.session_state.analysis_results = results
                            st.success("Analysis complete!")
                
                with col_btn2:
                    if st.button("🗑️ Clear Results", use_container_width=True):
                        st.session_state.analysis_results = None
                        st.rerun()
            
            with col2:
                st.subheader("📋 Expected Planogram")
                
                # Display annotated planogram image if available
                if 'annotated_planogram_path' in st.session_state and st.session_state.annotated_planogram_path:
                    annotated_path = st.session_state.annotated_planogram_path
                    
                    # Handle relative paths for cloud deployment
                    if not os.path.isabs(annotated_path) and not os.path.exists(annotated_path):
                        # Try making it relative to current directory
                        alt_path = os.path.join(os.getcwd(), annotated_path)
                        if os.path.exists(alt_path):
                            annotated_path = alt_path
                    
                    if os.path.exists(annotated_path):
                        planogram_image = Image.open(annotated_path)
                        # Create a resized version for display
                        planogram_display = _resize_image_for_display(planogram_image, max_width=600)
                        st.image(planogram_display, caption="Expected Planogram Layout", use_container_width=True)
                        
                    else:
                        st.error(f"Annotated planogram image not found at: {annotated_path}")
                        # Try to recreate the annotated image
                        if st.session_state.analyzer.config:
                            try:
                                annotator = PlanogramAnnotator(st.session_state.analyzer.config)
                                new_annotated_path = annotator.annotate_planogram_image()
                                st.session_state.annotated_planogram_path = new_annotated_path
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not recreate annotated planogram: {e}")
                else:
                    st.info("Please select a planogram configuration to view the expected layout.")
        else:
            # Show placeholder when no image is uploaded
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📸 Uploaded Image")
                st.info("Please upload an image to begin analysis.")
            
            with col2:
                st.subheader("📋 Expected Planogram")
                st.info("Please select a planogram configuration to view the expected layout.")

        # Results section
        if st.session_state.analysis_results is not None:
            st.header("📊 Analysis Results")
            results = st.session_state.analysis_results
            
            # Display annotated image
            st.subheader("🎯 Detected Items (Annotated)")
            if results.annotated_image is not None:
                # Create a resized version for display
                display_image = _resize_image_for_display(results.annotated_image, max_width=1080)
                
                # Center the image using columns
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(display_image, caption="Detected Items")
            
            # Results in tabs (enhanced with detailed inventory views)
            results_tab1, results_tab2, results_tab3, results_tab4, results_tab5 = st.tabs([
                "📦 All Detections",
                "❌ Misplaced Items", 
                "🔍 Inventory",
                "📋 Tasks",
                "📄 Summary"
            ])
            
            with results_tab1:
                st.subheader("All Detected Items")
                if not results.detected_items.empty:
                    st.dataframe(results.detected_items, use_container_width=True)
                    st.info(f"Total items detected: {len(results.detected_items)}")
                    
                    # Detection summary by item type
                    if 'class_name' in results.detected_items.columns:
                        item_counts = results.detected_items['class_name'].value_counts()
                        st.subheader("Detections by Items")
                        
                        # Create a DataFrame for the item counts table
                        item_data = []
                        for item_class, count in item_counts.items():
                            item_data.append({
                                'Item Type': item_class,
                                'Count': count
                            })
                        
                        if item_data:
                            item_df = pd.DataFrame(item_data)
                            st.table(item_df)
                        else:
                            st.info("No item types detected.")
                    
                    # Detection summary by section
                    if 'section_id' in results.detected_items.columns:
                        section_counts = results.detected_items['section_id'].value_counts()
                        st.subheader("Detections by Section")
                        
                        # Create a DataFrame for the table
                        section_data = []
                        for section, count in section_counts.items():
                            if section and section != 'None':  # Skip None/null sections
                                section_data.append({
                                    'Section': section,
                                    'Detected Items': count
                                })
                        
                        if section_data:
                            section_df = pd.DataFrame(section_data)
                            st.table(section_df)
                        else:
                            st.info("No items assigned to sections.")
                else:
                    st.warning("No items detected in the image.")
            
            with results_tab2:
                st.subheader("Misplaced Items")
                if not results.misplaced_items.empty:
                    st.dataframe(results.misplaced_items, use_container_width=True)
                    st.error(f"Found {len(results.misplaced_items)} misplaced items!")
                    
                    # Display individual visualizations for misplaced items
                    st.markdown("---")
                    st.subheader("🔍 Individual Misplaced Item Visualizations")
                    st.info("Each visualization shows the misplaced item (red), its current section (orange), and where it should be (green).")
                    
                    # Access the raw misplaced items with their visualization images
                    if hasattr(results, 'raw_misplaced_items') and results.raw_misplaced_items:
                        # Create expandable sections for each misplaced item with visualizations
                        for i, misplaced_item in enumerate(results.raw_misplaced_items):
                            item_class = misplaced_item.detected_item.class_name
                            expected_section = misplaced_item.expected_section
                            actual_section = misplaced_item.actual_section or 'Unknown'
                            confidence = misplaced_item.detected_item.confidence
                            
                            with st.expander(f"🔴 {item_class} (Confidence: {confidence:.2f})", expanded=False):
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    st.write("**Issue Details:**")
                                    st.write(f"• **Item Type:** {item_class}")
                                    st.write(f"• **Confidence:** {confidence:.2f}")
                                    st.write(f"• **Should be in:** {expected_section}")
                                    st.write(f"• **Currently in:** {actual_section}")
                                    
                                    st.write("**Action Required:**")
                                    st.error(f"Move this {item_class} from **{actual_section}** to **{expected_section}**")
                                    
                                    # Legend for the visualization
                                    st.write("**Visualization Legend:**")
                                    st.markdown("🔴 **Red**: Misplaced item")
                                    st.markdown("🟢 **Green**: Where it should be")
                                    if actual_section != 'Unknown':
                                        st.markdown("🟠 **Orange**: Where it currently is")
                                
                                with col2:
                                    st.write("**Detailed Visualization:**")
                                    
                                    # Display the visualization image if available
                                    if misplaced_item.visualization_image is not None:
                                        # Create a smaller version for display
                                        display_viz = _resize_image_for_display(
                                            misplaced_item.visualization_image, 
                                            max_width=600
                                        )
                                        st.image(
                                            display_viz, 
                                            caption=f"Misplaced {item_class} - Move to {expected_section}",
                                            use_container_width=True
                                        )
                                    else:
                                        st.warning("Visualization not available for this item.")
                    else:
                        # Fallback to basic information if raw items not available
                        st.info("Detailed visualizations with raw misplaced items are not available in this analysis result.")
                        
                        # Create expandable sections with basic information
                        for idx, row in results.misplaced_items.iterrows():
                            item_class = row['item_class']
                            expected_section = row['expected_section']
                            actual_section = row['actual_section']
                            confidence = row['confidence']
                            
                            with st.expander(f"🔴 {item_class} (Confidence: {confidence:.2f})", expanded=False):
                                st.write("**Issue Details:**")
                                st.write(f"• **Item Type:** {item_class}")
                                st.write(f"• **Confidence:** {confidence:.2f}")
                                st.write(f"• **Should be in:** {expected_section}")
                                st.write(f"• **Currently in:** {actual_section}")
                                
                                st.write("**Action Required:**")
                                st.error(f"Move this {item_class} from **{actual_section}** to **{expected_section}**")
                                
                                st.info("💡 Run a new analysis to generate detailed visualizations.")
                else:
                    st.success("No misplaced items detected!")
            
            with results_tab3:
                st.subheader("Inventory by Section")
                if not results.detailed_inventory_status.empty:
                    for _, section_data in results.detailed_inventory_status.iterrows():
                        section_name = section_data['section_name']
                        
                        # Create expandable section (without status since we removed it)
                        with st.expander(f"🏪 {section_name}", expanded=False):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Expected Total", section_data['total_expected'])
                            with col2:
                                st.metric("Expected Visible", section_data['total_expected_visible'])
                            with col3:
                                st.metric("Detected in Section", section_data['total_detected'])
                            with col4:
                                st.metric("Found Elsewhere", section_data['total_misplaced'])
                            
                            # Item breakdown table
                            st.subheader("Item Type Breakdown")
                            item_breakdown = section_data['item_breakdown']
                            
                            if item_breakdown:
                                breakdown_df = pd.DataFrame(item_breakdown)
                                
                                # Color code the availability status
                                def highlight_availability(row):
                                    colors = []
                                    for col in row.index:
                                        if col == 'availability_status':
                                            if row[col] == 'Sold Out':
                                                colors.append('background-color: #ffcccc; color: #cc0000')
                                            elif row[col] == 'Misplaced Only':
                                                colors.append('background-color: #fff3cd; color: #856404')
                                            elif row[col] == 'Partially Misplaced':
                                                colors.append('background-color: #cce5ff; color: #004085')
                                            elif row[col] == 'Low Stock':
                                                colors.append('background-color: #ffeaa7; color: #6c5ce7')
                                            elif row[col] == 'Mostly Hidden':
                                                colors.append('background-color: #ddd6fe; color: #7c3aed')
                                            elif row[col] == 'Available':
                                                colors.append('background-color: #d4edda; color: #155724')
                                            else:
                                                colors.append('')
                                        else:
                                            colors.append('')
                                    return colors
                                
                                styled_df = breakdown_df.style.apply(highlight_availability, axis=1)
                                st.dataframe(styled_df, use_container_width=True)
                                
                                # Key insights for this section
                                sold_out_items = [item for item in item_breakdown if item['availability_status'] == 'Sold Out']
                                misplaced_only_items = [item for item in item_breakdown if item['availability_status'] == 'Misplaced Only']
                                mostly_hidden_items = [item for item in item_breakdown if item['availability_status'] == 'Mostly Hidden']
                                low_stock_items = [item for item in item_breakdown if item['availability_status'] == 'Low Stock']
                                
                                if sold_out_items:
                                    st.error(f"🚫 Truly Sold Out: {', '.join([item['item_type'] for item in sold_out_items])}")
                                
                                if misplaced_only_items:
                                    st.warning(f"📦 Available but Misplaced: {', '.join([item['item_type'] for item in misplaced_only_items])}")
                                
                                if mostly_hidden_items:
                                    st.info(f"👁️ Mostly Hidden (behind other items): {', '.join([item['item_type'] for item in mostly_hidden_items])}")
                                
                                if low_stock_items:
                                    st.warning(f"📉 Low Stock: {', '.join([item['item_type'] for item in low_stock_items])}")
                            else:
                                st.info("No item breakdown available for this section.")
                else:
                    st.info("No detailed inventory data available.")
            
            with results_tab4:
                st.subheader("Recommended Tasks")
                if not results.tasks.empty:
                    st.dataframe(results.tasks, use_container_width=True)
                else:
                    st.info("No tasks available at this time.")
            
            with results_tab5:
                st.subheader("📊 Analysis Summary")
                
                # Key metrics row
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_detections = len(results.detected_items) if not results.detected_items.empty else 0
                misplaced_count = len(results.misplaced_items) if not results.misplaced_items.empty else 0
                pending_tasks = len(results.tasks) if not results.tasks.empty else 0
                
                # Calculate inventory status counts from detailed breakdown
                out_of_stock_count = 0
                low_stock_count = 0
                overstock_count = 0
                in_stock_count = 0
                sold_out_count = 0
                misplaced_only_count = 0
                
                if not results.detailed_inventory_status.empty:
                    # Extract status information from item breakdown
                    for _, row in results.detailed_inventory_status.iterrows():
                        if 'item_breakdown' in row and row['item_breakdown']:
                            for item in row['item_breakdown']:
                                status = item.get('availability_status', '')
                                if status == 'Sold Out':
                                    sold_out_count += 1
                                elif status == 'Low Stock':
                                    low_stock_count += 1
                                elif status == 'Misplaced Only':
                                    misplaced_only_count += 1
                                elif status == 'Available':
                                    in_stock_count += 1
                    
                    out_of_stock_count = sold_out_count  # Use sold out as out of stock metric
                
                # Calculate improved compliance score
                compliance_score = calculate_enhanced_compliance_score(results, st.session_state.analyzer.config)
                
                with col1:
                    st.metric("Total Detections", total_detections, delta=None)
                
                with col2:
                    st.metric("Misplaced Items", misplaced_count, 
                             delta=f"{-misplaced_count}" if misplaced_count > 0 else None)
                
                with col3:
                    st.metric("Pending Tasks", pending_tasks,
                             delta=f"{-pending_tasks}" if pending_tasks > 0 else None)
                
                with col4:
                    st.metric("Out of Stock", out_of_stock_count,
                             delta=f"{-out_of_stock_count}" if out_of_stock_count > 0 else None)
                
                with col5:
                    compliance_color = "normal" if compliance_score >= 80 else "inverse"
                    st.metric("Compliance Score", f"{compliance_score:.1f}%",
                             delta=f"{compliance_score-70:.1f}%" if compliance_score != 0 else None)
                
                st.markdown("---")
                
                # Visual analytics section
                if not results.detected_items.empty or not results.detailed_inventory_status.empty:
                    
                    # Create tabs for different analytics views
                    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs([
                        "📈 Inventory Overview", "🔍 Section Performance", "⚠️ Issues & Tasks"
                    ])
                    
                    with analytics_tab1:
                        create_inventory_overview_charts(results)
                    
                    with analytics_tab2:
                        create_section_performance_charts(results, st.session_state.analyzer.config)
                    
                    with analytics_tab3:
                        create_issues_tasks_charts(results)
                else:
                    st.info("📊 No data available for analysis. Please run detection on an image first.")
    
    with tab2:
        create_planogram_config()

def calculate_enhanced_compliance_score(results, config):
    """
    Calculate an enhanced compliance score based on multiple factors:
    - Inventory accuracy (40%)
    - Placement accuracy (30%)
    - Stock level health (20%)
    - Task urgency (10%)
    """
    if not config or not config.sections:
        return 0.0
    
    # Base weights
    weights = {
        'inventory': 0.10,
        'placement': 0.55, 
        'stock_health': 0.30,
        'task_urgency': 0.05
    }
    
    # Calculate inventory accuracy score based on visible items (accounting for occlusion)
    total_expected_visible = sum(section.expected_visible_count for section in config.sections)
    total_detected = len(results.detected_items) if not results.detected_items.empty else 0
    inventory_score = min(100, (total_detected / total_expected_visible * 100) if total_expected_visible > 0 else 100)
    
    # Calculate placement accuracy score
    misplaced_count = len(results.misplaced_items) if not results.misplaced_items.empty else 0
    placement_score = max(0, (total_detected - misplaced_count) / total_detected * 100) if total_detected > 0 else 100
    
    # Calculate stock health score (penalize out of stock and overstock)
    stock_health_score = 100
    if not results.detailed_inventory_status.empty:
        # Extract status counts from item breakdown
        sold_out_count = 0
        low_stock_count = 0
        total_items = 0
        
        for _, row in results.detailed_inventory_status.iterrows():
            if 'item_breakdown' in row and row['item_breakdown']:
                for item in row['item_breakdown']:
                    total_items += 1
                    status = item.get('availability_status', '')
                    if status == 'Sold Out':
                        sold_out_count += 1
                    elif status == 'Low Stock':
                        low_stock_count += 1
        
        if total_items > 0:
            out_of_stock_penalty = (sold_out_count / total_items) * 50
            low_stock_penalty = (low_stock_count / total_items) * 10
            stock_health_score = max(0, 100 - out_of_stock_penalty - low_stock_penalty)
    
    # Calculate task urgency score (penalize high-priority pending tasks)
    task_urgency_score = 100
    if not results.tasks.empty:
        high_priority_tasks = len(results.tasks[results.tasks['priority'] == 'High']) if 'priority' in results.tasks.columns else 0
        medium_priority_tasks = len(results.tasks[results.tasks['priority'] == 'Medium']) if 'priority' in results.tasks.columns else 0
        
        task_urgency_score = max(0, 100 - (high_priority_tasks * 15) - (medium_priority_tasks * 5))
    
    # Calculate weighted final score
    final_score = (
        inventory_score * weights['inventory'] +
        placement_score * weights['placement'] +
        stock_health_score * weights['stock_health'] +
        task_urgency_score * weights['task_urgency']
    )
    
    return min(100, max(0, final_score))

def create_inventory_overview_charts(results):
    """Create inventory overview visualizations"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📦 Inventory Status Distribution")
        if not results.detailed_inventory_status.empty:
            # Extract status counts from item breakdown
            status_counts = {}
            
            for _, row in results.detailed_inventory_status.iterrows():
                if 'item_breakdown' in row and row['item_breakdown']:
                    for item in row['item_breakdown']:
                        status = item.get('availability_status', '')
                        if status:
                            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                # Define colors for different statuses
                colors = {
                    'Available': '#2E8B57',
                    'Low Stock': '#FFD700', 
                    'Sold Out': '#DC143C',
                    'Misplaced Only': '#FF8C00',
                    'Partially Misplaced': '#4169E1',
                    'Not Expected': '#808080'
                }
                
                fig_pie = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Item Availability Status Breakdown",
                    color=list(status_counts.keys()),
                    color_discrete_map=colors
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No status breakdown available")
        else:
            st.info("No inventory status data available")
    
    with col2:
        st.subheader("📊 Stock Levels based on Visible Items")
        if not results.detected_items.empty:
            # Bar chart for item counts
            item_counts = results.detected_items['class_name'].value_counts()
            
            fig_bar = px.bar(
                x=item_counts.index,
                y=item_counts.values,
                labels={'x': 'Item Type', 'y': 'Count'},
                title="Detected Items Count",
                color=item_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No detection data available")
    
    with col3:
        st.subheader("📍 Items per Section")
        if not results.detected_items.empty and 'section_id' in results.detected_items.columns:
            section_counts = results.detected_items.groupby('section_id')['class_name'].count()
            
            fig_section = px.bar(
                x=section_counts.index,
                y=section_counts.values,
                labels={'x': 'Section ID', 'y': 'Item Count'},
                title="Items Detected by Section",
                color=section_counts.values,
                color_continuous_scale='Blues'
            )
            fig_section.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_section, use_container_width=True)
        else:
            st.info("Section data not available")



def create_issues_tasks_charts(results):
    """Create issues and tasks analysis visualizations"""
    
    if not results.misplaced_items.empty:
        st.subheader("⚠️ Detailed Misplaced Items Analysis")
        
        # Create tabs for different misplacement analyses
        misplaced_tab1, misplaced_tab2, misplaced_tab3, misplaced_tab4 = st.tabs([
            "📊 Overview", "🔄 Movement Flow", "📦 Item Types", "🎯 Actions by Confidence"
        ])
        
        with misplaced_tab1:
            # Overview with multiple charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Misplaced items by their expected (correct) section
                if 'expected_section' in results.misplaced_items.columns:
                    misplaced_by_expected_section = results.misplaced_items['expected_section'].value_counts()
                    
                    fig_expected = px.bar(
                        x=misplaced_by_expected_section.index,
                        y=misplaced_by_expected_section.values,
                        labels={'x': 'Expected Section', 'y': 'Misplaced Count'},
                        title="Items That Should Be In Each Section",
                        color=misplaced_by_expected_section.values,
                        color_continuous_scale='Reds'
                    )
                    fig_expected.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_expected, use_container_width=True)
            
            with col2:
                # Misplaced items by where they were actually found
                if 'actual_section' in results.misplaced_items.columns:
                    misplaced_by_actual_section = results.misplaced_items['actual_section'].value_counts()
                    
                    fig_actual = px.bar(
                        x=misplaced_by_actual_section.index,
                        y=misplaced_by_actual_section.values,
                        labels={'x': 'Actual Section', 'y': 'Foreign Items Count'},
                        title="Foreign Items Found In Each Section",
                        color=misplaced_by_actual_section.values,
                        color_continuous_scale='Oranges'
                    )
                    fig_actual.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_actual, use_container_width=True)
            
            # Summary metrics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            total_misplaced = len(results.misplaced_items)
            avg_confidence = results.misplaced_items['confidence'].mean() if 'confidence' in results.misplaced_items.columns else 0
            unique_sections_affected = results.misplaced_items['expected_section'].nunique() if 'expected_section' in results.misplaced_items.columns else 0
            unique_item_types = results.misplaced_items['item_class'].nunique() if 'item_class' in results.misplaced_items.columns else 0
            
            with col1:
                st.metric("Total Misplaced", total_misplaced)
            with col2:
                st.metric("Avg Confidence", f"{avg_confidence:.2f}" if avg_confidence > 0 else "N/A")
            with col3:
                st.metric("Sections Affected", unique_sections_affected)
            with col4:
                st.metric("Item Types", unique_item_types)
        
        with misplaced_tab2:
            # Movement flow analysis
            st.subheader("🔄 Item Movement Flow")
            
            if 'actual_section' in results.misplaced_items.columns and 'expected_section' in results.misplaced_items.columns:
                # Create movement flow data
                movement_data = []
                for _, row in results.misplaced_items.iterrows():
                    movement_data.append({
                        'From': row['expected_section'],
                        'To': row['actual_section'],
                        'Item': row['item_class'] if 'item_class' in row else 'Unknown',
                        'Confidence': row['confidence'] if 'confidence' in row else 0
                    })
                
                movement_df = pd.DataFrame(movement_data)
                
                # Group by movement pattern
                movement_summary = movement_df.groupby(['From', 'To']).agg({
                    'Item': 'count',
                    'Confidence': 'mean'
                }).rename(columns={'Item': 'Count'}).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Movement flow chart
                    fig_flow = px.bar(
                        movement_summary.head(10),  # Show top 10 movements
                        x='Count',
                        y=[f"{row['From']} → {row['To']}" for _, row in movement_summary.head(10).iterrows()],
                        orientation='h',
                        title="Top Movement Patterns (From → To)",
                        color='Count',
                        color_continuous_scale='Reds'
                    )
                    fig_flow.update_layout(height=400)
                    st.plotly_chart(fig_flow, use_container_width=True)
                
                with col2:
                    # Confidence distribution of movements
                    fig_conf = px.histogram(
                        movement_df,
                        x='Confidence',
                        nbins=20,
                        title="Confidence Distribution of Misplacements",
                        color_discrete_sequence=['#ff6b6b']
                    )
                    fig_conf.update_layout(height=400)
                    st.plotly_chart(fig_conf, use_container_width=True)
            else:
                st.info("Movement flow data not available - missing section information")
        
        with misplaced_tab3:
            # Item type analysis
            st.subheader("📦 Misplaced Items by Type")
            
            if 'item_class' in results.misplaced_items.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Item type distribution
                    item_counts = results.misplaced_items['item_class'].value_counts()
                    
                    fig_items = px.pie(
                        values=item_counts.values,
                        names=item_counts.index,
                        title="Misplaced Items by Type",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_items.update_traces(textposition='inside', textinfo='percent+label')
                    fig_items.update_layout(height=400)
                    st.plotly_chart(fig_items, use_container_width=True)
                
                with col2:
                    # Item type vs confidence
                    if 'confidence' in results.misplaced_items.columns:
                        fig_conf_item = px.box(
                            results.misplaced_items,
                            x='item_class',
                            y='confidence',
                            title="Detection Confidence by Item Type",
                            color='item_class'
                        )
                        fig_conf_item.update_layout(
                            height=400,
                            xaxis_tickangle=-45,
                            showlegend=False
                        )
                        st.plotly_chart(fig_conf_item, use_container_width=True)
                
                # Detailed breakdown table
                st.subheader("📋 Detailed Item Type Breakdown")
                
                if 'expected_section' in results.misplaced_items.columns and 'actual_section' in results.misplaced_items.columns:
                    detailed_breakdown = results.misplaced_items.groupby('item_class').agg({
                        'confidence': ['count', 'mean', 'min', 'max'],
                        'expected_section': lambda x: len(x.unique()),
                        'actual_section': lambda x: len(x.unique())
                    }).round(3)
                    
                    # Flatten column names
                    detailed_breakdown.columns = [
                        'Total Count', 'Avg Confidence', 'Min Confidence', 'Max Confidence',
                        'Expected Sections', 'Found In Sections'
                    ]
                    
                    st.dataframe(detailed_breakdown, use_container_width=True)
            else:
                st.info("Item class information not available")
        
        with misplaced_tab4:
            # Priority actions
            st.subheader("🎯 Actions by Confidence Level")
            st.info("💡 **Confidence levels indicate how reliable the misplacement detection is**:\n"
                   "- 🔴 **High (≥80%)**: Very reliable detections, act immediately\n"
                   "- 🟡 **Medium (60-80%)**: Moderately reliable, verify and act\n"
                   "- 🟢 **Low (<60%)**: Lower reliability, double-check before acting")
            
            # Create prioritized action list
            action_items = []
            
            if 'confidence' in results.misplaced_items.columns and 'expected_section' in results.misplaced_items.columns:
                for _, row in results.misplaced_items.iterrows():
                    confidence = row['confidence']
                    item_class = row['item_class'] if 'item_class' in row else 'Unknown'
                    expected_section = row['expected_section']
                    actual_section = row['actual_section'] if 'actual_section' in row else 'Unknown'
                    
                    # Determine confidence level based on detection confidence
                    if confidence >= 0.8:
                        confidence_level = "🔴 High Confidence"
                        confidence_score = 3
                    elif confidence >= 0.6:
                        confidence_level = "🟡 Medium Confidence" 
                        confidence_score = 2
                    else:
                        confidence_level = "🟢 Low Confidence"
                        confidence_score = 1
                    
                    action_items.append({
                        'Confidence Level': confidence_level,
                        'Confidence Score': confidence_score,
                        'Item Type': item_class,
                        'Action': f"Move from {actual_section} to {expected_section}",
                        'Confidence': f"{confidence:.2f}",
                        'Expected Section': expected_section,
                        'Current Section': actual_section
                    })
                
                # Sort by confidence score and confidence
                action_df = pd.DataFrame(action_items).sort_values(['Confidence Score', 'Confidence'], ascending=[False, False])
                
                # Display actions by confidence level - full width
                st.dataframe(
                    action_df[['Confidence Level', 'Item Type', 'Action', 'Confidence']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Action summary
                st.markdown("---")
                st.subheader("📝 Action Summary by Confidence")
                
                high_confidence = len(action_df[action_df['Confidence Level'] == '🔴 High Confidence'])
                medium_confidence = len(action_df[action_df['Confidence Level'] == '🟡 Medium Confidence'])
                low_confidence = len(action_df[action_df['Confidence Level'] == '🟢 Low Confidence'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if high_confidence > 0:
                        st.error(f"🔴 **{high_confidence} High Confidence Actions**")
                        st.write("Very reliable detections (≥80%)")
                    else:
                        st.success("✅ No high confidence actions")
                
                with col2:
                    if medium_confidence > 0:
                        st.warning(f"🟡 **{medium_confidence} Medium Confidence Actions**")
                        st.write("Moderately reliable (60-80%)")
                    else:
                        st.info("No medium confidence actions")
                
                with col3:
                    if low_confidence > 0:
                        st.info(f"🟢 **{low_confidence} Low Confidence Actions**")
                        st.write("Lower reliability (<60%)")
                    else:
                        st.info("No low confidence actions")
                
                # Task Priority Distribution
                st.markdown("---")
                st.subheader("📋 Task Priority Distribution")
                st.info("💡 **Note**: Task priority is based on business importance of sections (configured in planogram), not detection confidence.")
                
                if not results.tasks.empty and 'priority' in results.tasks.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        priority_counts = results.tasks['priority'].value_counts()
                        
                        # Define colors for priorities
                        priority_colors = {
                            'High': '#DC143C',
                            'Medium': '#FFD700',
                            'Low': '#32CD32'
                        }
                        
                        fig_tasks = px.pie(
                            values=priority_counts.values,
                            names=priority_counts.index,
                            title="Task Priority Breakdown",
                            color=priority_counts.index,
                            color_discrete_map=priority_colors
                        )
                        fig_tasks.update_traces(textposition='inside', textinfo='percent+label')
                        fig_tasks.update_layout(height=400)
                        st.plotly_chart(fig_tasks, use_container_width=True)
                    
                    with col2:
                        # Task details if available
                        if 'task_type' in results.tasks.columns:
                            task_type_counts = results.tasks['task_type'].value_counts()
                            
                            fig_task_types = px.bar(
                                x=task_type_counts.values,
                                y=task_type_counts.index,
                                orientation='h',
                                title="Tasks by Type",
                                color=task_type_counts.values,
                                color_continuous_scale='Blues'
                            )
                            fig_task_types.update_layout(height=400)
                            st.plotly_chart(fig_task_types, use_container_width=True)
                        else:
                            st.info("Task type information not available")
                else:
                    st.info("No task data available")
    else:
        st.success("🎉 No misplaced items detected!")

def create_section_performance_charts(results, config):
    """Create section performance analysis"""
    if not config or not config.sections:
        st.info("No planogram configuration available for section analysis")
        return
    
    st.subheader("🔍 Section Performance Analysis (Accurate Stock Assessment)")
    st.info("📍 **Key Insight**: Stock scores now only count items that actually belong in each section, excluding foreign items that may have been detected but don't belong there.")
    
    # Calculate section performance metrics
    section_data = []
    for section in config.sections:
        detected_in_section = 0
        misplaced_in_section = 0
        correctly_placed_in_section = 0
        foreign_items_in_section = 0
        
        if not results.detected_items.empty and 'section_id' in results.detected_items.columns:
            # All items detected in this section (including foreign items)
            detected_in_section = len(results.detected_items[
                results.detected_items['section_id'] == section.section_id
            ])
            
            # Count foreign items: items detected in this section but belonging elsewhere
            if not results.misplaced_items.empty and 'actual_section' in results.misplaced_items.columns:
                foreign_items_in_section = len(results.misplaced_items[
                    results.misplaced_items['actual_section'] == section.section_id
                ])
            
            # Calculate correctly placed items: detected items minus foreign items
            correctly_placed_in_section = max(0, detected_in_section - foreign_items_in_section)
        
        if not results.misplaced_items.empty and 'expected_section' in results.misplaced_items.columns:
            # Count items that BELONG to this section but were found elsewhere
            misplaced_in_section = len(results.misplaced_items[
                results.misplaced_items['expected_section'] == section.section_id
            ])
        
        # Calculate performance score using correctly placed items (not including foreign items)
        expected_visible = section.expected_visible_count
        available_total = correctly_placed_in_section + misplaced_in_section
        
        # Determine stock status using exact same logic as DetailedInventoryStatus but with correct items only
        if correctly_placed_in_section == 0 and available_total == 0:
            stock_status = "Sold Out"
            stock_score = 0
        elif correctly_placed_in_section == 0 and misplaced_in_section > 0:
            stock_status = "Misplaced Only" 
            stock_score = 25  # Items exist but need repositioning
        elif correctly_placed_in_section <= (expected_visible * 0.5):
            if misplaced_in_section > 0:
                stock_status = "Partially Misplaced"
                stock_score = (correctly_placed_in_section / expected_visible) * 75  # Scale to 0-75 for partial misplacement
            else:
                stock_status = "Low Stock"
                stock_score = (correctly_placed_in_section / expected_visible) * 50  # Scale to 0-50 for low stock
        else:
            stock_status = "Available"
            stock_score = min(100, (correctly_placed_in_section / expected_visible) * 100)
        
        # Calculate placement accuracy: what % of detected items in this section are correctly placed
        placement_score = (correctly_placed_in_section / detected_in_section * 100) if detected_in_section > 0 else 100
        
        section_data.append({
            'Section': section.section_id,
            'Expected Visible': expected_visible,
            'Correctly Placed': correctly_placed_in_section,
            'Found Elsewhere': misplaced_in_section,
            'Foreign Items': foreign_items_in_section,
            'Total Available': available_total,
            'Stock Status': stock_status,
            'Stock Score %': stock_score,
            'Placement %': max(0, placement_score),
            'Priority': section.priority
        })
    
    df_sections = pd.DataFrame(section_data)
    
    # Section stock level comparison - full width
    fig_stock = px.bar(
        df_sections,
        x='Section',
        y='Stock Score %',
        title="Section Stock Levels (vs Expected Visible Items)",
        color='Stock Status',
        color_discrete_map={
            'Sold Out': '#DC143C',
            'Misplaced Only': '#FF8C00', 
            'Low Stock': '#FFD700',
            'Partially Misplaced': '#4169E1',
            'Available': '#32CD32'
        }
    )
    fig_stock.add_hline(y=50, line_dash="dash", annotation_text="Low Stock Threshold: 50% of visible")
    fig_stock.update_layout(height=500)
    st.plotly_chart(fig_stock, use_container_width=True)
    
    # Section performance table
    st.subheader("📊 Detailed Section Metrics")
    styled_df = df_sections.style.format({
        'Stock Score %': '{:.1f}%',
        'Placement %': '{:.1f}%'
    }).background_gradient(subset=['Stock Score %', 'Placement %'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_df, use_container_width=True)
    
def _resize_image_for_display(image: Image.Image, max_width: int = 800) -> Image.Image:
    """
    Resize image for display while maintaining aspect ratio
    
    Args:
        image: PIL Image to resize
        max_width: Maximum width for display
        
    Returns:
        Resized PIL Image
    """
    original_width, original_height = image.size
    
    # Always resize to ensure consistent display size
    if original_width > max_width:
        # Calculate new dimensions maintaining aspect ratio
        aspect_ratio = original_height / original_width
        new_width = max_width
        new_height = int(max_width * aspect_ratio)
        
        # Resize using high-quality resampling
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image
    else:
        # If image is already smaller, still resize to max_width for consistency
        aspect_ratio = original_height / original_width
        new_width = max_width
        new_height = int(max_width * aspect_ratio)
        
        # Resize using high-quality resampling
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image

if __name__ == "__main__":
    main() 