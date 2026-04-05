import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    load_equipment, validate_restoration_bonuses, 
    get_weapon_label, format_bonus_summary, normalize_bonus,
    format_bonus_list, filter_equipment, get_abbr_item,
    ATTRIBUTE_COLORS
)
from src.logic.restoration_tracker import (
    load_trackers, register_tracker, advance_all_trackers, 
    delete_tracker, execute_apply_and_advance,
    update_tracker
)

from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css, render_slim_card, get_badge_html

st.set_page_config(page_title="復元強化厳選", page_icon="✨", layout="wide")
inject_card_css()

# Render shared sidebar
render_shared_sidebar()

@st.dialog("トラッキング内容を編集")
def edit_tracker_dialog(row, w_row):
    master = get_master_data()
    st.markdown(f"**{w_row['weapon_name']}** のトラッキング編集")
    
    new_count = st.number_input("残り回数", min_value=1, value=int(row['remaining_count']))
    
    sel_w_type = w_row['weapon_type']
    sel_element = w_row['element']
    is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
    is_bowgun = ("ボウガン" in sel_w_type)
    
    dyn_opts = ["なし"]
    for rt, lvs in master.get("restoration_bonuses", {}).items():
        if rt == "なし": continue
        if rt == "切れ味強化" and (is_bow or is_bowgun): continue
        if rt == "装填強化" and not is_bowgun: continue
        if rt == "属性強化" and (sel_element == "無" or (is_bow and sel_element in ["毒", "麻痺", "睡眠", "爆破"])): continue
        for lv in lvs:
            dyn_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            
    def get_rb_label(t, l):
        if t == "なし": return "なし"
        return t if l == "無印" else f"{t} [{l}]"
    
    rb_vals = []
    for i in range(5):
        curr_t = row.get(f'target_rest_{i+1}_type', 'なし')
        curr_l = row.get(f'target_rest_{i+1}_level', 'なし')
        # Handle Potential NaN from DB
        import numpy as np
        curr_t = "なし" if pd.isna(curr_t) else curr_t
        curr_l = "なし" if pd.isna(curr_l) else curr_l
        
        curr_label = get_rb_label(curr_t, curr_l)
        default_idx = dyn_opts.index(curr_label) if curr_label in dyn_opts else 0
        val = st.selectbox(f"枠{i+1}", dyn_opts, index=default_idx, key=f"etrb{i+1}")
        rb_vals.append(val)
        
    if st.button("保存", type="primary", use_container_width=True):
        parsed_rbs = []
        for rb in rb_vals:
            if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else: parsed_rbs.append({"type": rb, "level": "無印"})
            
        if update_tracker(row['id'], new_count, parsed_rbs):
            st.toast("更新しました")
            st.rerun()
        else: st.error("更新に失敗しました")

# --- Header ---
st.title("強化厳選登録 ✨")
st.markdown("武器ごとに、未来の抽選結果（複数）をトラッキングします。")

from src.logic.history import undo_last_action, redo_last_action, get_history

# ... (header area)
# History Controls
h_col1, h_col2, h_col3 = st.columns([1, 1, 6])
undo_stack, redo_stack = get_history()
with h_col1:
    if st.button("Undo ↩️", disabled=not undo_stack, use_container_width=True):
        if undo_last_action(): st.rerun()
with h_col2:
    if st.button("Redo ↪️", disabled=not redo_stack, use_container_width=True):
        if redo_last_action(): st.rerun()

st.divider()

eq_df = load_equipment()
if eq_df.empty:
    st.warning("まず Equipment Box に武器を登録してください。")
    st.stop()

master = get_master_data()

st.subheader("新しい強化抽選結果を記録")
exp_expanded = st.session_state.tracker_reg_w_id is not None
with st.expander("➕ 抽選結果を登録する", expanded=exp_expanded):
    st.markdown("##### 1. 対象の武器を選択")
    with st.expander("🔎 条件を指定して武器を探す", expanded=False):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            f_name = st.text_input("武器名で検索", placeholder="キーワード入力...")
            f_types = st.multiselect("武器種", master.get("weapon_types", []))
        with f_c2:
            f_elements = st.multiselect("属性", master.get("elements", []))
            f_enhancements = st.multiselect("巨戟強化", master.get("kyogeki_enhancements", []))
        with f_c3:
            f_sort = st.selectbox("並び替え", ["武器種順", "属性順", "新着順"], index=0)
            
    eq_df_filtered = filter_equipment(eq_df, search_name=f_name, weapon_types=f_types, elements=f_elements, enhancements=f_enhancements, sort_by=f_sort)
    
    for idx, w_row in eq_df_filtered.iterrows():
        is_selected = (st.session_state.tracker_reg_w_id == w_row['id'])
        elem = w_row['element']
        bg = ATTRIBUTE_COLORS.get(elem, "#444")
        txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
        badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
        w_display = w_row['weapon_name'] if w_row['weapon_name'] and not w_row['weapon_name'].startswith("無銘の") else w_row['weapon_type']
        
        # Render Selection Card
        col_c, col_b = st.columns([12, 1], vertical_alignment="center")
        with col_c:
            curr_rbs = []
            for i in range(1, 6):
                rt, rl = w_row[f'rest_{i}_type'], w_row[f'rest_{i}_level']
                curr_rbs.append(f"{rt}{rl if rl != '無印' else ''}" if rt != "なし" else "なし")
            bonus_html = f"✨ {format_bonus_list(curr_rbs)}"
            sub_text = f"📋 {w_row['enhancement_type']} | 🛡️ {w_row['current_series_skill']}"
            render_slim_card(badge_html, w_display, sub_text, bonus_html, subtitle=w_row['weapon_type'])
        with col_b:
            if st.button("選", key=f"sel_{w_row['id']}", type="primary" if is_selected else "secondary", use_container_width=True):
                st.session_state.tracker_reg_w_id = w_row['id']
                st.rerun()

    if st.session_state.tracker_reg_w_id:
        st.divider()
        sel_row = eq_df[eq_df['id'] == st.session_state.tracker_reg_w_id].iloc[0]
        st.markdown(f"##### 2. 「{sel_row['weapon_name']}」の抽選結果を入力")
        sel_w_type, sel_element = sel_row['weapon_type'], sel_row['element']
        is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
        is_bowgun = ("ボウガン" in sel_w_type)
        
        dynamic_rest_options = ["なし"]
        for r_type, levels in master.get("restoration_bonuses", {}).items():
            if r_type == "なし": continue
            if r_type == "切れ味強化" and (is_bow or is_bowgun): continue
            if r_type == "装填強化" and not is_bowgun: continue
            if r_type == "属性強化" and (sel_element == "無" or (is_bow and sel_element in ["毒", "麻痺", "睡眠", "爆破"])): continue
            for lv in levels: dynamic_rest_options.append(r_type if lv == "無印" else f"{r_type} [{lv}]")
                
        rc1, rc2, rc3, rc4, rc5 = st.columns(5)
        tb1 = rc1.selectbox("枠1", dynamic_rest_options, key="tb1")
        tb2 = rc2.selectbox("枠2", dynamic_rest_options, key="tb2")
        tb3 = rc3.selectbox("枠3", dynamic_rest_options, key="tb3")
        tb4 = rc4.selectbox("枠4", dynamic_rest_options, key="tb4")
        tb5 = rc5.selectbox("枠5", dynamic_rest_options, key="tb5")
        
        count_val = st.number_input("残り回数", min_value=1, value=1, step=1)
        if st.button("トラッキングに追加", type="primary", use_container_width=True):
            parsed_rbs = []
            for rb in [tb1, tb2, tb3, tb4, tb5]:
                if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
                elif " [" in rb:
                    parts = rb.split(" [")
                    parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
                else: parsed_rbs.append({"type": rb, "level": "無印"})
            if register_tracker(st.session_state.tracker_reg_w_id, count_val, parsed_rbs):
                st.session_state.tracker_reg_w_id = None
                st.toast("追加しました", icon="📋")
                st.rerun()

st.divider()
st.subheader("トラッキング中の抽選結果 (残り回数順)")
tracker_df = load_trackers()

if tracker_df.empty:
    st.info("トラッキング中の強化抽選結果はありません。")
else:
    tracker_df = tracker_df.sort_values(by=["remaining_count"])
    for index, row in tracker_df.iterrows():
        w_info = eq_df[eq_df['id'] == row['weapon_id']]
        if w_info.empty: continue
        w_row = w_info.iloc[0]
        rem = row['remaining_count']
        
        elem = w_row['element']
        bg = ATTRIBUTE_COLORS.get(elem, "#444")
        txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
        badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
        w_display = w_row['weapon_name'] if w_row['weapon_name'] and not w_row['weapon_name'].startswith("無銘の") else w_row['weapon_type']
        
        # Build Comparison Table for bonus_html
        curr_slots = [get_abbr_item(f"{w_row.get(f'rest_{i}_type','なし')}{w_row.get(f'rest_{i}_level','')}" if w_row.get(f'rest_{i}_type','なし') != "なし" else "なし") for i in range(1,6)]
        target_slots = [get_abbr_item(f"{row.get(f'target_rest_{i}_type','なし')}{row.get(f'target_rest_{i}_level','')}" if row.get(f'target_rest_{i}_type','なし') != "なし" else "なし") for i in range(1,6)]
        
        def build_comp_mini(title, slots, diff=None):
            h = f'<tr><td style="color:#888; font-size:0.8em; padding-right:5px; border:none;">{title}</td>'
            for i, s in enumerate(slots):
                is_d = diff and s != diff[i]
                clr = "#fff" if is_d else "#999"
                fw = "bold" if is_d else "normal"
                h += f'<td style="color:{clr}; font-weight:{fw}; font-size:0.8em; padding:0 4px; border:none;">{s}</td>'
            return h + '</tr>'

        comp_html = f'<div style="background:#222; padding:2px 6px; border-radius:4px;"><table style="border:none; margin:0; border-collapse:collapse;">{build_comp_mini("現", curr_slots)}{build_comp_mini("目", target_slots, diff=curr_slots)}</table></div>'
        
        col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
        sub_text = f"🛡️ {w_row['current_series_skill']} | 👥 {w_row['current_group_skill']} | <b style='color:{col_c};'>あと{rem}回</b>"
        
        col_card, col_act = st.columns([12, 1], vertical_alignment="center")
        with col_card:
            render_slim_card(badge_html, w_display, sub_text, comp_html, subtitle=w_row['weapon_type'])
        with col_act:
            with st.popover("⋮", use_container_width=True):
                if st.button("🔨 進行/適用", key=f"ap_{row['id']}", use_container_width=True):
                    if execute_apply_and_advance(row['id']): st.rerun()
                if st.button("✏️ 編集", key=f"ed_tr_{row['id']}", use_container_width=True):
                    edit_tracker_dialog(row, w_row)
                st.divider()
                if st.button("🗑️ 削除", key=f"dl_{row['id']}", type="primary", use_container_width=True):
                    if delete_tracker(row['id']): st.rerun()
