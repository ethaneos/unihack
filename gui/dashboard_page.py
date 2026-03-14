import streamlit as st

def show_dashboard_page(manager):

    st.header(":green[Welcome to Subscription Leak Detector!] ✨")
    
    with st.container():

        st.write(""":green[The average household manages 3 subscriptions per month just for streaming.<br>
        Think of all the services you currently pay for, can you remember them all? This is where SLD comes in to find them for you.]""")

        if st.button("Find my subscriptions", type="primary", width="stretch"):
            st.success("Let's a go!")
            st.switch_page("gui/upload_page.py")
    
    with st.sidebar:
        st.markdown("#")