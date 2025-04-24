
import streamlit as st
import requests
import pandas as pd

API_BASE = "https://render-scheduler-api.onrender.com"

st.title("📋 Job Shop Scheduler")

st.sidebar.header("Submit New Job")
job_id = st.sidebar.text_input("Job ID")
duration = st.sidebar.number_input("Duration", min_value=1, step=1)
due_date = st.sidebar.number_input("Due Date", min_value=1, step=1)
machine = st.sidebar.text_input("Machine")
skill = st.sidebar.text_input("Skill")

if st.sidebar.button("Add Job", key="add_job_button"):
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
            # Try to extract a structured error message
            try:
                error_detail = r.json().get("detail", r.text)
            except Exception:
                error_detail = r.text
            st.sidebar.error(f"❌ Failed: {error_detail}")
    except Exception as e:
        st.sidebar.error(f"❌ API Error: {e}")

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


if st.button("⚙️ Run Scheduler"):
    try:
        r = requests.post(f"{API_BASE}/run-scheduler")
        if r.status_code == 200:
            st.success(f"✅ Scheduler ran successfully. Jobs scheduled: {r.json().get('jobs_scheduled')}")
        else:
            st.error(f"❌ Scheduler failed: {r.text}")
    except Exception as e:
        st.error(f"❌ Scheduler API error: {e}")

if st.button("🧹 Clear All Data"):
    try:
        r = requests.delete(f"{API_BASE}/reset")
        if r.status_code == 200:
            st.success("✅ All jobs and schedules deleted.")
        else:
            st.error(f"❌ Failed to reset: {r.text}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")


