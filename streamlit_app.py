import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import streamlit_authenticator as stauth

# --- Authentication Configuration ---
import streamlit as st
import streamlit_authenticator as stauth

# Define your credentials dictionary
credentials = {
    'usernames': {
        'scheduler_user': {
            'name': 'Scheduler Admin',
            'password': '$2b$12$8L7OvR.e2Et8hmnXJ5BSsu9NJh9ixgyWxGCCiVyi8TL2fqwMh0.ce '  # Replace with your actual hashed password
        }
    }
}

# Initialize the authenticator
authenticator = stauth.Authenticate(
    credentials,
    cookie_name='scheduler_cookie',
    key='scheduler_secret_key',
    cookie_expiry_days=30
)

# Render the login widget
authenticator.login(location='main')

# Access authentication status and username from session state
if st.session_state.get("authentication_status"):
    authenticator.logout(location='sidebar')
    st.sidebar.write(f'Welcome *{credentials["usernames"][st.session_state["username"]]["name"]}*')
    st.title("Your App Content Here")

    # --- Original app code below (unchanged) ---
    API_BASE = "https://render-scheduler-api.onrender.com"

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
                    st.error(f"❌ Failed: {r.text}")
            except Exception as e:
                st.error(f"❌ API Error: {e}")

    st.title("📋 Job Scheduler Demo")
    st.markdown("---")

    if "schedule_v1" not in st.session_state:
        st.session_state["schedule_v1"] = []
    if "schedule_v2" not in st.session_state:
        st.session_state["schedule_v2"] = []

    st.subheader("📊 Current Jobs")
    try:
        jobs = requests.get(f"{API_BASE}/jobs").json()
        st.dataframe(pd.DataFrame(jobs))
    except:
        st.warning("Could not load job data.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generate Schedule V1")
        if st.button("⚙️ Run Scheduler V1"):
            r = requests.post(f"{API_BASE}/run-scheduler-v1")
            if r.status_code == 200:
                st.session_state["schedule_v1"] = r.json()
                st.success("✅ Schedule V1 generated.")
            else:
                st.error(f"❌ V1 failed: {r.text}")
        st.dataframe(pd.DataFrame(st.session_state["schedule_v1"]))
        st.markdown("<small>🚩 Scheduler V1: No-overlap per machine, shortest end time.</small>", unsafe_allow_html=True)

    with col2:
        st.subheader("Generate Schedule V2")
        if st.button("⚙️ Run Scheduler V2"):
            r = requests.post(f"{API_BASE}/run-scheduler-v2")
            if r.status_code == 200:
                st.session_state["schedule_v2"] = r.json()
                st.success("✅ Schedule V2 generated.")
            else:
                st.error(f"❌ V2 failed: {r.text}")
        st.dataframe(pd.DataFrame(st.session_state["schedule_v2"]))
        st.markdown("<small>🚩 Scheduler V2: No-overlap per machine, min completion time.</small>", unsafe_allow_html=True)

    if st.session_state["schedule_v1"] and st.session_state["schedule_v2"]:
        st.subheader("📈 Strategy Gantt Chart Comparison")
        df1 = pd.DataFrame(st.session_state["schedule_v1"])
        df2 = pd.DataFrame(st.session_state["schedule_v2"])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Strategy V1**")
            fig, ax = plt.subplots(figsize=(8, 4))
            for _, row in df1.iterrows():
                ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
            st.pyplot(fig)

        with col2:
            st.markdown("**Strategy V2**")
            fig, ax = plt.subplots(figsize=(8, 4))
            for _, row in df2.iterrows():
                ax.barh(row["job_id"], row["end"] - row["start"], left=row["start"])
            st.pyplot(fig)

    if st.button("🧹 Clear All Jobs + Schedule"):
        requests.delete(f"{API_BASE}/reset")
        st.success("✅ Cleared all job and schedule data.")


elif st.session_state["authentication_status"] is False:
    st.error('Username/password incorrect')

elif st.session_state["authentication_status"] is None:
    st.warning('Please enter username/password')
