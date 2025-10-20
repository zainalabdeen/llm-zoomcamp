import streamlit as st
import pandas as pd
import sys , os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.feedback_service import load_feedback_df
import plotly.express as px
import os

# 🔐 --- Basic Admin Auth ---
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="📊 Admin Dashboard", page_icon="🔐", layout="wide")
st.title("📊 Feedback Analytics Dashboard")

password = st.text_input("🔑 Enter admin password:", type="password")
if password != ADMIN_PASSWORD:
    st.error("❌ Unauthorized: Wrong password.")
    st.stop()

df = load_feedback_df()
if df is None or df.empty:
    st.warning("No feedback data available yet.")
else:
    st.dataframe(df)

    # 1️⃣ Rating distribution
    fig1 = px.histogram(df, x="rating", nbins=5, title="⭐ Rating Distribution")
    st.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Feedback over time
    fig2 = px.line(df, x="timestamp", y="rating", title="📈 Ratings Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    # 3️⃣ Top common feedback words
    df["word_count"] = df["user_feedback"].fillna("").apply(lambda x: len(x.split()))
    fig3 = px.histogram(df, x="word_count", title="📝 Feedback Length Distribution")
    st.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Accuracy gap: model vs corrected answers
    df["correction_flag"] = df["corrected_answer"].apply(lambda x: "Corrected" if isinstance(x, str) and len(x) > 0 else "As-is")
    fig4 = px.pie(df, names="correction_flag", title="📊 Corrected vs. Accepted Answers")
    st.plotly_chart(fig4, use_container_width=True)

    # 5️⃣ Average rating trend (monthly)
    df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M")
    fig5 = px.bar(df.groupby("month")["rating"].mean().reset_index(), x="month", y="rating", title="📆 Avg Monthly Rating")
    st.plotly_chart(fig5, use_container_width=True)
