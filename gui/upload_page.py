import streamlit as st
import pandas as pd

def show_upload_page(manager):
    st.header("Upload")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        bank_name = st.selectbox(
            "Select your bank",
            ("Ubank", "Bank of Melbourne", "Westpac", "Macquarie", "Rabobank"),
            index=None,
            placeholder="Select banking provider...",
        )
        if bank_name:
            uploaded_file = st.file_uploader("Upload a CSV", type="csv", accept_multiple_files=False)
            if st.button("Analyse banking records", type="primary", width="stretch"):
                if uploaded_file is not None:
                    manager.analyse_bank_csv(bank_name.lower(), uploaded_file)
                else:
                    st.error("Please upload a CSV file before analysing.")
    
    with st.sidebar:
        st.markdown("#")