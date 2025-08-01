import streamlit as st
import pandas as pd
from PIL import Image
import os
import json
import tempfile
import atexit
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
    
    # Check if interactive canvas is available (silently)
    try:
        from streamlit_drawable_canvas import st_canvas
        canvas_available = True
    except ImportError:
        canvas_available = False
        st.error("⚠️ Drawing component not available. Please install: `pip install streamlit-drawable-canvas-fix`")
        return
    
    # Step 1: Upload Image
    uploaded_image = st.file_uploader(
        "Upload your planogram image",
        type=['png', 'jpg', 'jpeg'],
        key="config_image_uploader"
    )
    
    if uploaded_image is not None:
        # Save uploaded image temporarily
        image = Image.open(uploaded_image)
        
        # Create temporary file in deployment-configured temp directory
        temp_dir = DeploymentConfig.get_temp_dir()
        os.makedirs(temp_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=temp_dir) as tmp_file:
            image.save(tmp_file.name, 'JPEG')
            temp_image_path = tmp_file.name
        
        st.session_state.temp_image_path = temp_image_path
        st.session_state.uploaded_image = image
        
        # Use the drawing interface
        sections = create_planogram_drawing_interface(image, AVAILABLE_ITEMS)
        
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
                    if os.path.exists(st.session_state.annotated_planogram_path):
                        planogram_image = Image.open(st.session_state.annotated_planogram_path)
                        # Create a resized version for display
                        planogram_display = _resize_image_for_display(planogram_image, max_width=600)
                        st.image(planogram_display, caption="Expected Planogram Layout", use_container_width=True)
                        
                    else:
                        st.error("Annotated planogram image not found.")
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
                st.subheader("Analysis Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Detections", 
                        len(results.detected_items) if not results.detected_items.empty else 0
                    )
                
                with col2:
                    st.metric(
                        "Misplaced Items", 
                        len(results.misplaced_items) if not results.misplaced_items.empty else 0
                    )
                
                with col3:
                    st.metric(
                        "Pending Tasks", 
                        len(results.tasks) if not results.tasks.empty else 0
                    )
                
                with col4:
                    if hasattr(results, 'inventory_status') and not results.inventory_status.empty:
                        out_of_stock_count = len(results.inventory_status[
                            results.inventory_status['status'] == 'Out of Stock'
                        ])
                    else:
                        out_of_stock_count = 0
                    st.metric("Out of Stock", out_of_stock_count)
                
                # Compliance score
                if not results.detected_items.empty:
                    total_expected = len(st.session_state.analyzer.config.sections) if st.session_state.analyzer.config else 1
                    compliance_score = max(0, (total_expected - len(results.misplaced_items)) / total_expected * 100)
                    st.metric("Compliance Score", f"{compliance_score:.1f}%")
    
    with tab2:
        create_planogram_config()

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