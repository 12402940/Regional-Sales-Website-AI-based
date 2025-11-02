import streamlit as st
import os
from streamlit_lottie import st_lottie
import requests

REPORTS_DIR = "uploads"
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show():
    st.title("📑 Download Reports")

    animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json")
    if animation:
        st_lottie(animation, height=250, key="reports-animation")

    st.markdown("Download your **Visualizations** and **AI Prediction Reports** directly to your computer 📊💻")

    files = os.listdir(REPORTS_DIR)
    if files:
        for file in files:
            file_path = os.path.join(REPORTS_DIR, file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {file}",
                    data=f,
                    file_name=file,
                    mime="application/octet-stream",
                    key=f"download-{file}" 
                )
    else:
        st.info("📂 No reports generated yet. Please run visualizations or predictions first.")

    