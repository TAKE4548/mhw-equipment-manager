import streamlit as st
from src.logic.equipment import register_upgrade
from src.logic.favorites import get_favorite_list, prepare_skill_choices
from src.components.pickers import render_skill_picker

@st.fragment
def render_registration_form(master, user_id):
    """未登録の強化抽選結果を追加するフォーム (Fragment化)"""
    with st.expander("🆕 未登録の強化抽選結果を追加する", expanded=False):
        series_skills_master = master.get("series_skills", [])
        group_skills_master = master.get("group_skills", [])
        
        c1, c2 = st.columns(2)
        with c1: w_type = st.selectbox("武器種", master.get("weapon_types", []), key="lottery_reg_wt")
        with c2: element = st.selectbox("属性", master.get("elements", []), key="lottery_reg_elem")
            
        st.markdown("**抽選スキル**")
        c_lot_s, c_lot_g = st.columns(2)
        with c_lot_s: series_skill = render_skill_picker("シリーズスキル", master.get("series_skills", []), "series", "lot_reg_s")
        with c_lot_g: group_skill = render_skill_picker("グループスキル", master.get("group_skills", []), "group", "lot_reg_g")
        
        count = st.number_input("残り回数 (到達まで)", min_value=1, value=1, step=1, key="lot_reg_count")
        
        if st.button("登録の確定", type="primary", use_container_width=True):
            if not series_skill.strip() or not group_skill.strip():
                st.error("スキルを選択してください")
            else:
                record_id = register_upgrade(w_type, element, series_skill, group_skill, count, user_id=user_id)
                if record_id:
                    st.toast("登録完了")
                    st.rerun()
                else:
                    st.error("登録失敗")
