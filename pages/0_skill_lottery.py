import streamlit as st
import pandas as pd
from src.logic.equipment import get_active_upgrades, register_upgrade
from src.logic.master import get_master_data
from src.components.tables import render_active_upgrades
from src.components.sidebar import render_shared_sidebar

st.set_page_config(page_title="スキル抽選結果", page_icon="⚔️", layout="wide")

# Render shared sidebar (boots from cookie instantly)
render_shared_sidebar()

st.title("スキル抽選結果 🏹")
st.markdown("巨戟強化の抽選順序を確認し、スキルを武器に割り当てます。")

# --- Registration Form (Merged from 1_register) ---
master = get_master_data()
with st.expander("🆕 未登録の強化抽選結果を追加する", expanded=False):
    series_skills_master = master.get("series_skills", [])
    series_skill_labels = [f"{s['skill_parts']} ({s['skill_name']})" if s['skill_parts'] != "なし" else "なし" for s in series_skills_master]
    
    group_skills_master = master.get("group_skills", [])
    group_skill_labels = [f"{g['group_name']} ({g['skill_name']})" if g['group_name'] != "なし" else "なし" for g in group_skills_master]

    with st.form("register_form_dash", border=False):
        c1, c2 = st.columns(2)
        with c1:
            w_type = st.selectbox("武器種", master.get("weapon_types", []))
        with c2:
            element = st.selectbox("属性", master.get("elements", []))
            
        sc1, sc2 = st.columns(2)
        with sc1:
            selected_series_idx = st.selectbox("シリーズスキル", range(len(series_skill_labels)), format_func=lambda i: series_skill_labels[i])
            series_skill = series_skills_master[selected_series_idx]["skill_parts"]
        with sc2:
            selected_group_idx = st.selectbox("グループスキル", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
            group_skill = group_skills_master[selected_group_idx]["group_name"]
            
        count = st.number_input("残り回数 (到達まで)", min_value=1, value=1, step=1)
        
        if st.form_submit_button("登録の確定", type="primary"):
            if not series_skill.strip() or not group_skill.strip():
                st.error("スキルを正しく選択してください。")
            else:
                record_id = register_upgrade(w_type, element, series_skill, group_skill, count)
                if record_id:
                    st.session_state['undo_stack'].append({'action_type': 'REGISTER', 'target_id': record_id})
                    st.session_state['redo_stack'].clear()
                    st.success("抽選結果を登録しました！")
                    st.success("抽選結果を登録しました！")

st.divider()

# --- Dashboard Actions ---
h_col1, h_col2, h_col3 = st.columns([1, 1, 6], vertical_alignment="center")
with h_col1:
    undo_disabled = not st.session_state.get('undo_stack', [])
    if st.button("Undo ↩️", disabled=undo_disabled, use_container_width=True):
        undo_last_action()
with h_col2:
    redo_disabled = not st.session_state.get('redo_stack', [])
    if st.button("Redo ↪️", disabled=redo_disabled, use_container_width=True):
        redo_last_action()

# --- Main Dashboard List ---
df = get_active_upgrades()
render_active_upgrades(df)
