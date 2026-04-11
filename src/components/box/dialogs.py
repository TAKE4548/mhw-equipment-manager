import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    update_equipment, validate_restoration_bonuses, delete_equipment
)
from src.logic.favorites import get_favorite_list, prepare_skill_choices
from src.components.pickers import render_skill_picker

@st.dialog("武器情報を編集")
def edit_equipment_dialog(row, user_id):
    """武器の基本情報を編集するダイアログ"""
    master = get_master_data()
    st.markdown(f"#### {row['weapon_name']} の編集")
    
    new_name = st.text_input("武器の識別名", value=row['weapon_name'])
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        w_type = st.selectbox("Weapon Type", master.get("weapon_types", []), index=master.get("weapon_types", []).index(row['weapon_type']))
    with c2:
        element = st.selectbox("Element", master.get("elements", []), index=master.get("elements", []).index(row['element']))
    with c3:
        enhancement = st.selectbox("巨戟強化種別", master.get("kyogeki_enhancements", []), index=master.get("kyogeki_enhancements", []).index(row['enhancement_type']))

    st.markdown("##### 付与スキル")
    c_s, c_g = st.columns(2)
    with c_s: sel_s = render_skill_picker("シリーズスキル", master.get("series_skills", []), "series", "edit_s", current_val=row['current_series_skill'])
    with c_g: sel_g = render_skill_picker("グループスキル", master.get("group_skills", []), "group", "edit_g", current_val=row['current_group_skill'])
    
    st.markdown("##### 生産ボーナス")
    p_opts = master.get("production_bonuses", [])
    pc1, pc2, pc3 = st.columns(3)
    pb1 = pc1.selectbox("枠1", p_opts, index=p_opts.index(row['p_bonus_1']), key="epb1")
    pb2 = pc2.selectbox("枠2", p_opts, index=p_opts.index(row['p_bonus_2']), key="epb2")
    pb3 = pc3.selectbox("枠3", p_opts, index=p_opts.index(row['p_bonus_3']), key="epb3")
    
    st.markdown("##### 復元ボーナス")
    is_bow = ("弓" in w_type and "ボウガン" not in w_type)
    is_bowgun = ("ボウガン" in w_type)
    dyn_opts = ["なし"]
    for rt, lvs in master.get("restoration_bonuses", {}).items():
        if rt == "なし": continue
        if rt == "切れ味強化" and (is_bow or is_bowgun): continue
        if rt == "装填強化" and not is_bowgun: continue
        if rt == "属性強化" and (element == "無" or (is_bow and element in ["毒", "麻痺", "睡眠", "爆破"])): continue
        for lv in lvs:
            dyn_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            
    def get_rb_label(t, l):
        if t == "なし": return "なし"
        return t if l == "無印" else f"{t} [{l}]"
    
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    rb_vals = []
    for i, col in enumerate([rc1, rc2, rc3, rc4, rc5]):
        curr_t = row.get(f'rest_{i+1}_type', 'なし')
        curr_l = row.get(f'rest_{i+1}_level', 'なし')
        curr_t = "なし" if pd.isna(curr_t) else curr_t
        curr_l = "なし" if pd.isna(curr_l) else curr_l
        
        curr_label = get_rb_label(curr_t, curr_l)
        default_idx = dyn_opts.index(curr_label) if curr_label in dyn_opts else 0
        val = col.selectbox(f"枠{i+1}", dyn_opts, index=default_idx, key=f"erb{i+1}")
        rb_vals.append(val)
        
    if st.button("変更を保存", type="primary", use_container_width=True):
        parsed_rbs = []
        for rb in rb_vals:
            if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else: parsed_rbs.append({"type": rb, "level": "無印"})
            
        is_valid, err = validate_restoration_bonuses(parsed_rbs)
        if not is_valid: st.error(err)
        else:
            try:
                if update_equipment(row['id'], new_name, w_type, element, 
                                     sel_s, sel_g,
                                     enhancement, [pb1, pb2, pb3], parsed_rbs, user_id=user_id):
                    st.toast("更新しました！")
                    st.rerun()
                else: st.error("更新に失敗しました。")
            except Exception as e:
                st.error(f"更新失敗: {str(e)}")

