
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

API_BASE = "https://render-scheduler-api.onrender.com".strip()  # Replace with your backend URL

# Sidebar Logo and Job Submission Form
with st.sidebar:
    logo = Image.open("logo.png")
    st.image(logo, width=140)
    st.markdown("### Submit New Job")
    job_id = st.text_input("Job ID", key="job_id_input")
    duration = st.number_input("Duration", min_value=1, step=1, key="duration_input")
    due_date = st.number_input("Due Date", min_value=1, step=1, key="due_input")
    machine = st.text_input("Machine", key="machine_input")
    skill = st.text_input("Skill", key="skill_input")
    if st.button("Add Job", key="add_job_btn"):
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
                st.success("✅ Job submitted.")
            else:
                try:
                    error_detail = r.json().get("detail", r.text)
                except Exception:
                    error_detail = r.text
                st.error(f"❌ Failed: {error_detail}")
        except Exception as e:
            st.error(f"❌ API Error: {e}")

# Title with clipboard emoji and line
st.title("📋 Job Scheduler Demo")
st.markdown("---")

# Session state initialization
if "schedule_v1" not in st.session_state:
    st.session_state["schedule_v1"] = []
if "schedule_v2" not in st.session_state:
    st.session_state["schedule_v2"] = []
if "v1_status" not in st.session_state:
    st.session_state["v1_status"] = ""
if "v2_status" not in st.session_state:
    st.session_state["v2_status"] = ""

# Current Jobs
st.subheader("📊 Current Jobs")
try:
    jobs = requests.get(f"{API_BASE}/jobs").json()
    st.dataframe(pd.DataFrame(jobs))
except:
    st.warning("Could not load job data.")

# Schedule buttons and display
col1, col2 = st.columns(2)

with col1:
    st.subheader("Generate Schedule V1")
    if st.button("⚙️ Run Scheduler V1", key="run_v1"):
        try:
            r = requests.post(f"{API_BASE}/run-scheduler-v1")
            if r.status_code == 200:
                st.session_state["schedule_v1"] = r.json()
                st.session_state["v1_status"] = "✅ Schedule V1 generated."
            else:
                st.session_state["v1_status"] = f"❌ V1 failed: {r.text}"
        except Exception as e:
            st.session_state["v1_status"] = f"❌ Error: {e}"
    if st.session_state["v1_status"]:
        st.info(st.session_state["v1_status"])
    st.dataframe(pd.DataFrame(st.session_state["schedule_v1"]))

    # Add explanatory text clearly under the V1 button
    st.markdown("### 🚩 Scheduler V1 uses **No-overlap per machine** logic.")

    st.markdown("---")

with col2:
    st.subheader("Generate Schedule V2")
    if st.button("⚙️ Run Scheduler V2", key="run_v2"):
        try:
            r = requests.post(f"{API_BASE}/run-scheduler-v2")
            if r.status_code == 200:
                st.session_state["schedule_v2"] = r.json()
                st.session_state["v2_status"] = "✅ Schedule V2 generated."
            else:
                st.session_state["v2_status"] = f"❌ V2 failed: {r.text}"
        except Exception as e:
            st.session_state["v2_status"] = f"❌ Error: {e}"
    if st.session_state["v2_status"]:
        st.info(st.session_state["v2_status"])
    st.dataframe(pd.DataFrame(st.session_state["schedule_v2"]))

# Comparison chart if both exist
if st.session_state["schedule_v1"] and st.session_state["schedule_v2"]:
    df1 = pd.DataFrame(st.session_state["schedule_v1"])
    df2 = pd.DataFrame(st.session_state["schedule_v2"])
    st.subheader("📈 Strategy Gantt Chart Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Strategy V1**")
        fig, ax = plt.subplots(figsize=(8, 4))
        for _, row in df1.iterrows():
            ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
            ax.text(row["start"], row["job_id"], f'{row["start"]}-{row["end"]}', va='center', ha='left')
        ax.set_xlabel("Time")
        ax.set_ylabel("Job ID")
        ax.set_title("V1 Gantt Chart")
        st.pyplot(fig)

    with col2:
        st.markdown("**Strategy V2**")
        fig, ax = plt.subplots(figsize=(8, 4))
        for _, row in df2.iterrows():
            ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
            ax.text(row["start"], row["job_id"], f'{row["start"]}-{row["end"]}', va='center', ha='left')
        ax.set_xlabel("Time")
        ax.set_ylabel("Job ID")
        ax.set_title("V2 Gantt Chart")
        st.pyplot(fig)

    st.subheader("📊 Strategy Metrics")
    df1["version"] = "v1"
    df2["version"] = "v2"
    all_df = pd.concat([df1, df2])
    all_df["duration"] = all_df["end"] - all_df["start"]
    summary = all_df.groupby("version").agg({
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

# Clear All Button
if st.button("🧹 Clear All Jobs + Schedule", key="clear_btn"):
    try:
        r = requests.delete(f"{API_BASE}/reset")
        if r.status_code == 200:
            st.success("✅ Cleared all job and schedule data.")
            st.session_state["schedule_v1"] = []
            st.session_state["schedule_v2"] = []
            st.session_state["v1_status"] = ""
            st.session_state["v2_status"] = ""
        else:
            st.error(f"❌ Reset failed: {r.text}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")
