import streamlit as st

def show_dashboard_page(manager):

    st.title(":white[WTH am I paying for???]")
    st.header(":white[Welcome to Subscription Leak Detector!] ✨")

    with st.container():

        st.markdown(":white[The average household manages **3** subscriptions per month just for streaming.]")
        st.markdown(":white[Think of the services you currently pay for; can you remember them all? This is where SLD comes in to find them for you.]")
        if st.button("Find my subscriptions", type="primary", width="content"):

            st.success("Let's a go!")
            st.switch_page(manager.upload_page)
    
    with st.sidebar:
        st.markdown("#")
