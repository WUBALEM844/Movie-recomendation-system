import streamlit as st
from services.firebase_client import get_client
from typing import Optional

client = get_client()


class SessionUser:
    def __init__(self, uid: str, email: str):
        self.uid = uid
        self.email = email


def login_ui() -> Optional[SessionUser]:
    """Render a compact login/signup widget in sidebar and return SessionUser or None."""
    if "user" not in st.session_state:
        st.session_state.user = None

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Account")

    if st.session_state.user:
        st.sidebar.write("✓ Signed in")
        if st.sidebar.button("Sign out"):
            st.session_state.user = None
            st.success("Signed out")
        return SessionUser(uid=st.session_state.user["localId"], email=st.session_state.user.get("email", ""))

    tab = st.sidebar.radio("", ["Sign in", "Sign up"], index=0)

    email = st.sidebar.text_input("Email", key="_auth_email")
    password = st.sidebar.text_input("Password", type="password", key="_auth_password")

    if tab == "Sign up":
        display_name = st.sidebar.text_input("Display name (optional)", key="_auth_display")
        if st.sidebar.button("Create account"):
            if not email or not password:
                st.sidebar.error("Email and password are required")
            else:
                try:
                    user = client.signup(email, password, display_name=display_name)
                    st.session_state.user = user
                    st.sidebar.success("Account created and signed in")
                    return SessionUser(uid=user.get("localId"), email=user.get("email"))
                except Exception as e:
                    st.sidebar.error(f"Signup failed: {e}")
                    return None

    else:
        if st.sidebar.button("Sign in"):
            if not email or not password:
                st.sidebar.error("Email and password are required")
            else:
                try:
                    user = client.login(email, password)
                    st.session_state.user = user
                    st.sidebar.success("Signed in")
                    return SessionUser(uid=user.get("localId"), email=user.get("email"))
                except Exception as e:
                    st.sidebar.error(f"Sign-in failed: {e}")
                    return None

    return None


def full_page_auth() -> Optional[SessionUser]:
    """Render a centered full-page sign in / sign up flow for first-time users.
    Returns a SessionUser when signed in, otherwise None.
    """
    if "user" not in st.session_state:
        st.session_state.user = None

    st.markdown(
        "<style>"
        "[data-testid='stAppViewContainer'] .main .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }"
        "[data-testid='stAppViewContainer'] .main { overflow: visible !important; }"
        "</style>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='width:100%; display:flex; justify-content:center; align-items:flex-start; margin:0; padding:0;'>", unsafe_allow_html=True)
    cols = st.columns([1, 0.95, 1])
    with cols[1]:
        st.markdown(
            "<div style='width:100%; max-width:520px; margin:24px 0 24px; padding:32px; background: rgba(17,24,39,0.95); border-radius:20px; box-shadow: 0 28px 80px rgba(0,0,0,0.45); overflow:hidden;'>"
            "<div style='margin-bottom:24px;'>"
            "<h2 style='color:#eef2ff; margin:0 0 10px; font-size:2rem;'>Welcome back</h2>"
            "<p style='margin:0; color:#cbd5e1; line-height:1.6;'>Sign in or create an account to continue to your personalized recommendations.</p>"
            "</div>"
            "<div style='padding:24px; background: rgba(10,14,25,0.92); border-radius:18px;'>",
            unsafe_allow_html=True,
        )
        tab = st.radio("", ["Sign in", "Sign up"], horizontal=True)

        email = st.text_input("Email", key="_fp_email")
        password = st.text_input("Password", type="password", key="_fp_password")

        if tab == "Sign up":
            display_name = st.text_input("Display name (optional)", key="_fp_display")
            if st.button("Create account"):
                if not email or not password:
                    st.error("Email and password are required")
                else:
                    try:
                        user = client.signup(email, password, display_name=display_name)
                        st.session_state.user = user
                        st.session_state.page = "Home"
                        st.success("Account created and signed in")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Signup failed: {e}")
        else:
            if st.button("Sign in"):
                if not email or not password:
                    st.error("Email and password are required")
                else:
                    try:
                        user = client.login(email, password)
                        st.session_state.user = user
                        st.session_state.page = "Home"
                        st.success("Signed in")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sign-in failed: {e}")

        st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return None


def add_favorite_ui(uid: str, movie: dict):
    try:
        ok = client.add_favorite(uid, movie)
        if ok:
            st.success("Added to favorites")
        else:
            st.error("Failed to add favorite")
    except Exception as e:
        st.error(f"Error: {e}")


def add_watchlist_ui(uid: str, movie: dict):
    try:
        ok = client.add_watchlist(uid, movie)
        if ok:
            st.success("Added to watchlist")
        else:
            st.error("Failed to add to watchlist")
    except Exception as e:
        st.error(f"Error: {e}")


def list_user_collections(uid: str):
    favs = client.list_favorites(uid)
    wl = client.list_watchlist(uid)
    return favs, wl
