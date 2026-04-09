import streamlit as st
from src.logic.equipment_box import (
    add_equipment, validate_restoration_bonuses
)
from src.components.pickers import render_skill_picker

@st.fragment
def render_registration_section(master, user_id):
    """武器を新規登録するためのフォーム。Fragment化により独立性を確保。"""
    exp_expanded = st.session_state.get("tracker_reg_w_id") is not None
    
    with st.expander("➕ 武器を新規登録する", expanded=exp_expanded):
        weapon_name = st.text_input("識別名", placeholder="例: 火竜大剣用", key="reg_w_name")
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            w_type = st.selectbox("Weapon Type", master.get("weapon_types", []), key="reg_w_type")
        with c2:
            element = st.selectbox("Element", master.get("elements", []), key="reg_w_elem")
        with c3:
            enhancement = st.selectbox("巨戟強化種別", master.get("kyogeki_enhancements", []), key="reg_w_enh")

        st.markdown("**付与されているスキル**")
        c_reg_s, c_reg_g = st.columns(2)
        with c_reg_s: current_series = render_skill_picker("シリーズスキル", master.get("series_skills", []), "series", "reg_s")
        with c_reg_g: current_group = render_skill_picker("グループスキル", master.get("group_skills", []), "group", "reg_g")
            
        st.markdown("**生産ボーナス**")
        pc1, pc2, pc3 = st.columns(3)
        with pc1: pb1 = st.selectbox("枠1", master.get("production_bonuses", []), key="reg_pb1")
        with pc2: pb2 = st.selectbox("枠2", master.get("production_bonuses", []), key="reg_pb2")
        with pc3: pb3 = st.selectbox("枠3", master.get("production_bonuses", []), key="reg_pb3")
        
        # Dynamic Restoration Options
        is_bow = ("弓" in w_type and "ボウガン" not in w_type)
        is_bowgun = ("ボウガン" in w_type)
        
        dynamic_rest_options = ["なし"]
        for r_type, levels in master.get("restoration_bonuses", {}).items():
            if r_type == "なし": continue
            if r_type == "切れ味強化" and (is_bow or is_bowgun): continue
            if r_type == "装填強化" and not is_bowgun: continue
            if r_type == "属性強化":
                if element == "無": continue
                if is_bow and element in ["毒", "麻痺", "睡眠", "爆破"]: continue
                
            for lv in levels:
                label = r_type if lv == "無印" else f"{r_type} [{lv}]"
                dynamic_rest_options.append(label)
                
        st.markdown("**復元ボーナス**")
        rc1, rc2, rc3, rc4, rc5 = st.columns(5)
        with rc1: rb1 = st.selectbox("枠1", dynamic_rest_options, key="reg_rb1")
        with rc2: rb2 = st.selectbox("枠2", dynamic_rest_options, key="reg_rb2")
        with rc3: rb3 = st.selectbox("枠3", dynamic_rest_options, key="reg_rb3")
        with rc4: rb4 = st.selectbox("枠4", dynamic_rest_options, key="reg_rb4")
        with rc5: rb5 = st.selectbox("枠5", dynamic_rest_options, key="reg_rb5")
        
        if st.button("武器を登録", type="primary", key="btn_reg_w"):
            final_weapon_name = weapon_name.strip() or f"無銘の{w_type}"
            parsed_rbs = []
            for rb in [rb1, rb2, rb3, rb4, rb5]:
                if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
                elif " [" in rb:
                    parts = rb.split(" [")
                    parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
                else: parsed_rbs.append({"type": rb, "level": "無印"})
            
            is_valid, err_msg = validate_restoration_bonuses(parsed_rbs)
            if not is_valid: st.error(err_msg)
            else:
                record_id = add_equipment(
                    final_weapon_name, w_type, element, 
                    current_series, current_group, enhancement,
                    [pb1, pb2, pb3], parsed_rbs, user_id=user_id
                )
                if record_id:
                    st.toast(f"{final_weapon_name} を登録しました！", icon="✅")
                    st.rerun()
                else: st.error("登録に失敗しました。")
