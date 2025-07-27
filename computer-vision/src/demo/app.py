import streamlit as st
import pandas as pd
from PIL import Image
import os
import json
import tempfile
from backend.planogram_analyzer import PlanogramAnalyzer
from backend.config import PlanogramConfig
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
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
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
                        except:
                            pass
                            
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
            if results['annotated_image'] is not None:
                # Create a resized version for display
                display_image = _resize_image_for_display(results['annotated_image'], max_width=1080)
                
                # Center the image using columns
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(display_image, caption="Detected Items")
            
            # Results in tabs (reordered: All Detections → Misplaced → Inventory → Tasks → Summary)
            results_tab1, results_tab2, results_tab3, results_tab4, results_tab5 = st.tabs([
                "📦 All Detections",
                "❌ Misplaced Items", 
                "📈 Inventory Status",
                "📋 Tasks",
                "📄 Summary"
            ])
            
            with results_tab1:
                st.subheader("All Detected Items")
                if not results['detected_items'].empty:
                    st.dataframe(results['detected_items'], use_container_width=True)
                    st.info(f"Total items detected: {len(results['detected_items'])}")
                    
                    # Detection summary by item type
                    if 'class_name' in results['detected_items'].columns:
                        item_counts = results['detected_items']['class_name'].value_counts()
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
                    if 'section_id' in results['detected_items'].columns:
                        section_counts = results['detected_items']['section_id'].value_counts()
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
                if not results['misplaced_items'].empty:
                    st.dataframe(results['misplaced_items'], use_container_width=True)
                    st.error(f"Found {len(results['misplaced_items'])} misplaced items!")
                    
                    # Misplaced items by expected section
                    if 'expected_section' in results['misplaced_items'].columns:
                        misplaced_counts = results['misplaced_items']['expected_section'].value_counts()
                        st.subheader("Misplaced Items by Target Section")
                        for section, count in misplaced_counts.items():
                            st.warning(f"**{section}**: {count} items need relocation")
                else:
                    st.success("No misplaced items detected!")
            
            with results_tab3:
                st.subheader("Inventory Status")
                if not results['inventory_status'].empty:
                    st.dataframe(results['inventory_status'], use_container_width=True)
                    
                    # Inventory status summary
                    if 'status' in results['inventory_status'].columns:
                        status_counts = results['inventory_status']['status'].value_counts()
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("In Stock", status_counts.get('In Stock', 0))
                        with col2:
                            st.metric("Low Stock", status_counts.get('Low Stock', 0))
                        with col3:
                            st.metric("Out of Stock", status_counts.get('Out of Stock', 0))
                        with col4:
                            st.metric("Overstock", status_counts.get('Overstock', 0))
                    
                    # Highlight critical issues
                    out_of_stock = results['inventory_status'][
                        results['inventory_status']['status'] == 'Out of Stock'
                    ]
                    if not out_of_stock.empty:
                        st.error(f"⚠️ {len(out_of_stock)} sections are out of stock!")
                        st.dataframe(out_of_stock[['section_name', 'expected_count']], use_container_width=True)
                else:
                    st.info("No inventory data available.")
            
            with results_tab4:
                st.subheader("Recommended Tasks")
                if not results['tasks'].empty:
                    st.dataframe(results['tasks'], use_container_width=True)
                    
                    # Task priority and type summary
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'priority' in results['tasks'].columns:
                            st.subheader("By Priority")
                            priority_counts = results['tasks']['priority'].value_counts()
                            st.metric("🔴 High Priority", priority_counts.get('High', 0))
                            st.metric("🟡 Medium Priority", priority_counts.get('Medium', 0))
                            st.metric("🟢 Low Priority", priority_counts.get('Low', 0))
                    
                    with col2:
                        if 'task_type' in results['tasks'].columns:
                            st.subheader("By Type")
                            type_counts = results['tasks']['task_type'].value_counts()
                            for task_type, count in type_counts.items():
                                st.metric(f"{task_type}", count)
                else:
                    st.success("No tasks required!")
            
            with results_tab5:
                st.subheader("Analysis Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Detections", 
                        len(results['detected_items']) if not results['detected_items'].empty else 0
                    )
                
                with col2:
                    st.metric(
                        "Misplaced Items", 
                        len(results['misplaced_items']) if not results['misplaced_items'].empty else 0
                    )
                
                with col3:
                    st.metric(
                        "Pending Tasks", 
                        len(results['tasks']) if not results['tasks'].empty else 0
                    )
                
                with col4:
                    out_of_stock_count = len(results['inventory_status'][
                        results['inventory_status']['status'] == 'Out of Stock'
                    ]) if not results['inventory_status'].empty else 0
                    st.metric("Out of Stock", out_of_stock_count)
                
                # Compliance score
                if not results['detected_items'].empty:
                    total_expected = len(st.session_state.analyzer.config.sections) if st.session_state.analyzer.config else 1
                    compliance_score = max(0, (total_expected - len(results['misplaced_items'])) / total_expected * 100)
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