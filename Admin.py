import streamlit as st
import mysql.connector
from datetime import date
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Gym Admin Dashboard",
    page_icon="💪",
    layout="wide"
)

# --- HEADER ---
st.markdown("""
    <h1 style='text-align: center; color: #FF6F61;'>🏋️ Gym Management System</h1>
    <p style='text-align: center;'>Welcome, Admin. Manage members, events, and trainers with ease.</p>
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

# --- ADD MEMBER ---
def add_member(name, join_date, plan_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.callproc("AddMemberAndPayment", (name, join_date, plan_id))
    db.commit()
    cursor.close()
    db.close()
    st.success("✅ Member added successfully!")

# --- FETCH QUERY HELPER ---
def fetch_all(query):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    db.close()
    return result, columns

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👥 Members", "➕ Add Member", "📆 Events", "🧑‍🏫 Trainers", "⏳ Expiring Soon",
    "🏅 Trainer Performance", "📒 Event Attendance"
])


# === TAB 1: MEMBERS ===
with tab1:
    st.markdown("### 📋 All Members")

    # Dropdown to select how many rows to view
    row_limit = st.selectbox(
        "Show latest members",
        options=[10, 25, 50, 100, "All"],
        index=0
    )

    base_query = """
        SELECT m.member_id, m.name, m.join_date, p.plan_name, m.expiration_date
        FROM members m
        JOIN membership_plans p ON m.plan_id = p.plan_id
        ORDER BY m.member_id DESC
    """

    # Add limit to query if not "All"
    if row_limit != "All":
        base_query += f" LIMIT {row_limit}"

    members, _ = fetch_all(base_query)
    columns = ["Member ID", "Name", "Join Date", "Plan", "Expiration Date"]
    df = pd.DataFrame(members, columns=columns)

    st.dataframe(df, use_container_width=True, height=400)


# === TAB 2: ADD MEMBER ===
with tab2:
    st.markdown("### ➕ Register New Member")

    with st.form("add_member_form"):
        name = st.text_input("Member Name")
        join_date = st.date_input("Join Date", value=date.today())
        
        plans, _ = fetch_all("SELECT plan_id, plan_name FROM membership_plans")
        plan_dict = {p[1]: p[0] for p in plans}
        selected_plan = st.selectbox("Select Plan", list(plan_dict.keys()))

        submitted = st.form_submit_button("Add Member")
        if submitted:
            add_member(name, join_date.strftime('%Y-%m-%d'), plan_dict[selected_plan])
            st.rerun()

# === TAB 3: EVENTS ===
with tab3:
    st.markdown("### 📆 Upcoming Events")

    events, _ = fetch_all("""
        SELECT e.event_id, e.event_name, e.event_date, t.name AS trainer_name, e.description
        FROM events e
        JOIN trainers t ON e.trainer_id = t.trainer_id
        ORDER BY e.event_date ASC;
    """)
    event_columns = ["Event ID", "Event Name", "Event Date", "Trainer", "Description"]
    df_events = pd.DataFrame(events, columns=event_columns)

    st.metric("Upcoming Events", len(df_events))
    st.dataframe(df_events, use_container_width=True)

# === TAB 4: TRAINERS ===
with tab4:
    st.markdown("### 🧑‍🏫 Trainer Directory")

    trainers, _ = fetch_all("SELECT trainer_id, name, specialty, availability_days FROM trainers")
    trainer_columns = ["Trainer ID", "Name", "Specialty", "Available Days"]
    df_trainers = pd.DataFrame(trainers, columns=trainer_columns)

    st.metric("Total Trainers", len(df_trainers))
    st.dataframe(df_trainers, use_container_width=True)

# === TAB 5: EXPIRING MEMBERS ===
with tab5:
    st.markdown("### ⏳ Memberships Expiring by Month")

    selected_date = st.date_input("Select a Month", value=date.today())
    selected_year = selected_date.year
    selected_month = selected_date.month

    query = f"""
        SELECT m.member_id, m.name, m.join_date, p.plan_name, m.expiration_date
        FROM members m
        JOIN membership_plans p ON m.plan_id = p.plan_id
        WHERE YEAR(m.expiration_date) = {selected_year}
        AND MONTH(m.expiration_date) = {selected_month};
    """

    expiring_members, _ = fetch_all(query)
    columns = ["Member ID", "Name", "Join Date", "Plan", "Expiration Date"]
    df_expiring = pd.DataFrame(expiring_members, columns=columns)

    st.metric("Expiring This Month", len(df_expiring))

    if df_expiring.empty:
        st.info("✅ No members expiring this month.")
    else:
        st.dataframe(df_expiring, use_container_width=True)
with tab6:
    st.markdown("### 🏅 Trainer Performance Overview")

    performance_query = """
        SELECT t.name AS Trainer, COUNT(e.event_id) AS Event_Count
        FROM trainers t
        LEFT JOIN events e ON t.trainer_id = e.trainer_id
        GROUP BY t.trainer_id
        ORDER BY Event_Count DESC;
    """

    data, _ = fetch_all(performance_query)
    df_perf = pd.DataFrame(data, columns=["Trainer", "Total Events"])

    if df_perf.empty:
        st.info("No events assigned to any trainer yet.")
    else:
        st.bar_chart(df_perf.set_index("Trainer"))
        st.dataframe(df_perf, use_container_width=True)

with tab7:
    st.markdown("### 🏆 Top 10 Most Attended Events")

    query = """
        SELECT 
            e.event_name AS Event,
            COUNT(*) AS Attendance_Count
        FROM event_attendance ea
        JOIN events e ON ea.event_id = e.event_id
        GROUP BY e.event_id
        ORDER BY Attendance_Count DESC
        LIMIT 10
    """

    top_event_data, _ = fetch_all(query)
    df_top = pd.DataFrame(top_event_data, columns=["Event", "Attendance Count"])

    if df_top.empty:
        st.info("No attendance data available.")
    else:
        st.bar_chart(df_top.set_index("Event"))
        st.dataframe(df_top, use_container_width=True)
