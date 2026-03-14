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

    #gradient bg
    st.html(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #7fffd4 0%, #008000 200%);
            overflow: hidden;
        }}
        #bgCanvas {{
            position: absolute;
            top: 0;
            left: 0;
            z-index: -3;
        }}
        </style>
        <canvas id="bgCanvas"></canvas>
    """)
    #Bubbles
    st.html(f"""
    <div style="
        position: absolute; 
        top: 0; 
        right: 0; 
        width: 350px; 
        height: 350px;
    ">
        <div style="
            position: absolute;
            top: 0;
            right: 0;
            width: 250px; 
            height: 250px; 
            background: #90ee90;
            border-radius: 50%;
            opacity: 0.9;
            z-index: 2;
        "></div>

        <div style="
            position: absolute;
            top: 180px;
            right: 180px;
            width: 120px; 
            height: 120px; 
            background: #90ee90;
            border-radius: 50%;
            opacity: 0.5;
            z-index: 1;
        "></div>
    </div>
""")
    #Lines
    st.html(f"""
    <div style="
        position: fixed;
        bottom: 0vw;
        left: 10vw;
        width: 1300px;
        height: 900px;
        
        background: repeating-linear-gradient(
            45deg,
            rgba(127, 255, 212, 0.3),   /* Color 1 */
            rgba(127, 255, 212, 0.3) 2px, /* Line thickness */
            transparent 2px,             /* Start of gap */
            transparent 10px             /* End of gap/space between lines */
        );
    "></div>
""")
    #Header bar
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