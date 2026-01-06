import streamlit as st
import os
import tempfile
from markitdown import MarkItDown
import requests

# App Configuration
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄", layout="wide")

def main():
    st.title("📄 Universal Document-to-Text Converter")
    st.markdown("Upload any Office doc, PDF, or HTML file to convert it into clean Markdown.")

    # Initialize Engine with specific session settings
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
            # Define variable immediately inside the loop to avoid NameError
            current_file_name = uploaded_file.name
            base_name = os.path.splitext(current_file_name)[0]
            extension = os.path.splitext(current_file_name)[1]
            
            try:
                # Use a temporary file to handle the conversion safely
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name

                with st.spinner(f"Processing {current_file_name}..."):
                    # The actual conversion engine call
                    result = md.convert(tmp_file_path)
                    converted_text = result.text_content

                # UI: Preview and Downloads
                with st.expander(f"✅ Preview: {current_file_name}", expanded=True):
                    st.text_area("Content", value=converted_text, height=300, key=f"txt_{current_file_name}")

                    c1, c2 = st.columns(2)
                    c1.download_button("Download MD", converted_text, f"{base_name}.md", "text/markdown", key=f"md_dl_{current_file_name}")
                    c2.download_button("Download TXT", converted_text, f"{base_name}.txt", "text/plain", key=f"txt_dl_{current_file_name}")

                # Clean up the temp file
                os.remove(tmp_file_path)

            except Exception as e:
                # Fixed NameError by using current_file_name which is guaranteed to exist here
                st.error(f"⚠️ Could not read {current_file_name}. Please check the format.")
                # Developer hint: This shows you the underlying reason for the PDF failure
                with st.sidebar:
                    st.warning(f"Technical Log for {current_file_name}:")
                    st.code(str(e))

if __name__ == "__main__":
    main()
