import streamlit as st

def show_home_page(manager):
    st.header("Home Page")
    st.write("Welcome to Subscription Leak Detector!")

    col1 = st.columns(1)

    with col1:
        st.button("test button", type="primary", use_container_width=True)

    input = st.text_input("What is your name?")#text box
    
    if st.button("Say Hello"):
        if input:
            st.write(f"Hello, {input}!")
        else:
            st.warning("Please enter a name first.")
    
    with st.sidebar:
        st.markdown("#")
