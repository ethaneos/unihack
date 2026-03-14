import streamlit as st

def show_home_page(manager):

    st.header("Welcome to Subscription Leak Detector! ✨")
    
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f0fdf4; /* Very light mint green */
    }
    
    /* Style the metric cards */
    [data-testid="stMetricValue"] {
        color: #166534; /* Dark forest green */
    }
    
    /* Colorful Sidebar */
    [data-testid="stSidebar"] {
        background-color: #dcfce7; /* Soft pastel green */
    }
    </style>
    """, unsafe_allow_html = True)
    
    with st.container(border = True):
        st.write("""The average household manages 3 subscriptions per month just for streaming.
        Think of all the services you pay for, can you remember them all?
        This is where SLD comes in to find them for you.""")

        st.page_link("upload_page.py", label="View Your Subscriptions", icon="📊")
        
        
    
    with st.sidebar:
        st.markdown("#")
