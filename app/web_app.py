import streamlit as st
from gui.webpages import (
    dashboard_page,
    upload_page,
    ai_copilot,
    reports_page,
    visualize_page,
    ai_prediction,
    login_page
)
from streamlit_lottie import st_lottie
import requests
import random

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def get_random_lottie():
    lottie_urls = [
        "https://lottie.host/472747a3-53cc-4700-91de-4da2f0b63de8/x8WqO9w6mD.json",  
        "https://lottie.host/33c82303-1b77-4e7c-b58a-6c4df3096dcf/EJQ1kA1wT7.json",  
        "https://lottie.host/5d8c4f87-848a-49da-8f89-2edcd65399e4/4kqzIksgkK.json",  
        "https://lottie.host/2c71237f-1b04-4fa8-bf52-65dffebc5e13/Ht2ySYRmm2.json"   
    ]
    return load_lottieurl(random.choice(lottie_urls))

lottie_menu = get_random_lottie()

# ---------------- Session Setup ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ---------------- Login Handling ----------------
if not st.session_state["logged_in"]:
    login_page.show()  
else:
    with st.sidebar:
        st.title("📌 Navigation")

        if lottie_menu:
            st_lottie(lottie_menu, height=120, key="menu_anim")

        page = st.radio(
            "Go to",
            ("Dashboard", "Upload Data", "Reports", "Visualizations", "AI Predictions", "AI Copilot"),
            format_func=lambda x: f"➡️ {x}"
        )

        st.markdown("---")
        st.sidebar.success(f"👤 Logged in as {st.session_state['username']}")

        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

    # ---------------- Page Routing ----------------
    if page == "Dashboard":
        dashboard_page.show()
    elif page == "Upload Data":
        upload_page.show()
    elif page == "Reports":
        reports_page.show()
    elif page == "Visualizations":
        visualize_page.show()
    elif page == "AI Predictions":
        ai_prediction.show()
    elif page == "AI Copilot":
        ai_copilot.show()
    else:
        st.error("Page not found.")
