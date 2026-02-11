import streamlit as st

def login():
    """Display login form."""
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        return True

    st.header("🔐 User Login")
    username = st.text_input("Enter Username", key="login_username")
    if st.button("Login"):
        if username:
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Please enter a username")
    return False

def logout():
    """Logout user."""
    st.session_state.user = None
    st.session_state.current_collection = None
    st.session_state.messages = []
    st.rerun()

def get_current_user():
    return st.session_state.get("user")
