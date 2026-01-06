import tempfile # Add this to your imports at the top

# ... inside your 'if uploaded_files:' loop ...
try:
    # Use a temporary file to avoid permission/cleanup issues
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name

    with st.spinner(f"Processing {file_name}..."):
        # Convert using the path to the temp file
        result = md.convert(tmp_file_path)
        converted_text = result.text_content

    # ... rest of your preview and download code ...

    # Cleanup the temp file path
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)

except Exception as e:
    st.error(f"⚠️ Could not read {file_name}. Please check the format.")
    # For debugging: uncomment the line below to see exactly WHY it failed
    # st.exception(e)
