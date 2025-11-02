import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from io import BytesIO

def show():
    st.title("🤖 AI Predictions")
    
    # 🔒 Check data upload
    if "uploaded_data" not in st.session_state:
        st.warning("📂 Upload a dataset first before running predictions.")
        return

    df = st.session_state["uploaded_data"]
    
    # ✨ Styling for cards
    st.markdown(
        """
        <style>
        .result-card {
            background: #ffffff;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            margin: 10px 0;
            transition: transform 0.2s ease-in-out;
        }
        .result-card:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .metric-title {
            font-size: 16px;
            font-weight: 500;
            color: #2C3E50;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: bold;
            color: #1ABC9C;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 📊 Data preview
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head())

    # 🎯 Select target column
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if not numeric_cols:
        st.error("❌ No numeric columns found for prediction.")
        return

    target_col = st.selectbox("🎯 Select target column to predict:", numeric_cols)

    # ⚙️ Select features
    feature_cols = st.multiselect(
        "🧮 Select features (independent variables):",
        [col for col in numeric_cols if col != target_col],
        default=[col for col in numeric_cols if col != target_col]
    )

    if not feature_cols:
        st.warning("⚠️ Please select at least one feature to train the model.")
        return

    # 🧑‍💻 Train-test split
    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 🤖 Train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 🔮 Predictions
    predictions = model.predict(X_test)

    # 📈 Model Performance (card style)
    mse = mean_squared_error(y_test, predictions)
    st.subheader("📊 Model Performance")
    st.markdown(
        f"""
        <div class="result-card">
            <div class="metric-title">Mean Squared Error</div>
            <div class="metric-value">{mse:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 📝 Show actual vs predicted
    results = pd.DataFrame({
        f"✅ Actual {target_col}": y_test,
        f"🤖 Predicted {target_col}": predictions
    })
    st.dataframe(results.head(10))

    # 📉 Plot
    st.subheader("📉 Actual vs Predicted Plot")
    fig, ax = plt.subplots()
    ax.scatter(y_test, predictions, alpha=0.7, color="#3498db", edgecolor="white")
    ax.plot([y.min(), y.max()], [y.min(), y.max()], "r--", lw=2)
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title(f"Actual vs Predicted {target_col}")
    st.pyplot(fig)

    # ================== 💾 SAVE/DOWNLOAD SECTION ==================
    st.subheader("💾 Save Results")

    # Save DataFrame as CSV
    csv_buffer = BytesIO()
    results.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download Predictions (CSV)",
        data=csv_buffer.getvalue(),
        file_name="predictions_results.csv",
        mime="text/csv"
    )

    # Save Plot as PNG
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", bbox_inches="tight")
    st.download_button(
        label="⬇️ Download Plot (PNG)",
        data=img_buffer.getvalue(),
        file_name="predictions_plot.png",
        mime="image/png"
    )

    plt.close(fig)

