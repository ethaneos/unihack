import streamlit as st
from app.app import AppManager
from pages.home_page import show_home_page
from pages.upload_page import show_upload_page
from pages.analysis_page import show_analysis_page
from pages.settings_page import show_settings_page

def home_page():
    show_home_page(st.session_state.manager)

def upload_page():
    show_upload_page(st.session_state.manager)

def analysis_page():
    show_analysis_page(st.session_state.manager)

def settings_page():
    show_settings_page(st.session_state.manager)
        
def launch():
    st.set_page_config(layout="wide", page_title="Unihack project")

    # Instantiate the "brain" of our app ONCE and store it in the session state.
    # This is crucial so the manager object persists as we switch pages.
    if 'manager' not in st.session_state:
        st.session_state.manager = AppManager()

    pages_list = [
        st.Page(home_page, title="Home Page", url_path="home"),
        st.Page(upload_page, title="Upload Page", url_path="upload"),
        st.Page(analysis_page, title="Analysis Page", url_path="analysis"),
        st.Page(settings_page, title="Settings Page", url_path="settings"),
    ]

    st.html("""
        <style>
        .stAppHeader span {
            color: white !important;
            font-size: 24px;
            margin: 10px;
        }
        </style>

        """)

    all_page = st.navigation(pages_list, position = "top")
    all_page.run()
