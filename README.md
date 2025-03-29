# 💪 Gym Management System (SQL + Streamlit)

A full-stack gym admin dashboard built with **Python**, **SQLite**, and **Streamlit** – designed to help admins manage members, trainers, events, and visualize growth analytics 🚀.

> 🔥 **SQL-Driven Automation** using TRIGGERS  
> 📈 Live Charts with Streamlit  
> 🧠 Smart Schema Design & Relational Modeling  
> ✅ 100% Streamlit Cloud Deployable

---

## 🔍 Project Features

### 🎯 Admin Dashboard
- View all members with their **join/expiration dates**
- Register new members (auto-calculates expiration)
- Track upcoming **events and trainer schedules**
- View **expiring memberships** by month

### 📊 Growth Analytics
- Monthly membership trends
- Daily signup tracking (last 30 days)
- Plan-wise member distribution
- Peak signup month + summary metrics

### 🏅 Trainer Performance
- See which trainer conducted the **most events**
- Reward top trainers based on real data

---

## 🛠️ Tech Stack

| Layer      | Tool               |
|------------|--------------------|
| Frontend   | [Streamlit](https://streamlit.io) |
| Database   | SQLite (`.db` file) |
| Language   | Python 3.x         |
| Hosting    | Streamlit Cloud    |
| Faker Data | `faker` Python lib |

---

## 🧠 SQL Highlights

### 📐 Relational Database Design

- `members` ⟶ `membership_plans`
- `members` ⟶ `payments` (via TRIGGER)
- `events` ⟶ `trainers`
- `event_attendance` ⟶ members + events

### ⚡ Triggers

> Whenever a member is added, a **payment record is automatically generated** using a `TRIGGER` in SQLite.

```sql
CREATE TRIGGER AddMemberAndPayment
AFTER INSERT ON members
BEGIN
  INSERT INTO payments (member_id, amount, payment_date)
  VALUES (
    NEW.member_id,
    (SELECT price FROM membership_plans WHERE plan_id = NEW.plan_id),
    DATE('now')
  );
END;
