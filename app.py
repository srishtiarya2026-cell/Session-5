import streamlit as st
import os
from markitdown import MarkItDown
import requests

# App Configuration
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄", layout="wide")

def main():
    st.title("📄 Universal Document-to-Text Converter")
    st.markdown("Upload any Office doc, PDF, or HTML file to convert it into clean Markdown.")

    # Initialize the Engine
    # MarkItDown allows passing a custom requests session for User-Agent/Timeout control
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (UniversalDocConverter/1.0)"})
    
    # We use a custom adapter or manual timeout isn't directly in MarkItDown's init, 
    # but we handle the engine calls safely below.
    md = MarkItDown(requests_session=session)

    # 1. Upload Area
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        type=["docx", "xlsx", "pptx", "pdf", "html", "zip"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            base_name = os.path.splitext(file_name)[0]
            
            try:
                # Save uploaded file to a temporary location for MarkItDown to process
                with open(file_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 2. The Engine Processing
                with st.spinner(f"Processing {file_name}..."):
                    # MarkItDown handles format detection automatically
                    # We wrap this in a timeout-capable logic if it were a URL, 
                    # but for local files it is near-instant.
                    result = md.convert(file_name)
                    converted_text = result.text_content

                # 3. Instant Preview
                with st.expander(f"✅ Preview: {file_name}", expanded=True):
                    st.text_area(
                        label="Converted Content",
                        value=converted_text,
                        height=300,
                        key=f"text_{file_name}"
                    )

                    # 4. Download Options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="Download as Markdown (.md)",
                            data=converted_text,
                            file_name=f"{base_name}_converted.md",
                            mime="text/markdown",
                            key=f"md_{file_name}"
                        )
                    
                    with col2:
                        st.download_button(
                            label="Download as Text (.txt)",
                            data=converted_text,
                            file_name=f"{base_name}_converted.txt",
                            mime="text/plain",
                            key=f"txt_{file_name}"
                        )

                # Cleanup temporary file
                os.remove(file_name)

            except Exception as e:
                # 5. Resilience / Error Handling
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                # Log the error for the developer (optional)
                # st.write(f"Error details: {e}")

if __name__ == "__main__":
    main()
