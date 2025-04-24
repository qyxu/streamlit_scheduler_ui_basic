import streamlit as st
import requests
import pandas as pd

API_BASE = "https://render-scheduler-api.onrender.com"  # Replace with your actual Render backend URL

st.title("📋 Job Shop Scheduler")

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
            # Try to get JSON error message
            try:
                error_msg = r.json().get("detail", "")
            except Exception:
                error_msg = r.text or "Unknown error"
            st.sidebar.error(f"❌ Failed: {error_msg}")
    except Exception as e:
        st.sidebar.error(f"❌ API Error: {e}")

if st.button("⚙️ Run Scheduler", key="run_scheduler_btn"):
    try:
        r = requests.post(f"{API_BASE}/run-scheduler")
        if r.status_code == 200:
            st.success(f"✅ Scheduler ran successfully. Jobs scheduled: {r.json().get('jobs_scheduled')}")
        else:
            try:
                error_detail = r.json().get("detail", r.text)
            except Exception:
                error_detail = r.text
            st.error(f"❌ Scheduler failed: {error_detail}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")

if st.button("🧹 Clear All Data", key="clear_btn"):
    try:
        r = requests.delete(f"{API_BASE}/reset")
        if r.status_code == 200:
            st.success("✅ All jobs and schedules cleared.")
        else:
            st.error(f"❌ Reset failed: {r.text}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")

st.subheader("📊 Current Jobs")
try:
    jobs = requests.get(f"{API_BASE}/jobs").json()
    st.dataframe(pd.DataFrame(jobs))
except:
    st.warning("Could not fetch job data. Is the API running?")

st.subheader("📅 Current Schedule")
try:
    sched = requests.get(f"{API_BASE}/schedule").json()
    st.dataframe(pd.DataFrame(sched))
except:
    st.warning("Could not fetch schedule data. Is the API running?")
