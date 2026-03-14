import streamlit as st
import pandas as pd

def show_upload_page(manager):
    st.header("Upload")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded_file = st.file_uploader("Upload a CSV", type="csv", accept_multiple_files=False)
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df)
    
    with st.sidebar:
        st.markdown("#")