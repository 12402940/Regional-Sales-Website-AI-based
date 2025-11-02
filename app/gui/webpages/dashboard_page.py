import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def show():
    st.title("🚀 Welcome to the Sales Dashboard")

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please login first.")
        return

    animation1 = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")
    animation2 = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_puciaact.json")
    animation3 = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_tll0j4bb.json")

    col1, col2 = st.columns(2)
    with col1:
        if animation1:
            st_lottie(animation1, height=250, key="analytics")
    with col2:
        st.markdown("""
        ### 📖 How to Use This Dashboard
        - 📂 **Upload Data** from the sidebar  
        - 📊 Explore **Reports & KPIs**  
        - 📈 Generate **Visualizations**  
        - 🤖 Try **AI Predictions** for insights  
        - 🧾 Download and export results  
        """)

    st.write("---")

    # Features Section
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        ### ✨ Key Features
        - Interactive charts & dashboards  
        - AI-powered forecasting  
        - Simple, clean, and modern UI  
        - Secure login system  
        - One-click export to Excel/CSV  
        """)
    with col4:
        if animation2:
            st_lottie(animation2, height=250, key="dataflow")

    st.write("---")

    if animation3:
        st_lottie(animation3, height=200, key="getstarted")
    st.success("✅ Use the sidebar menu to start exploring your sales data 🚀")
