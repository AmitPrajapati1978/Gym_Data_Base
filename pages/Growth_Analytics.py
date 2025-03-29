import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="📈 Gym Growth Dashboard", page_icon="📁", layout="wide")

# --- HEADER ---
st.markdown("""
    <h2 style='text-align: center; color: #4CAF50;'>📈 Gym Membership & Activity Analytics</h2>
    <p style='text-align: center;'>Gain insights into gym member growth, engagement, and seasonal activity patterns.</p>
    <hr style='border:1px solid #ccc'/>
""", unsafe_allow_html=True)

# --- DB CONNECTION ---
def connect_db():
    return sqlite3.connect("Gym_Data_Base_Fixed.db")

# --- FETCH MEMBERSHIP GROWTH BY MONTH ---
def fetch_monthly_growth():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', join_date) AS Month,
            COUNT(*) AS New_Members
        FROM members
        GROUP BY Month
        ORDER BY Month
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return pd.DataFrame(data, columns=["Month", "New Members"])

# --- FETCH PLAN DISTRIBUTION ---
def fetch_plan_distribution():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.plan_name, COUNT(m.member_id) 
        FROM members m
        JOIN membership_plans p ON m.plan_id = p.plan_id
        GROUP BY p.plan_name
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return pd.DataFrame(data, columns=["Plan", "Count"])

# --- FETCH DAILY SIGNUPS LAST 30 DAYS ---
def fetch_daily_signups():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT join_date, COUNT(*) 
        FROM members 
        WHERE join_date >= date('now', '-30 days')
        GROUP BY join_date
        ORDER BY join_date
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return pd.DataFrame(data, columns=["Date", "Signups"])

# --- DISPLAY ---
st.subheader("📈 Monthly Membership Growth")
df_growth = fetch_monthly_growth()
if df_growth.empty:
    st.info("👭 No member growth data found.")
else:
    st.line_chart(df_growth.set_index("Month"))
    st.bar_chart(df_growth.set_index("Month"))

    total = df_growth["New Members"].sum()
    peak = df_growth.loc[df_growth["New Members"].idxmax()]

    st.metric("👥 Total New Members", int(total))
    st.metric("🗕️ Peak Month", peak["Month"], str(int(peak["New Members"])))

st.subheader("📋 Plan Distribution")
df_plans = fetch_plan_distribution()
if df_plans.empty:
    st.warning("No plan data available.")
else:
    st.dataframe(df_plans, use_container_width=True)
    st.bar_chart(df_plans.set_index("Plan"))

st.subheader("🕒 Daily Signups (Last 30 Days)")
df_daily = fetch_daily_signups()
if df_daily.empty:
    st.info("No recent daily signup data.")
else:
    st.line_chart(df_daily.set_index("Date"))

# 🔙 Back to main app
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><a href='/'><button style='padding:0.5rem 1rem;'>🏠 Back to Dashboard</button></a></div>", unsafe_allow_html=True)
