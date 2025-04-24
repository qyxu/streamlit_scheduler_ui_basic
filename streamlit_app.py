
import streamlit as st
import requests
import pandas as pd

API_BASE = "https://render-scheduler-api.onrender.com"  # Replace with your Render backend URL

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

# Generate schedule from each version individually
col1, col2 = st.columns(2)

with col1:
    st.subheader("Generate Schedule V1")
    if st.button("⚙️ Run Scheduler V1", key="run_v1"):
        try:
            r = requests.post(f"{API_BASE}/run-scheduler-v1")
            if r.status_code == 200:
                st.success("✅ Schedule V1 generated.")
                v1 = r.json()
                st.dataframe(pd.DataFrame(v1))
            else:
                st.error(f"❌ V1 failed: {r.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with col2:
    st.subheader("Generate Schedule V2")
    if st.button("⚙️ Run Scheduler V2", key="run_v2"):
        try:
            r = requests.post(f"{API_BASE}/run-scheduler-v2")
            if r.status_code == 200:
                st.success("✅ Schedule V2 generated.")
                v2 = r.json()
                st.dataframe(pd.DataFrame(v2))
            else:
                st.error(f"❌ V2 failed: {r.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Show current jobs
st.subheader("📊 Current Jobs")
try:
    jobs = requests.get(f"{API_BASE}/jobs").json()
    st.dataframe(pd.DataFrame(jobs))
except:
    st.warning("Could not load job data.")

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
