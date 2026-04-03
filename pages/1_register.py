import streamlit as st
from src.logic.equipment import register_upgrade

from src.logic.master import get_master_data

st.set_page_config(page_title="Register Upgrade", page_icon="📝")
st.title("Register New Skill Upgrade")

# Load master data
master = get_master_data()
series_skills_master = master.get("series_skills", [])
series_skill_labels = [f"{s['skill_parts']} ({s['skill_name']})" if s['skill_parts'] != "なし" else "なし" for s in series_skills_master]

group_skills_master = master.get("group_skills", [])
group_skill_labels = [f"{g['group_name']} ({g['skill_name']})" if g['group_name'] != "なし" else "なし" for g in group_skills_master]

with st.form("register_form"):
    w_type = st.selectbox("Weapon Type", master.get("weapon_types", []))
    element = st.selectbox("Element", master.get("elements", []))
    
    selected_series_idx = st.selectbox("Series Skill", range(len(series_skill_labels)), format_func=lambda i: series_skill_labels[i])
    series_skill = series_skills_master[selected_series_idx]["skill_parts"]
    
    selected_group_idx = st.selectbox("Group Skill", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
    group_skill = group_skills_master[selected_group_idx]["group_name"]
    
    count = st.number_input("Upgrade Count", min_value=1, value=1, step=1)
    
    submitted = st.form_submit_button("Register", disabled=not st.session_state.get('gsheet_url'))
    
    if not st.session_state.get('gsheet_url'):
        st.warning("Please set your Google Sheet URL in the sidebar of the Home page before registering.")

    if submitted:
        if not st.session_state.get('gsheet_url'):
            st.error("Google Sheet URL is required for registration.")
        elif not series_skill.strip() or not group_skill.strip():
            st.error("Series Skill and Group Skill are required.")
        else:
            record_id = register_upgrade(w_type, element, series_skill, group_skill, count)
            if record_id:
                # Add to history
                st.session_state['undo_stack'].append({
                    'action_type': 'REGISTER',
                    'target_id': record_id,
                })
                st.session_state['redo_stack'].clear()
                st.success("Successfully registered!")
            else:
                st.error("Failed to register. Please check your Google Sheet URL and permissions.")
