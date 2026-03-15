import streamlit as st

def show_dashboard_page(manager):

    st.title("WTH am I paying for???")
    st.header("Welcome to Subscription Leak Detector! ✨")

    with st.container():

        st.markdown('<p style="z-index:100; font-family:sans-serif; font-size: 150%;">' \
        'The average household manages 3 subscriptions per month just for streaming.<br>' \
        'Think of the services you currently pay for; can you remember them all?<br>' \
        'This is where our app comes in to help find them for you.'
        '</p>', unsafe_allow_html=True)
       
        if st.button("Find my subscriptions", type="primary", width="content"):

            st.success("Let's a go!")
            st.switch_page(manager.upload_page)
    
