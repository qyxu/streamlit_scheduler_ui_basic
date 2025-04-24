
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_BASE = "https://render-scheduler-api.onrender.com"  # Replace with your actual backend URL

st.title("📋 Unified Job Shop Scheduler")

# Job submission
st.sidebar.header("Submit New Job")
job_id = st.sidebar.text_input("Job ID", key="job_id_input")
duration = st.sidebar.number_input("Duration", min_value=1, step=1, key="duration_input")
due_date = st.sidebar.number_input("Due Date", min_value=1, step=1, key="due_input")
machine = st.sidebar.text_input("Machine", key="machine_input")
skill = st.sidebar.text_input("Skill", key="skill_input")

if st.sidebar.button("Add Job", key="add_job_btn"):
    payload = {
        "job_id": job_id,
        "duration": duration,
        "due_date": due_date,
        "machine_required": machine,
        "skill_required": skill
    }
    try:
        r = requests.post(f"{API_BASE}/jobs", json=payload)
        if r.status_code == 200:
            st.sidebar.success("✅ Job submitted.")
        else:
            try:
                error_detail = r.json().get("detail", r.text)
            except Exception:
                error_detail = r.text
            st.sidebar.error(f"❌ Failed: {error_detail}")
    except Exception as e:
        st.sidebar.error(f"❌ API Error: {e}")

# Run and compare both strategies
if st.button("🧪 Compare Scheduling Strategies", key="compare_btn"):
    try:
        r = requests.post(f"{API_BASE}/compare-schedulers")
        if r.status_code == 200:
            data = r.json()
            df = pd.DataFrame(data)
            if df.empty:
                st.warning("No jobs available to schedule.")
            else:
                v1 = df[df["version"] == "v1"]
                v2 = df[df["version"] == "v2"]

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Strategy V1")
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.set_title("Gantt Chart: V1")
                    for _, row in v1.iterrows():
                        ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
                        ax.text(row["start"], row["job_id"], f'{row["start"]}-{row["end"]}', va='center', ha='left')
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Job ID")
                    st.pyplot(fig)

                with col2:
                    st.subheader("Strategy V2")
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.set_title("Gantt Chart: V2")
                    for _, row in v2.iterrows():
                        ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
                        ax.text(row["start"], row["job_id"], f'{row["start"]}-{row["end"]}', va='center', ha='left')
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Job ID")
                    st.pyplot(fig)

                st.subheader("📊 Summary Metrics")
                df["duration"] = df["end"] - df["start"]
                summary = df.groupby("version").agg({
                    "job_id": "count",
                    "start": "mean",
                    "end": "mean",
                    "duration": "mean"
                }).rename(columns={
                    "job_id": "Job Count",
                    "start": "Avg Start",
                    "end": "Avg End",
                    "duration": "Avg Duration"
                }).reset_index()
                st.dataframe(summary)
        else:
            st.error(f"❌ Compare failed: {r.text}")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Show current data
st.subheader("📊 Current Jobs")
try:
    jobs = requests.get(f"{API_BASE}/jobs").json()
    st.dataframe(pd.DataFrame(jobs))
except:
    st.warning("Could not load job data.")

st.subheader("📅 Current Schedule")
try:
    sched = requests.get(f"{API_BASE}/schedule").json()
    st.dataframe(pd.DataFrame(sched))
except:
    st.warning("Could not load schedule data.")

# Clear all
if st.button("🧹 Clear All Jobs + Schedule", key="clear_btn"):
    try:
        r = requests.delete(f"{API_BASE}/reset")
        if r.status_code == 200:
            st.success("✅ Cleared all job and schedule data.")
        else:
            st.error(f"❌ Reset failed: {r.text}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")
