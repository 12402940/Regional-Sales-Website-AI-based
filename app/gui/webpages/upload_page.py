import streamlit as st
import pandas as pd
import requests
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st_lottie = None
    st.warning("The 'streamlit_lottie' package is not installed. Please install it with 'pip install streamlit-lottie' to enable animations.")

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show():
    st.title("📂 Upload Sales Data")
    st.markdown("### Upload your CSV or Excel files for analysis")

    lottie_upload = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")

    col1, col2 = st.columns([1, 2])

    with col1:
        if lottie_upload:
            st_lottie(lottie_upload, key="upload", height=250)

    with col2:
        uploaded_file = st.file_uploader("📤 Upload CSV or Excel", type=["csv", "xlsx"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.session_state["uploaded_data"] = df

                st.success("✅ Data uploaded successfully!")
                st.dataframe(df.head())

            except Exception as e:
                st.error(f"❌ Error loading file: {e}")

    st.markdown("---")
    st.info("💡 Tip: Only CSV or Excel files are supported at the moment.")
    if "uploaded_data" in st.session_state:
        if st.button("Clear Uploaded Data"):
            del st.session_state["uploaded_data"]
            st.success("🗑️ Uploaded data cleared.")

