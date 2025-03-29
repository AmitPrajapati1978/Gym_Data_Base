import streamlit as st
import pandas as pd
import mysql.connector

# --- PAGE CONFIG ---
st.set_page_config(page_title="📈 Gym Growth Analytics", page_icon="📊", layout="wide")

# --- HEADER ---
st.markdown("""
    <h2 style='text-align: center; color: #6C63FF;'>📈 Membership Growth Overview</h2>
    <p style='text-align: center;'>Track monthly membership growth trends and business momentum.</p>
    <hr style='border:1px solid #eee'/>
""", unsafe_allow_html=True)

# --- STYLES ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stDataFrame thead tr th {
        background-color: #f0f2f6;
        color: #333;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- DB CONNECTION ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Gym_Data_Base"
    )

# --- DATA FETCH ---
def fetch_growth():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(join_date, '%Y-%m') AS month, COUNT(*) AS new_members
        FROM members
        GROUP BY month
        ORDER BY month;
    """)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return pd.DataFrame(result, columns=["Month", "New Members"])

# --- MAIN CONTENT ---
df_growth = fetch_growth()

if df_growth.empty:
    st.info("📭 No data available yet. Add some members first.")
else:
    total = df_growth["New Members"].sum()
    highest_month = df_growth.loc[df_growth["New Members"].idxmax()]
    recent_month = df_growth.iloc[-1]

    # 📊 Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total New Members", total)
    col2.metric("🚀 Best Month", highest_month["Month"], int(highest_month["New Members"]))
    col3.metric("📆 Most Recent Month", recent_month["Month"], int(recent_month["New Members"]))

    st.markdown("### 📈 Monthly Growth – Line Chart")
    st.line_chart(df_growth.set_index("Month"))

    st.markdown("### 📊 Monthly Growth – Bar Chart")
    st.bar_chart(df_growth.set_index("Month"))

# 🔙 Back to main app
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><a href='/'><button style='padding:0.5rem 1rem;'>🏠 Back to Dashboard</button></a></div>", unsafe_allow_html=True)
