import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import streamlit_authenticator as stauth

# Authentication setup
credentials = {
    'usernames': {
        'accumet': {
            'name': 'Scheduler Admin',
            'password': '$2b$12$8L7OvR.e2Et8hmnXJ5BSsu9NJh9ixgyWxGCCiVyi8TL2fqwMh0.ce'
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='scheduler_cookie',
    key='scheduler_secret_key',
    cookie_expiry_days=30
)

authenticator.login(location='main')

if st.session_state.get("authentication_status"):
    authenticator.logout(location='sidebar')

    API_BASE = "https://render-scheduler-api.onrender.com"

    # Sidebar Job Submission
    with st.sidebar:
        logo = Image.open("logo.png")
        st.image(logo, width=140)
        st.markdown("### Submit New Job")
        job_id = st.text_input("Job ID")
        duration = st.number_input("Duration", min_value=1, step=1)
        due_date = st.number_input("Due Date", min_value=1, step=1)
        machine = st.text_input("Machine")
        skill = st.text_input("Skill")
        if st.button("Add Job"):
            payload = {
                "job_id": job_id,
                "duration": duration,
                "due_date": due_date,
                "machine_required": machine,
                "skill_required": skill
            }
            r = requests.post(f"{API_BASE}/jobs", json=payload)
            if r.status_code == 200:
                st.success("✅ Job submitted.")
            else:
                st.error(f"❌ Failed: {r.text}")

    st.title("📋 Job Scheduler Demo")
    st.markdown("---")

    # Initialize Session States
    for key in ["schedule_v1", "schedule_v2", "v1_status", "v2_status"]:
        if key not in st.session_state:
            st.session_state[key] = [] if "schedule" in key else ""

    # Load Current Jobs
    st.subheader("📊 Current Jobs")
    jobs = requests.get(f"{API_BASE}/jobs").json()
    st.dataframe(pd.DataFrame(jobs))

    col1, col2 = st.columns(2)

    # Scheduler V1
    with col1:
        st.subheader("Generate Schedule V1")
        if st.button("⚙️ Run Scheduler V1"):
            r = requests.post(f"{API_BASE}/run-scheduler-v1")
            if r.status_code == 200:
                st.session_state["schedule_v1"] = r.json()
                st.session_state["v1_status"] = "✅ Schedule V1 generated."
            else:
                st.session_state["v1_status"] = f"❌ V1 failed: {r.text}"

        if st.session_state["v1_status"]:
            st.success(st.session_state["v1_status"])

        st.dataframe(pd.DataFrame(st.session_state["schedule_v1"]))
        st.markdown("<small>🚩 Scheduler V1: No-overlap per machine, shortest end time.</small>", unsafe_allow_html=True)

    # Scheduler V2
    with col2:
        st.subheader("Generate Schedule V2")
        if st.button("⚙️ Run Scheduler V2"):
            r = requests.post(f"{API_BASE}/run-scheduler-v2")
            if r.status_code == 200:
                st.session_state["schedule_v2"] = r.json()
                st.session_state["v2_status"] = "✅ Schedule V2 generated."
            else:
                st.session_state["v2_status"] = f"❌ V2 failed: {r.text}"

        if st.session_state["v2_status"]:
            st.success(st.session_state["v2_status"])

        st.dataframe(pd.DataFrame(st.session_state["schedule_v2"]))
        st.markdown("<small>🚩 Scheduler V2: No-overlap per machine, min completion time.</small>", unsafe_allow_html=True)

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

    # Clear All Data
    if st.button("🧹 Clear All Jobs + Schedule"):
        r = requests.delete(f"{API_BASE}/reset")
        if r.status_code == 200:
            for key in ["schedule_v1", "schedule_v2", "v1_status", "v2_status"]:
                st.session_state[key] = [] if "schedule" in key else ""
            st.success("✅ Cleared all job and schedule data.")
            jobs = requests.get(f"{API_BASE}/jobs").json()
            st.dataframe(pd.DataFrame(jobs))
        else:
            st.error(f"❌ Reset failed: {r.text}")

elif st.session_state.get("authentication_status") is False:
    st.error('Username/password incorrect')
elif st.session_state.get("authentication_status") is None:
    st.warning('Please enter username/password')
