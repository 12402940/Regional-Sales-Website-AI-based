import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import os
import random
from streamlit_lottie import st_lottie

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def get_random_lottie():
    lottie_urls = [
        "https://lottie.host/6d228f36-2a40-4c16-8b1b-3c4c12e60d09/YLz0zA2A2D.json",  # Data Visualization
        "https://lottie.host/cc5d43c5-60b4-47e0-9f14-9ef6b6cb5a73/QhQK5cK1Cq.json",  # Dashboard UI
        "https://lottie.host/6d9e12dc-8ff9-4c9f-ae0b-b8b7ab63c36e/EaC3JtMXyZ.json",  # Global Network
        "https://lottie.host/28516f1e-59f7-40e5-a88b-69efad6817aa/lottie.json"       # Data Flow
    ]
    return load_lottieurl(random.choice(lottie_urls))

lottie_viz = get_random_lottie()

def save_chart(fig, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    fig.savefig(filepath, bbox_inches="tight")
    return filepath


def show():
    st.set_page_config(page_title="Regional Sales Dashboard", layout="wide")
    st.title("📊 Regional Sales Dashboard")

    if lottie_viz:
        st_lottie(lottie_viz, height=120, key="viz_anim")

    if "uploaded_data" in st.session_state:
        df = st.session_state["uploaded_data"]

       
        st.sidebar.header("🔽 Filters")

        if "Year" in df.columns:
            year_filter = st.sidebar.multiselect(
                "Select Year(s)",
                sorted(df["Year"].unique()),
                default=df["Year"].unique()
            )
            df = df[df["Year"].isin(year_filter)]

        if "Region" in df.columns:
            region_filter = st.sidebar.multiselect(
                "Select Region(s)",
                df["Region"].unique(),
                default=df["Region"].unique()
            )
            df = df[df["Region"].isin(region_filter)]

        if "Product" in df.columns:
            product_filter = st.sidebar.multiselect(
                "Select Product(s)",
                df["Product"].unique(),
                default=df["Product"].unique()
            )
            df = df[df["Product"].isin(product_filter)]

        
        total_revenue = df["Revenue"].sum() if "Revenue" in df.columns else None
        pipeline = df["Pipeline"].sum() if "Pipeline" in df.columns else None
        revenue_goal = df["RevenueGoal"].sum() if "RevenueGoal" in df.columns else None
        forecast = (total_revenue / revenue_goal * 100) if total_revenue and revenue_goal else None

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("💰 Revenue Won", f"${total_revenue:,.2f}" if total_revenue else "N/A")
        kpi2.metric("📦 Qualified Pipeline", f"${pipeline:,.2f}" if pipeline else "N/A")
        kpi3.metric("🎯 Revenue Goal", f"${revenue_goal:,.2f}" if revenue_goal else "N/A")
        kpi4.metric("📈 Forecast %", f"{forecast:.1f}%" if forecast else "N/A")

        st.markdown("---")

        # ------------------------------
        
        row1_col1, row1_col2 = st.columns([1.5, 1])
        row2_col1, row2_col2 = st.columns([1.5, 1])

        with row1_col1:
            st.subheader("🔄 Revenue by Sales Stage")
            if {"Stage", "Revenue"}.issubset(df.columns):
                stage_rev = df.groupby("Stage")["Revenue"].sum().reset_index()
                fig = px.funnel(
                    stage_rev,
                    x="Revenue",
                    y="Stage",
                    color="Stage",
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚠️ No Stage/Revenue columns found for this chart.")

        with row1_col2:
            st.subheader("📦 Revenue Won & Pipeline by Product")
            if {"Product", "Revenue", "Pipeline"}.issubset(df.columns):
                prod = df.groupby("Product")[["Revenue", "Pipeline"]].sum().reset_index()
                fig = px.bar(
                    prod,
                    x="Product",
                    y=["Revenue", "Pipeline"],
                    barmode="group",
                    title="Revenue vs Pipeline"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚠️ No Product/Revenue/Pipeline columns found for this chart.")

        with row2_col1:
            st.subheader("🌍 Forecast by Territory")
            if {"Region", "Revenue", "Latitude", "Longitude"}.issubset(df.columns):
                region_sales = df.groupby(["Region", "Latitude", "Longitude"])["Revenue"].sum().reset_index()
                try:
                    fig = px.scatter_geo(
                        region_sales,
                        lat="Latitude",
                        lon="Longitude",
                        text="Region",
                        size="Revenue",
                        color="Revenue",
                        color_continuous_scale="Blues",
                        projection="natural earth",
                        title="Revenue by Region"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"⚠️ Could not render map. Reason: {e}")
            else:
                st.info("⚠️ No Region/Revenue/Latitude/Longitude columns found. Map cannot be displayed.")

        with row2_col2:
            st.subheader("📊 Forecast by Product")
            if {"Product", "Revenue", "Pipeline"}.issubset(df.columns):
                prod = df.groupby("Product")[["Revenue", "Pipeline"]].sum()
                prod["Forecast%"] = (prod["Revenue"] / prod["Pipeline"].replace(0, 1)) * 100
                st.dataframe(prod.reset_index())
            else:
                st.info("⚠️ No Product/Revenue/Pipeline columns found. Forecast table cannot be displayed.")

        st.markdown("---")
        st.subheader("📈 Extra Analysis")

        if "Revenue" in df.columns:
            fig = px.box(df, y="Revenue", title="Revenue Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Revenue column not found. Box plot cannot be displayed.")

        if lottie_viz:
            st_lottie(lottie_viz, height=200, key="upload_prompt")

    else:
        st.warning("⚠️ No dataset uploaded yet.")
        st.info("➡️ Go to the **Upload Data** page to upload your sales data.")
