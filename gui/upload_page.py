import streamlit as st
import pandas as pd

def show_upload_page(manager):
    st.header("Upload")

    uploaded_files = st.file_uploader("Upload a CSV", type="csv", accept_multiple_files=True)
    if uploaded_files is not None:
        for file in uploaded_files:
            df = pd.read_csv(file)
            st.write(df)
    
    with st.sidebar:
        st.markdown("#")