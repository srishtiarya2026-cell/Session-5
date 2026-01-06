import streamlit as st
import os
import tempfile
from markitdown import MarkItDown
import requests

# App Configuration
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄", layout="wide")

def get_file_size_mb(size_in_bytes):
    """Converts bytes to MB string."""
    return round(size_in_bytes / (1024 * 1024), 4)

def main():
    st.title("📄 Universal Document-to-Text Converter")
    st.markdown("Convert Office docs, PDFs, and HTML to Markdown instantly.")

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
            # Capture file details immediately
            fname = uploaded_file.name
            original_size_bytes = uploaded_file.size
            base_name = os.path.splitext(fname)[0]
            extension = os.path.splitext(fname)[1]
            
            # Place processing inside a container for clean UI per file
            with st.container():
                try:
                    # 1. Process File
                    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name

                    with st.spinner(f"Converting {fname}..."):
                        result = md.convert(tmp_path)
                        text_out = result.text_content
                    
                    # 2. Calculate Stats
                    converted_size_bytes = len(text_out.encode('utf-8'))
                    reduction = ((original_size_bytes - converted_size_bytes) / original_size_bytes) * 100

                    # 3. Display Tabs
                    t1, t2 = st.tabs(["📝 Conversion & Preview", "📊 File Size Comparison"])
                    
                    with t1:
                        st.text_area("Markdown Content", value=text_out, height=300, key=f"area_{fname}")
                        c1, c2 = st.columns(2)
                        c1.download_button("Download .md", text_out, f"{base_name}_converted.md", "text/markdown", key=f"md_{fname}")
                        c2.download_button("Download .txt", text_out, f"{base_name}_converted.txt", "text/plain", key=f"txt_{fname}")

                    with t2:
                        st.subheader("Efficiency Metrics")
                        # Create Comparison Table
                        st.table({
                            "Version": ["Original File", "Converted Text"],
                            "Size (MB)": [f"{get_file_size_mb(original_size_bytes)} MB", f"{get_file_size_mb(converted_size_bytes)} MB"]
                        })
                        st.success(f"📈 **Text version is {reduction:.1f}% smaller** than the original!")

                    # Cleanup
                    os.remove(tmp_path)

                except Exception as e:
                    # This error now ONLY shows if the 'try' block fails
                    st.error(f"⚠️ Could not read {fname}. Please check the format.")
                    with st.expander("View Error Details"):
                        st.code(str(e))

if __name__ == "__main__":
    main()
