import streamlit as st
import pandas as pd
from PIL import Image
import io
import os
from backend.planogram_analyzer import PlanogramAnalyzer
from backend.config import PlanogramConfig
from backend.planogram_annotator import PlanogramAnnotator

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

def main():
    st.title("🏪 Planogram Vision System Demo")
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

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of your store shelf/planogram to analyze"
        )
        
        if uploaded_file is not None:
            # Display uploaded image (resized for better display)
            image = Image.open(uploaded_file)
            
            # Resize image for display if too large
            display_image = _resize_image_for_display(image, max_width=600)
            st.image(display_image, caption="Uploaded Image", use_container_width=True)
            
            # Analyze button
            if st.button("🔍 Analyze Planogram", type="primary"):
                with st.spinner("Analyzing planogram..."):
                    # Convert PIL image to bytes for processing
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    
                    # Run analysis
                    results = st.session_state.analyzer.analyze_image(img_bytes)
                    st.session_state.analysis_results = results
                    st.success("Analysis complete!")
    
    with col2:
        st.header("📋 Current Planogram")
        
        # Display annotated planogram image if available
        if 'annotated_planogram_path' in st.session_state and st.session_state.annotated_planogram_path:
            if os.path.exists(st.session_state.annotated_planogram_path):
                planogram_image = Image.open(st.session_state.annotated_planogram_path)
                
                # Resize planogram for display
                display_image = _resize_image_for_display(planogram_image, max_width=600)
                st.image(display_image, caption="Expected Planogram Layout", use_container_width=True)
                
                # Show section summary
                if st.session_state.analyzer.config:
                    total_sections = len(st.session_state.analyzer.config.sections)
                    total_expected = sum(s.expected_count for s in st.session_state.analyzer.config.sections)
                    st.info(f"📊 {total_sections} sections • {total_expected} expected items")
            else:
                st.error("Annotated planogram image not found.")
        else:
            st.info("Please select a planogram configuration to view the expected layout.")

    # Results section
    if st.session_state.analysis_results is not None:
        st.header("📊 Analysis Results")
        results = st.session_state.analysis_results
        
        # Display annotated image (resized for better display)
        st.subheader("🎯 Detected Items (Annotated)")
        if results['annotated_image'] is not None:
            # Resize the annotated image for display
            display_image = _resize_image_for_display(results['annotated_image'], max_width=800)
            st.image(display_image, caption="Detected Items", use_container_width=True)
        
        # Results in tabs (reordered: All Detections → Misplaced → Inventory → Tasks → Summary)
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📦 All Detections",
            "❌ Misplaced Items", 
            "📈 Inventory Status",
            "📋 Tasks",
            "📄 Summary"
        ])
        
        with tab1:
            st.subheader("All Detected Items")
            if not results['detected_items'].empty:
                st.dataframe(results['detected_items'], use_container_width=True)
                st.info(f"Total items detected: {len(results['detected_items'])}")
                
                # Detection summary by section
                if 'section_id' in results['detected_items'].columns:
                    section_counts = results['detected_items']['section_id'].value_counts()
                    st.subheader("Detections by Section")
                    col1, col2 = st.columns(2)
                    for i, (section, count) in enumerate(section_counts.items()):
                        if section and section != 'None':  # Skip None/null sections
                            if i % 2 == 0:
                                with col1:
                                    st.metric(f"{section}", count)
                            else:
                                with col2:
                                    st.metric(f"{section}", count)
            else:
                st.warning("No items detected in the image.")
        
        with tab2:
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
        
        with tab3:
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
        
        with tab4:
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
        
        with tab5:
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
    
    # Only resize if image is larger than max_width
    if original_width <= max_width:
        return image
    
    # Calculate new dimensions maintaining aspect ratio
    aspect_ratio = original_height / original_width
    new_width = max_width
    new_height = int(max_width * aspect_ratio)
    
    # Resize using high-quality resampling
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_image

if __name__ == "__main__":
    main() 