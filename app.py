import streamlit as st
import os
import tempfile
from pathlib import Path
import logging
from typing import Optional
import time

# Import our custom modules
from main import TikTokTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="TikTok Video Translator & Makeup Transformer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #4ECDC4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
    .progress-bar {
        margin: 1rem 0;
    }
    .download-button {
        background-color: #FF6B6B;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🎬 TikTok Video Translator & Makeup Transformer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Processing options
        st.markdown("### Processing Options")
        enable_translation = st.checkbox("Enable Audio Translation", value=True, help="Translate Spanish audio to English")
        enable_makeup = st.checkbox("Enable Makeup Transformation", value=True, help="Transform Latino makeup to American style")
        
        # Quality settings
        st.markdown("### Quality Settings")
        video_quality = st.selectbox(
            "Video Quality",
            ["High (1080p)", "Medium (720p)", "Low (480p)"],
            index=1
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            batch_processing = st.checkbox("Enable Batch Processing", value=False)
            preserve_original = st.checkbox("Preserve Original Audio", value=False)
            custom_output_dir = st.text_input("Custom Output Directory", value="output")
    
    # Main content
    if batch_processing:
        render_batch_processing(enable_translation, enable_makeup, video_quality, custom_output_dir)
    else:
        render_single_processing(enable_translation, enable_makeup, video_quality, custom_output_dir)

def render_single_processing(enable_translation: bool, enable_makeup: bool, video_quality: str, output_dir: str):
    """Render single video processing interface."""
    
    st.markdown('<h2 class="sub-header">📹 Single Video Processing</h2>', unsafe_allow_html=True)
    
    # File upload
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a TikTok video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
        help="Upload a TikTok video file to process"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Display video info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Video Information")
            file_size = uploaded_file.size / (1024 * 1024)  # MB
            st.write(f"**File Name:** {uploaded_file.name}")
            st.write(f"**File Size:** {file_size:.2f} MB")
            st.write(f"**File Type:** {uploaded_file.type}")
        
        with col2:
            st.markdown("### 🎯 Processing Options")
            st.write(f"**Translation:** {'✅ Enabled' if enable_translation else '❌ Disabled'}")
            st.write(f"**Makeup Transform:** {'✅ Enabled' if enable_makeup else '❌ Disabled'}")
            st.write(f"**Quality:** {video_quality}")
        
        # Process button
        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
            process_single_video(uploaded_file, enable_translation, enable_makeup, video_quality, output_dir)

def render_batch_processing(enable_translation: bool, enable_makeup: bool, video_quality: str, output_dir: str):
    """Render batch processing interface."""
    
    st.markdown('<h2 class="sub-header">📁 Batch Video Processing</h2>', unsafe_allow_html=True)
    
    # Directory upload
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose multiple TikTok video files",
        type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
        accept_multiple_files=True,
        help="Upload multiple TikTok video files to process in batch"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.markdown("### 📋 Selected Files")
        for i, file in enumerate(uploaded_files):
            file_size = file.size / (1024 * 1024)  # MB
            st.write(f"{i+1}. **{file.name}** ({file_size:.2f} MB)")
        
        # Process button
        if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
            process_batch_videos(uploaded_files, enable_translation, enable_makeup, video_quality, output_dir)

def process_single_video(uploaded_file, enable_translation: bool, enable_makeup: bool, video_quality: str, output_dir: str):
    """Process a single uploaded video."""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        status_text.text("📁 File saved to temporary location...")
        progress_bar.progress(10)
        
        # Initialize transformer
        transformer = TikTokTransformer()
        status_text.text("🔧 Initializing video processor...")
        progress_bar.progress(20)
        
        # Process video
        status_text.text("🎬 Processing video...")
        progress_bar.progress(30)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate output filename
        output_filename = f"{Path(uploaded_file.name).stem}_translated.mp4"
        output_filepath = str(output_path / output_filename)
        
        # Process the video
        processed_path = transformer.process_video(temp_path, output_filepath)
        progress_bar.progress(90)
        
        # Cleanup temporary file
        os.unlink(temp_path)
        progress_bar.progress(100)
        
        # Success message
        status_text.text("✅ Processing complete!")
        
        # Display results
        st.success("🎉 Video processed successfully!")
        
        # Download section
        st.markdown("### 📥 Download Processed Video")
        
        with open(processed_path, "rb") as file:
            st.download_button(
                label="⬇️ Download Processed Video",
                data=file.read(),
                file_name=output_filename,
                mime="video/mp4",
                use_container_width=True
            )
        
        # Display video preview
        st.markdown("### 🎥 Preview")
        st.video(processed_path)
        
    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        logger.error(f"Error processing video: {e}")
    finally:
        # Cleanup
        try:
            transformer.cleanup()
        except:
            pass

def process_batch_videos(uploaded_files, enable_translation: bool, enable_makeup: bool, video_quality: str, output_dir: str):
    """Process multiple uploaded videos."""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    processed_files = []
    temp_files = []
    
    try:
        # Initialize transformer
        transformer = TikTokTransformer()
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"📁 Processing {uploaded_file.name} ({i+1}/{len(uploaded_files)})...")
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
                temp_files.append(temp_path)
            
            # Generate output filename
            output_filename = f"{Path(uploaded_file.name).stem}_translated.mp4"
            output_filepath = str(output_path / output_filename)
            
            # Process the video
            processed_path = transformer.process_video(temp_path, output_filepath)
            processed_files.append(processed_path)
            
            # Update progress
            progress = (i + 1) / len(uploaded_files) * 100
            progress_bar.progress(progress)
        
        status_text.text("✅ Batch processing complete!")
        
        # Success message
        st.success(f"🎉 Successfully processed {len(processed_files)} videos!")
        
        # Display results
        st.markdown("### 📋 Processed Videos")
        for i, processed_file in enumerate(processed_files):
            filename = Path(processed_file).name
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i+1}. **{filename}**")
            with col2:
                with open(processed_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Download",
                        data=file.read(),
                        file_name=filename,
                        mime="video/mp4",
                        key=f"download_{i}"
                    )
        
    except Exception as e:
        st.error(f"❌ Error during batch processing: {str(e)}")
        logger.error(f"Error during batch processing: {e}")
    finally:
        # Cleanup
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        try:
            transformer.cleanup()
        except:
            pass

def render_features():
    """Render feature highlights."""
    
    st.markdown("## ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🎤 Audio Translation</h3>
            <p>Automatically translate Spanish audio to English using advanced speech recognition and synthesis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>💄 Makeup Transformation</h3>
            <p>Transform Latino makeup styles to American mainstream looks using AI-powered style transfer.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>🎬 Video Processing</h3>
            <p>High-quality video processing with face detection and real-time makeup application.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Render features at the top
    render_features()
    
    # Main application
    main()