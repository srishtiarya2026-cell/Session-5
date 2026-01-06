import streamlit as st
import os
import tempfile
from markitdown import MarkItDown
import requests

# App Configuration
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄", layout="wide")

def get_file_size(size_in_bytes):
    """Converts bytes to a human-readable string (MB)."""
    return round(size_in_bytes / (1024 * 1024), 2)

def main():
    st.title("📄 Universal Document-to-Text Converter")
    
    # Initialize Engine
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (UniversalDocConverter/1.0)"})
    md = MarkItDown(requests_session=session)

    # Upload Area
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        type=["docx", "xlsx", "pptx", "pdf", "html", "zip"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            current_file_name = uploaded_file.name
            base_name = os.path.splitext(current_file_name)[0]
            extension = os.path.splitext(current_file_name)[1]
            
            # Get original size
            original_size_bytes = uploaded_file.size
            original_size_mb = get_file_size(original_size_bytes)

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name

                with st.spinner(f"Processing {current_file_name}..."):
                    result = md.convert(tmp_file_path)
                    converted_text = result.text_content
                
                # Calculate converted size
                converted_size_bytes = len(converted_text.encode('utf-8'))
                converted_size_mb = get_file_size(converted_size_bytes)
                
                # Calculate percentage reduction
                if original_size_bytes > 0:
                    reduction = ((original_size_bytes - converted_size_bytes) / original_size_bytes) * 100
                else:
                    reduction = 0

                # Create Tabs for the specific file
                tab1, tab2 = st.tabs(["📝 Conversion & Preview", "📊 File Size Comparison"])

                with tab1:
                    st.text_area("Content", value=converted_text, height=300, key=f"txt_{current_file_name}")
                    c1, c2 = st.columns(2)
                    c1.download_button("Download MD", converted_text, f"{base_name}.md", "text/markdown", key=f"md_{current_file_name}")
                    c2.download_button("Download TXT", converted_text, f"{base_name}.txt", "text/plain", key=f"txt_{current_file_name}")

                with tab2:
                    st.subheader(f"Storage Metrics: {current_file_name}")
                    
                    # Create the comparison table
                    metrics_data = {
                        "File State": ["Original File", "Converted Text File"],
                        "Size (MB)": [f"{original_size_mb} MB", f"{converted_size_mb} MB"]
                    }
                    st.table(metrics_data)

                    # Show the percentage highlight
                    if reduction > 0:
                        st.success(f"✨ **Text version is {reduction:.1f}% smaller** than the original file.")
                    else:
                        st.info("The file size remained roughly the same.")

                os.remove(tmp_file_path)

            except Exception as e:
                st.error(f"⚠️ Could not read {current_file_name}. Please check the format.")
                with st.sidebar:
                    st.warning(f"Technical Log for {current_file_name}:")
                    st.code(str(e))

if __name__ == "__main__":
    main()
