import streamlit as st

def show_upload_page(manager):
    st.header("Upload")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded_file = st.file_uploader("Upload a CSV")
        if uploaded_file is not None:
            st.caption("File uploaded")
    
    with st.sidebar:
        st.markdown("#")