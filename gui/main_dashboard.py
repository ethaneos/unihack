import streamlit as st
from app.app import AppManager
from gui.home_page import show_home_page

def launch():
    st.set_page_config(layout="wide", page_title="Unihack project")

    # Instantiate the "brain" of our app ONCE and store it in the session state.
    # This is crucial so the manager object persists as we switch pages.
    if 'manager' not in st.session_state:
        st.session_state.manager = AppManager()

    def home_page():
        show_home_page(st.session_state.manager)

    pages_list = [
        st.Page(home_page, title="Home Page", url_path="home"),
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