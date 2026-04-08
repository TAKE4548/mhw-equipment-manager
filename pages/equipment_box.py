import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    load_equipment, add_equipment, delete_equipment, update_equipment,
    validate_restoration_bonuses, get_weapon_label, format_bonus_summary, normalize_bonus,
    format_bonus_list, filter_equipment,
    ATTRIBUTE_COLORS
)
from src.logic.favorites import get_favorite_list, prepare_skill_choices, add_favorite, remove_favorite, is_favorite

from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css, render_slim_card, get_badge_html
from src.components.pickers import render_skill_picker
from src.components.auth import get_current_user_id
from src.components.common import render_lean_header, render_item_count, render_item_count

st.set_page_config(page_title="所有武器台帳", page_icon="📦", layout="wide")
inject_card_css()

# Deleted render_skill_selector_with_toggle as it is replaced by render_skill_picker

@st.dialog("武器情報を編集")
def edit_equipment_dialog(row, user_id):
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
    # Fetch current lists for favorites
    fav_s = get_favorite_list("series")
    fav_g = get_favorite_list("group")
    sorted_s, labels_s = prepare_skill_choices(master.get("series_skills", []), fav_s, "skill_parts")
    sorted_g, labels_g = prepare_skill_choices(master.get("group_skills", []), fav_g, "group_name")
    
    # Custom Picker for Skills (Side-by-side)
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
    # Re-calc options based on current edit state
    # Simplified for dialog speed, using a fixed set of options similar to registration
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
            
    # Helper to find index in dyn_opts
    def get_rb_label(t, l):
        if t == "なし": return "なし"
        return t if l == "無印" else f"{t} [{l}]"
    
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    rb_vals = []
    for i, col in enumerate([rc1, rc2, rc3, rc4, rc5]):
        curr_t = row.get(f'rest_{i+1}_type', 'なし')
        curr_l = row.get(f'rest_{i+1}_level', 'なし')
        # Handle Potential NaN from DB
        import numpy as np
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
            if update_equipment(row['id'], new_name, w_type, element, 
                                sel_s, sel_g,
                                enhancement, [pb1, pb2, pb3], parsed_rbs, user_id=user_id):
                st.toast("更新しました！")
                st.rerun()
            else: st.error("更新に失敗しました。")

# Render shared sidebar
render_shared_sidebar()

# Wait for localStorage data to be available
if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
    st.info("⏳ データを読み込み中...")
    st.stop()

from src.logic.history import undo_last_action, redo_last_action, get_history

render_lean_header("所持武器台帳", "所持武器の登録・管理および強化状況の確認を行います。", icon="🎒")
 
user_id = get_current_user_id()

@st.fragment
def render_registration_section(master, user_id):
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
        
        # Dynamic Restoration Options based on Weapon Type
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

master = get_master_data()
render_registration_section(master, user_id)

@st.fragment
def render_equipment_list(master, user_id):
    enhancement_opts = master.get("kyogeki_enhancements", [])
    p_bonus_opts = master.get("production_bonuses", [])

    with st.expander("🔎 条件を指定して絞り込む・並び替え", expanded=False):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            f_name = st.text_input("武器名検索", placeholder="キーワード...", key="f_w_name_list")
            f_types = st.multiselect("武器種", master.get("weapon_types", []), key="f_w_types_list")
        with f_c2:
            f_elements = st.multiselect("属性", master.get("elements", []), key="f_w_elems_list")
            f_enhancements = st.multiselect("巨戟強化", enhancement_opts, key="f_w_enhs_list")
        with f_c3:
            f_sort = st.selectbox("並び替え", ["武器種順", "属性順", "新着順"], index=0, key="f_w_sort_list")

        sf_c1, sf_c2 = st.columns(2)
        with sf_c1:
            f_series = st.multiselect("シリーズスキル", [s['skill_parts'] for s in master.get("series_skills", []) if s['skill_parts'] != "なし"], key="f_w_ser_list")
        with sf_c2:
            f_groups = st.multiselect("グループスキル", [g['group_name'] for g in master.get("group_skills", []) if g['group_name'] != "なし"], key="f_w_grp_list")

        st.markdown("**ボーナス絞り込み**")
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            f_pbs = st.multiselect("生産ボーナス", p_bonus_opts, key="f_w_pbs_list")
        with b_c2:
            f_rbs_opts = []
            for rt, lvs in master.get("restoration_bonuses", {}).items():
                if rt == "なし": continue
                for lv in lvs: f_rbs_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            f_rbs = st.multiselect("復元ボーナス", f_rbs_opts, key="f_w_rbs_list")

    df_raw = load_equipment(user_id)
    df = filter_equipment(df_raw, search_name=f_name, weapon_types=f_types, elements=f_elements, series_skills=f_series, group_skills=f_groups, enhancements=f_enhancements, production_bonuses=f_pbs, restoration_bonuses=f_rbs, sort_by=f_sort)

    render_item_count(len(df))

    if df.empty:
        st.info("条件に一致する武器がありません。")
    else:
        # Localize high-density layout to ONLY the list container
        with st.container():
            st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
            for index, row in df.iterrows():
                elem = row['element']
                bg = ATTRIBUTE_COLORS.get(elem, "#444")
                txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
                badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
                
                w_display = row['weapon_name'] if row['weapon_name'] and not str(row['weapon_name']).startswith("無銘の") else row['weapon_type']
                
                # Summary of bonuses
                pbs = [row.get(f'p_bonus_{i}', 'なし') for i in range(1,4)]
                rbs_with_lv = []
                for i in range(1, 6):
                    rt, rl = row.get(f'rest_{i}_type', 'なし'), row.get(f'rest_{i}_level', 'なし')
                    if rt != 'なし': rbs_with_lv.append(f"{rt}{rl if rl and rl != '無印' else ''}")
                
                bonus_html = f"🛠️ {format_bonus_summary(pbs)} / ✨ {format_bonus_summary(rbs_with_lv)}"
                sub_text = f"📋 {row['enhancement_type']} | 🛡️ {row['current_series_skill']} | 👥 {row['current_group_skill']}"
                
                from src.components.cards import CARD_ACTION_RATIO
                col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
                with col_card:
                    render_slim_card(badge_html, w_display, sub_text, bonus_html, subtitle=row['weapon_type'])
                    
                with col_act:
                    with st.popover("⋮", help="操作メニュー", use_container_width=True, key=f"pop_w_{row['id']}"):
                        if st.button("✏️ 編集", key=f"edit_{row['id']}", use_container_width=True):
                            edit_equipment_dialog(row, user_id)
                        if st.button("🎯 強化厳選へ", key=f"tr_{row['id']}", use_container_width=True):
                            st.session_state.tracker_reg_w_id = row['id']
                            st.switch_page("pages/reinforcement_registration.py")
                        st.divider()
                        if st.button("🗑️ 削除", key=f"del_{row['id']}", type="primary", use_container_width=True):
                            if delete_equipment(row['id'], user_id=user_id):
                                st.toast("武器を削除しました。")
                                st.rerun()

render_equipment_list(master, user_id)
