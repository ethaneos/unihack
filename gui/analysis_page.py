import streamlit as st

def show_analysis_page(manager):
    st.header("Analysis")

    def show__quiz():

        # 1. Initialize  State
        if 'current_node' not in st.session_state:
            st.session_state.current_node = "start"
        if 'history' not in st.session_state:
            st.session_state.history = {}

        # 2. Define the Branching Logic (The Story Tree)
        # Each node can lead to different nodes based on the choice
        service = "[Placeholder]"
        story_tree = {
            "start": {
                "text": f"Think of {service}. How many times have you used this in the last month?",
                "type": "numeric",
                "threshold": 9,
                "if_above": "heavy_user",
                "if_below": "casual_user"
            },
            "heavy_user": {
                "text": "You use this service quite often. I guess it's alright for you to keep it.",
                "type": "end",
            },
            "casual_user": {
                "text": "Do you think this subscription is worth the $$ it cost you this month?",
                "type": "choice",
                "yes_next": "big_spender",
                "no_next": "lose_it"
            },
            "keep_it": {
                "text": "I guess you can keep it.",
                "type": "confirm"
            },
            "lose_it": {
                "text": "You should probably unsubscribe.",
                "type": "confirm"
            }
        }

        # CSS for the Red/Green buttons
        st.markdown("""
            <style>
                div.stButton > button[key^="yes"] { background-color: #28a745 !important; color: white !important; }
                div.stButton > button[key^="no"] { background-color: #dc3545 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        # 3. Render Current Node
        node_id = st.session_state.current_node
        
        # Check if we've reached an "End Node" (not in the tree)
        if node_id not in story_tree:
            st.success(f"🏁 Path Complete: {node_id.replace('_', ' ').title()}")
            if st.button("Restart"):
                st.session_state.current_node = "start"
                st.session_state.history = {}
                st.rerun()
            return

        node = story_tree[node_id]
        st.subheader("Do you need it?")
        st.write(f"### {node['text']}")

        # 4. Handle Different Question Types
        if node["type"] == "numeric":
            val = st.number_input("Enter amount", min_value=0, step=1)
            if st.button("Confirm Amount", use_container_width=True):
                st.session_state.history[node_id] = val
                st.session_state.current_node = node["if_above"] if val > node["threshold"] else node["if_below"]
                st.rerun()

        elif node["type"] == "choice":
            col1, col2, _, _ = st.columns(4)
            with col1:
                if st.button("Yes", key=f"yes_{node_id}", use_container_width=True):
                    st.session_state.history[node_id] = "Yes"
                    st.session_state.current_node = node["yes_next"]
                    st.rerun()
            with col2:
                if st.button("No", key=f"no_{node_id}", use_container_width=True):
                    st.session_state.history[node_id] = "No"
                    st.session_state.current_node = node["no_next"]
                    st.rerun()
        elif node["type"] == "confirm":
            _, col1, _ = st.columns(3)
            with col1:
                if st.button("Confirm", key=f"confirm_{node_id}", use_container_width=True):
                    st.rerun()

    # Call in your page
    show__quiz()

#guess total: reveal all in table