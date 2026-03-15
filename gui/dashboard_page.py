import streamlit as st

def show_dashboard_page(manager):

    st.title("WTH am I paying for???", text_alignment='center')
    st.header("Welcome to Subscription Leak Detector! ✨", text_alignment='center')

    with st.container():
        st.markdown('<p style="z-index:100; font-family:sans-serif; font-size: 150%;">' \
        'Made for Unihack 2026, WTF am I paying for??? searches through your estatements and finds out what you\'re paying for!' \
        '</p>', unsafe_allow_html=True, text_alignment='center')

        _, col1, _ = st.columns(3)
        with col1:
            if st.button("Find my subscriptions", type="primary", width="stretch"):

                st.success("Let's a go!")
                st.switch_page(manager.upload_page)
        
        st.markdown('<p style="z-index:100; font-family:sans-serif; font-size: 90%;">' \
        'The average household manages 3 subscriptions per month just for streaming.<br> ' \
        'Think of the services you currently pay for; can you remember them all?<br> ' \
        'This is where our app comes in to help find them for you.'
        '</p>', unsafe_allow_html=True, text_alignment='center')