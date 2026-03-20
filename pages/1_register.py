import streamlit as st
from src.logic.equipment import register_upgrade

st.set_page_config(page_title="Register Upgrade", page_icon="📝")
st.title("Register New Skill Upgrade")

with st.form("register_form"):
    w_type = st.selectbox("Weapon Type", ["大剣", "太刀", "片手剣", "双剣", "ハンマー", "狩猟笛", "ランス", "ガンランス", "スラッシュアックス", "チャージアックス", "操虫棍", "ライトボウガン", "ヘビィボウガン", "弓"])
    element = st.selectbox("Element", ["無", "火", "水", "雷", "氷", "龍", "毒", "麻痺", "睡眠", "爆破"])
    series_skill = st.selectbox("Series Skill", ["なし", "火竜の奥義", "角竜の奥義", "雷狼竜の奥義", "氷牙竜の秘技", "迅竜の秘技"])
    group_skill = st.selectbox("Group Skill", ["なし", "星", "月", "太陽", "空", "海", "地"])
    count = st.number_input("Upgrade Count", min_value=1, value=1, step=1)
    
    submitted = st.form_submit_button("Register")
    
    if submitted:
        if not series_skill.strip() or not group_skill.strip():
            st.error("Series Skill and Group Skill are required.")
        else:
            record_id = register_upgrade(w_type, element, series_skill, group_skill, count)
            # Add to history
            st.session_state['undo_stack'].append({
                'action_type': 'REGISTER',
                'target_id': record_id,
            })
            st.session_state['redo_stack'].clear()
            st.success("Successfully registered!")
