import streamlit as st
from app.app import AppManager

def launch():
    st.set_page_config(layout="wide", page_title="Unihack project")

    # Instantiate the "brain" of our app ONCE and store it in the session state.
    # This is crucial so the manager object persists as we switch pages.
    if 'manager' not in st.session_state:
        AppManager.init_file_path()
        st.session_state.manager = AppManager(AppManager.save_path)

    pages_list = []
    all_page = st.navigation(pages_list, position = "top")
    all_page.run()