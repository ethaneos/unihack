import streamlit as st

def show_home_page(manager):

    st.header(":green[Welcome to Subscription Leak Detector!] ✨")
    
    
    with st.container(border = True):
        st.write(""":lightgreen[The average household manages 3 subscriptions per month just for streaming.
        Think of all the services you pay for, can you remember them all?
        This is where SLD comes in to find them for you.]""")        
        
    
    with st.sidebar:
        st.markdown("#")
