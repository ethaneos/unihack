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

    st.html(f"""
        <style>
            /* 1. Global App Background */
            .stApp {{
                background: linear-gradient(135deg, #7fffd4 0%, #008000 200%);
            }}

            /* 2. Header Text Color */
            .stAppHeader span {{
                color: white !important;
                font-size: 24px;
                margin: 10px;
            }}

            /* 3. The Canvas Background */
            #bgCanvas {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                z-index: -100;
                pointer-events: none;
            }}

            /* 4. Decorations Wrapper (Crucial for Z-Index) */
            .ui-decoration {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                z-index: 0; /* Sits behind the main app content */
                pointer-events: none; /* Allows clicking through to buttons */
            }}

            .bubble-main {{
                position: absolute;
                top: -5vw; right: -5vw;
                width: 25vw; height: 25vw;
                background: #90ee90;
                border-radius: 50%;
                opacity: 0.8;
            }}

            .bubble-sub {{
                position: absolute;
                top: 15vw; right: 15vw;
                width: 12vw; height: 12vw;
                background: #90ee90;
                border-radius: 50%;
                opacity: 0.4;
            }}

            .diagonal-lines {{
                position: absolute;
                bottom: 0; left: 0;
                width: 100vw; height: 100vw;
                background: repeating-linear-gradient(
                    45deg,
                    rgba(127, 255, 212, 0.3),
                    rgba(127, 255, 212, 0.3) 2px,
                    transparent 2px,
                    transparent 12px
                );
                -webkit-mask-image: radial-gradient(circle at bottom left, black 20%, transparent 80%);
            }}
        </style>

        <canvas id="bgCanvas"></canvas>
        
        <div class="ui-decoration">
            <div class="bubble-main"></div>
            <div class="bubble-sub"></div>
            <div class="diagonal-lines"></div>
        </div>
    """)
    
    all_page = st.navigation(pages_list, position = "top")
    all_page.run()