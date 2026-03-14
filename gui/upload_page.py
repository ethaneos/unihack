import streamlit as st

def show_upload_page(manager):
    st.header("Upload")

    uploaded_file = st.file_uploader("Upload a CSV", type="csv", accept_multiple_files=True)
    if uploaded_file is not None:
        st.caption("File uploaded")
    
    with st.sidebar:
        st.markdown("#")