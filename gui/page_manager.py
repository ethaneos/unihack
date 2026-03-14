import streamlit as st
from app.app import AppManager
from gui.dashboard_page import show_dashboard_page
from gui.upload_page import show_upload_page
from gui.analysis_page import show_analysis_page
from gui.settings_page import show_settings_page

def launch():
    st.set_page_config(layout="wide", page_title="Unihack project")

    # Instantiate the "brain" of our app ONCE and store it in the session state.
    # This is crucial so the manager object persists as we switch pages.
    if 'manager' not in st.session_state:
        st.session_state.manager = AppManager()

    def dashboard_page():
        show_dashboard_page(st.session_state.manager)

    def upload_page():
        show_upload_page(st.session_state.manager)

    def analysis_page():
        show_analysis_page(st.session_state.manager)
    
    def settings_page():
        show_settings_page(st.session_state.manager)

    pages_list = [
        st.Page(dashboard_page, title="Dashboard", url_path="home"),
        st.Page(upload_page, title="Upload", url_path="upload"),
        st.Page(analysis_page, title="Analysis", url_path="analysis"),
        st.Page(settings_page, title="Settings", url_path="settings"),
    ]

    st.session_state.manager.upload_page = pages_list[1]

    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #e0f7da 0%, #66bb6a 100%);
            overflow: hidden;
        }}
        #bgCanvas {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1;
        }}
        </style>
        <canvas id="bgCanvas"></canvas>
        """, unsafe_allow_html=True)
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