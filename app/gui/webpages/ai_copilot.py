# ai_copilot.py (updated with dynamic plots)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io, os, json, contextlib, joblib, re, time
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score

MODEL_PATH = "trained_ai_model.pkl"
MEMORY_PATH = "memory.json"

SYSTEM_PROMPT = (
    "You are a local Data Copilot that uses trained ML models and dataset analysis "
    "to answer business questions about sales, regions, products and provide charts."
)

# ---------------- MEMORY HELPERS ----------------
def load_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"insights": []}
    return {"insights": []}

def save_memory(mem):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)

def add_memory_entry(title, content):
    mem = load_memory()
    entry = {"title": title, "content": content, "timestamp": datetime.utcnow().isoformat()+"Z"}
    mem["insights"].insert(0, entry)
    mem["insights"] = mem["insights"][:50]
    save_memory(mem)

# ---------------- DATA HELPERS ----------------
def brief_df_summary(df: pd.DataFrame) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        print("\nColumns & dtypes:")
        print(df.dtypes)
        print("\nMissing values per column:")
        print(df.isna().sum())
        print("\nPreview:")
        print(df.head(5).to_string())
    return buf.getvalue()

def parse_feature_pairs(text):
    d = {}
    for k,v in re.findall(r"([A-Za-z_]+)\s*=\s*([0-9\.]+)", text):
        try: d[k]=float(v)
        except: d[k]=v
    for k,v in re.findall(r"([A-Za-z_]+)\s+([0-9]+(?:\.[0-9]+)?)", text):
        if k not in d:
            try: d[k]=float(v)
            except: d[k]=v
    return d

# ---------------- MAIN PAGE ----------------
def show():
    st.set_page_config(page_title="AI Copilot (Persistent ML)", layout="wide")
    st.title("🧠 AI Copilot — Trainable Local Model + Memory")

    if "memory_cleared" not in st.session_state: st.session_state["memory_cleared"]=False
    if "chat_history" not in st.session_state: st.session_state.chat_history=[{"role":"system","content":SYSTEM_PROMPT}]

    df = st.session_state.get("uploaded_data")
    if df is None:
        st.warning("Upload dataset first on Upload Data page.")
        return

    # Dataset preview
    with st.expander("📂 Dataset preview"):
        st.write("Shape:", df.shape)
        st.dataframe(df.head())

    st.markdown("---")

    # Show memory
    mem = load_memory()
    if mem["insights"]:
        with st.expander("💾 Copilot memory (recent insights)"):
            for e in mem["insights"][:5]:
                st.markdown(f"**{e['title']}** — {e['timestamp']}")
                st.write(e['content'])
            if st.button("Clear memory"):
                save_memory({"insights":[]})
                st.session_state["memory_cleared"]=True
                st.stop()
    if st.session_state["memory_cleared"]:
        st.success("Memory cleared ✅")
        st.session_state["memory_cleared"]=False

    st.markdown("---")
    st.subheader("🧩 Train / Retrain AI Models")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        target_col = st.selectbox("Choose numeric target", numeric_cols, index=0)
        train_epochs = st.slider("ANN epochs", 5, 200, 50)
        n_clusters = st.slider("KMeans clusters", 2, 8, 3)

        if st.button("Train / Retrain AI Copilot"):
            with st.spinner("Training models..."):
                try:
                    df_pre = df.copy()
                    target = df_pre[target_col].copy()
                    obj_cols = df_pre.select_dtypes(include=['object','category']).columns.tolist()
                    if target_col in obj_cols: obj_cols.remove(target_col)
                    if obj_cols: df_pre = pd.get_dummies(df_pre, columns=obj_cols, drop_first=True)
                    feature_cols = [c for c in df_pre.columns if c != target_col]
                    X = df_pre[feature_cols].select_dtypes(include=[np.number])
                    y = df_pre[target_col].values
                    if X.shape[1]==0: raise ValueError("No numeric predictors")

                    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)

                    # ANN with progress
                    ann = MLPRegressor(hidden_layer_sizes=(64,32),max_iter=1,warm_start=True,random_state=42)
                    st.write("Training ANN...")
                    progress_bar=st.progress(0)
                    for epoch in range(train_epochs):
                        ann.max_iter = epoch+1
                        ann.fit(X_train_scaled, y_train)
                        progress_bar.progress((epoch+1)/train_epochs)
                        time.sleep(0.05)

                    # Linear Regression
                    linreg = LinearRegression().fit(X_train_scaled, y_train)

                    # KMeans
                    kmeans = KMeans(n_clusters=n_clusters,random_state=42)
                    kmeans.fit(X_train_scaled)

                    # Save model
                    joblib.dump({"scaler":scaler,"ann":ann,"linreg":linreg,"kmeans":kmeans,
                                 "feature_columns":X.columns.tolist(),"target_col":target_col},MODEL_PATH)

                    # Evaluation
                    st.success("✅ Models trained and saved")
                    st.write(f"ANN R²: {r2_score(y_test,ann.predict(X_test_scaled)):.3f}, Linear R²: {r2_score(y_test,linreg.predict(X_test_scaled)):.3f}")

                    # Top features memory
                    coefs=dict(zip(X.columns.tolist(),linreg.coef_))
                    sorted_feats = sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
                    feat_text=", ".join([f"{k} ({v:.3f})" for k,v in sorted_feats])
                    add_memory_entry("Top model features", feat_text)
                    st.write("Top features:", feat_text)

                except Exception as e:
                    st.error(f"Training error: {e}")

    st.markdown("---")
    st.subheader("💬 Ask the Copilot — natural queries + predictions")
    user_query = st.text_input("Ask (examples): 'summary', 'top 3 products by Revenue', 'predict Revenue if ads=5000', 'focus low revenue regions'")

    if st.button("Send") and user_query:
        text=user_query.lower()
        handled=False

        # 1) SUMMARY
        if "summary" in text or "overview" in text:
            st.chat_message("assistant").markdown("📄 Quick dataset summary:")
            st.code(brief_df_summary(df))
            add_memory_entry("Summary","Provided dataframe summary")
            handled=True

        # 2) TOP N
        m = re.search(r"top\s+(\d+)\s+([A-Za-z_ ]+?)\s+by\s+([A-Za-z_ ]+)", text)
        if m:
            n=int(m.group(1)); cat_col=m.group(2).strip().title(); num_col=m.group(3).strip().title()
            cat_candidates=[c for c in df.columns if c.startswith(cat_col)]
            if cat_candidates and num_col in df.columns:
                cat_col_used = cat_candidates[0]
                out = df.groupby(cat_col_used)[num_col].sum().nlargest(n)
                st.chat_message("assistant").markdown(f"🔝 Top {n} {cat_col} by {num_col}:")
                st.dataframe(out.reset_index())
                # Plot
                fig, ax = plt.subplots()
                out.reset_index().plot(kind="bar", x=cat_col_used, y=num_col, ax=ax, color="skyblue")
                ax.set_ylabel(num_col); ax.set_title(f"Top {n} {cat_col} by {num_col}")
                st.pyplot(fig)
                add_memory_entry(f"Top {n} {cat_col}", f"Computed top {n}")
                handled=True

        # 3) TOTAL / AVG
        if "total" in text or "average" in text:
            num_cols=df.select_dtypes(include=[np.number]).columns.tolist()
            for col in ["Region","Product","Stage"]:
                col_candidates=[c for c in df.columns if c.startswith(col)]
                if col_candidates and num_cols:
                    cat_col_used=col_candidates[0]
                    valcol=num_cols[0]
                    total_val=df.groupby(cat_col_used)[valcol].sum()
                    st.chat_message("assistant").info(f"Total {valcol} by {cat_col_used}:")
                    st.dataframe(total_val.reset_index())
                    # Plot
                    fig, ax=plt.subplots()
                    total_val.plot(kind="bar", ax=ax,color="orange")
                    ax.set_ylabel(valcol); ax.set_title(f"Total {valcol} by {cat_col_used}")
                    st.pyplot(fig)
                    add_memory_entry("Total query", f"Total {valcol} by {cat_col_used}")
                    handled=True

        # 4) PREDICTIONS
        if "predict" in text and os.path.exists(MODEL_PATH):
            try:
                model_bundle=joblib.load(MODEL_PATH)
                scaler, ann, feature_cols, target_col = model_bundle["scaler"], model_bundle["ann"], model_bundle["feature_columns"], model_bundle["target_col"]
                pairs=parse_feature_pairs(text)
                sample_vec=[pairs.get(c.split("_")[0],0.0) for c in feature_cols]
                sample=np.array(sample_vec).reshape(1,-1)
                pred=ann.predict(scaler.transform(sample))[0]
                st.chat_message("assistant").success(f"🤖 Predicted {target_col}: {pred:.2f}")
                add_memory_entry("Prediction", f"{text} -> {pred:.2f}")
                handled=True
            except Exception as e:
                st.warning(f"Prediction error: {e}")

        # 5) CLUSTER
        if any(w in text for w in ["cluster","focus","recommend","improve"]) and os.path.exists(MODEL_PATH):
            try:
                model_bundle=joblib.load(MODEL_PATH)
                scaler, kmeans, feature_cols, target_col = model_bundle["scaler"], model_bundle["kmeans"], model_bundle["feature_columns"], model_bundle["target_col"]
                df_pre=df.copy()
                obj_cols=df_pre.select_dtypes(include=['object','category']).columns.tolist()
                if obj_cols: df_pre=pd.get_dummies(df_pre, columns=obj_cols, drop_first=True)
                X_all=df_pre.reindex(columns=feature_cols, fill_value=0).values
                labels=kmeans.predict(scaler.transform(X_all))
                df["Cluster"]=labels
                cluster_rev=df.groupby("Cluster")[target_col].sum().sort_values()
                worst=cluster_rev.index[0]
                st.chat_message("assistant").info(f"🔎 Cluster {worst} has lowest total {target_col}")
                st.dataframe(cluster_rev.reset_index().rename(columns={target_col:"TotalRevenue"}))
                # Cluster plot
                fig, ax=plt.subplots()
                cluster_rev.plot(kind="bar", ax=ax, color="lightgreen")
                ax.set_ylabel(target_col); ax.set_title("Total per Cluster")
                st.pyplot(fig)
                add_memory_entry("Recommendation", f"Focus cluster {worst}")
                handled=True
            except Exception as e:
                st.warning(f"Clustering failed: {e}")

        if not handled:
            st.info("I couldn't parse your question. Try examples:\n- 'Total revenue by region'\n- 'Top 5 products by Revenue'\n- 'Predict Revenue if ads=5000'\n- 'Cluster low revenue regions'")
