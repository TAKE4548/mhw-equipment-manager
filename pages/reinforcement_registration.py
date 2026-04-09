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
from src.components.auth import get_current_user_id


from src.components.sidebar import render_shared_sidebar
from src.components.cards import (
    inject_card_css, render_slim_card, get_badge_html, 
    render_selectable_card
)
from src.components.common import render_lean_header, render_item_count

st.set_page_config(page_title="復元強化厳選", page_icon="✨", layout="wide")
inject_card_css()
render_shared_sidebar()

@st.dialog("トラッキング内容を編集")
def edit_tracker_dialog(row, w_row, user_id):
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
        val = st.selectbox(f"枠{i+1}", dyn_opts, index=default_idx, key=f"etrb{i+1}_{row['id']}")
        rb_vals.append(val)
        
    if st.button("保存", type="primary", use_container_width=True):
        parsed_rbs = []
        for rb in rb_vals:
            if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else: parsed_rbs.append({"type": rb, "level": "無印"})
            
        if update_tracker(row['id'], new_count, parsed_rbs, user_id=user_id):
            st.toast("更新しました")
            st.rerun()
        else: st.error("更新に失敗しました")

# --- Header ---
render_lean_header("復元強化厳選", "武器ごとの復元ボーナス進行状況をトラッキングし、抽選結果を反映します。", icon="✨")

user_id = get_current_user_id()
eq_df = load_equipment(user_id)
if eq_df.empty:
    st.warning("まず Equipment Box に武器を登録してください。")
    st.stop()

master = get_master_data()

@st.fragment
def render_registration_section(master, eq_df):
    """v14 Visual Selector: Hierarchical Filtering + Responsive Grid Selection."""
    st.markdown("### 1. 武器を選択")
    
    # --- Hierarchical Filters (4-step) ---
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    
    # Prepare filtered data for options
    cur_df = eq_df.copy()
    
    with f_c1:
        w_types = ["すべて"] + sorted(cur_df['weapon_type'].unique().tolist())
        sel_type = st.selectbox("武器種", w_types, key="h_f_type")
        if sel_type != "すべて": cur_df = cur_df[cur_df['weapon_type'] == sel_type]
        
    with f_c2:
        elems = ["すべて"] + sorted(cur_df['element'].unique().tolist())
        sel_elem = st.selectbox("属性", elems, key="h_f_elem", disabled=len(elems) <= 1)
        if sel_elem != "すべて": cur_df = cur_df[cur_df['element'] == sel_elem]
        
    with f_c3:
        # Combine Series and Group skills for a unified "Focus Skill" filter
        available_skills = set()
        for idx, r in cur_df.iterrows():
            if r['current_series_skill'] != "なし": available_skills.add(r['current_series_skill'])
            if r['current_group_skill'] != "なし": available_skills.add(r['current_group_skill'])
        
        skill_opts = ["すべて"] + sorted(list(available_skills))
        sel_skill = st.selectbox("スキル中心絞り込み", skill_opts, key="h_f_skill", disabled=len(skill_opts) <= 1)
        if sel_skill != "すべて":
            cur_df = cur_df[(cur_df['current_series_skill'] == sel_skill) | (cur_df['current_group_skill'] == sel_skill)]
            
    with f_c4:
        # Bonuses - pooling p_bonus and restoration bonus types for terminal filtering
        available_bonuses = set()
        for idx, r in cur_df.iterrows():
            # Check p_bonuses
            for i in range(1, 4):
                if r[f'p_bonus_{i}'] != "なし": available_bonuses.add(r[f'p_bonus_{i}'])
            # Check current restoration bonuses
            for i in range(1, 6):
                if r[f'rest_{i}_type'] != "なし": available_bonuses.add(r[f'rest_{i}_type'])
        
        bonus_opts = ["すべて"] + sorted(list(available_bonuses))
        sel_bonus = st.selectbox("ボーナス成分で検索", bonus_opts, key="h_f_bonus", disabled=len(bonus_opts) <= 1)
        if sel_bonus != "すべて":
            def check_bonus_exists(row):
                for i in range(1, 4):
                    if row[f'p_bonus_{i}'] == sel_bonus: return True
                for i in range(1, 6):
                    if row[f'rest_{i}_type'] == sel_bonus: return True
                return False
            cur_df = cur_df[cur_df.apply(check_bonus_exists, axis=1)]

    # Sorting
    cur_df = cur_df.sort_values(by=["weapon_type", "element", "weapon_name"])

    # --- Render Results in Native Grid (3-column on desktop) ---
    if cur_df.empty:
        st.info("条件に一致する武器が見つかりません。")
    else:
        st.markdown(f"**候補: {len(cur_df)} 件**")
        
        # Streamlit-native list (1-column for maximum visibility)
        with st.container():
            st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
            for idx, w_row in cur_df.iterrows():
                is_selected = (st.session_state.get("tracker_reg_w_id") == w_row['id'])
                elem = w_row['element']
                bg = ATTRIBUTE_COLORS.get(elem, "#444")
                txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
                badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
                w_display = w_row['weapon_name'] if w_row['weapon_name'] and not str(w_row['weapon_name']).startswith("無銘の") else w_row['weapon_type']
                
                # Preparation for display
                p_bonuses = [w_row[f'p_bonus_{i}'] for i in range(1, 4) if w_row[f'p_bonus_{i}'] != "なし"]
                r_bonuses = [f"{w_row[f'rest_{i}_type']}{w_row[f'rest_{i}_level'] if w_row[f'rest_{i}_level'] != '無印' else ''}" for i in range(1, 6) if w_row[f'rest_{i}_type'] != "なし"]
                
                p_bonus_text = f"🛠️ {format_bonus_summary(p_bonuses)}" if p_bonuses else ""
                r_bonus_text = f"✨ {format_bonus_list(r_bonuses)}"
                
                # Sub-text with maximum-contrast color for visibility
                desc = f"<div style='margin-bottom:4px; color:#ddd;'>📋 {w_row['current_series_skill']} / {w_row['current_group_skill']}</div>"
                desc += f"<div style='font-size:0.75rem; opacity:1.0; color:#bbb; line-height:1.2;'>{p_bonus_text}{'<br>' if p_bonus_text else ''}{r_bonus_text}</div>"
                
                if render_selectable_card(
                    badge_html, w_display, desc, "", 
                    key=f"hsel_{w_row['id']}", 
                    subtitle=w_row['weapon_type'], 
                    is_selected=is_selected,
                    mode="hud"
                ):
                    st.session_state.tracker_reg_w_id = w_row['id']
                    st.rerun()

    # --- Step 2: Registration Form (Visible when weapon selected) ---
    if st.session_state.get("tracker_reg_w_id"):
        st.markdown("---")
        st.markdown("### 2. 抽選結果を入力")
        sel_row = eq_df[eq_df['id'] == st.session_state.tracker_reg_w_id].iloc[0]
        st.info(f"選択中: **{sel_row['weapon_name']}** ({sel_row['weapon_type']})")
        
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
        
        count_val = st.number_input("残り回数 (目標までのスキップ数)", min_value=1, value=1, step=1, key="tr_count")
        
        b_c1, b_c2 = st.columns([7, 3])
        if b_c1.button("トラッキングに追加", type="primary", use_container_width=True):
            parsed_rbs = []
            for rb in [tb1, tb2, tb3, tb4, tb5]:
                if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
                elif " [" in rb:
                    parts = rb.split(" [")
                    parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
                else: parsed_rbs.append({"type": rb, "level": "無印"})
            if register_tracker(st.session_state.tracker_reg_w_id, count_val, parsed_rbs, user_id=user_id):
                st.session_state.tracker_reg_w_id = None
                st.toast("トラッキングに追加しました", icon="📋")
                st.rerun()
            else: st.error("保存に失敗しました")
        
        if b_c2.button("キャンセル", use_container_width=True):
            st.session_state.tracker_reg_w_id = None
            st.rerun()

# --- Tracking List Toolbar ---
@st.fragment
def render_active_tracker_list(master, eq_df, user_id):
    tracker_df = load_trackers(user_id)

    if tracker_df.empty:
        st.info("トラッキング中の強化抽選結果はありません。")
        return

    # --- Toolbar for Tracker List ---
    with st.expander("🔎 トラッキングを絞り込む・並び替え", expanded=False):
        t_c1, t_c2, t_c3 = st.columns(3)
        with t_c1:
            t_f_types = st.multiselect("武器種で絞り込み", master.get("weapon_types", []), key="t_filter_type")
        with t_c2:
            t_f_elems = st.multiselect("属性で絞り込み", master.get("elements", []), key="t_filter_elem")
        with t_c3:
            t_f_sort = st.selectbox("並び替え", ["残り回数(少)", "残り回数(多)", "武器種順", "属性順", "新着順"], index=0, key="t_sort_by")

        st.markdown("**ボーナス絞り込み**")
        tb_c1, tb_c2 = st.columns(2)
        with tb_c1:
            t_f_rbs_opts = []
            for rt, lvs in master.get("restoration_bonuses", {}).items():
                if rt == "なし": continue
                for lv in lvs: t_f_rbs_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            t_f_rbs = st.multiselect("目標復元ボーナス (AND検索)", t_f_rbs_opts, key="t_filter_rbs")

    # Apply Filtering to Tracker List
    merged_df = tracker_df.merge(eq_df, left_on='weapon_id', right_on='id', suffixes=('', '_eq'))
    
    if t_f_types: merged_df = merged_df[merged_df['weapon_type'].isin(t_f_types)]
    if t_f_elems: merged_df = merged_df[merged_df['element'].isin(t_f_elems)]

    if t_f_rbs:
        # Target tuples for robust matching
        target_tuples = []
        for s in t_f_rbs:
            if " [" in s:
                parts = s.split(" [")
                target_tuples.append((parts[0], parts[1][:-1]))
            else:
                target_tuples.append((s, "無印"))
        target_set = set(target_tuples)

        def check_tracker_rbs(row):
            tr_bonuses = set()
            for i in range(1, 6):
                rt, rl = row[f'target_rest_{i}_type'], row[f'target_rest_{i}_level']
                if rt != "なし":
                    tr_bonuses.add((rt, rl))
            return target_set.issubset(tr_bonuses)
        
        merged_df = merged_df[merged_df.apply(check_tracker_rbs, axis=1)]
    
    # Apply Sorting
    w_order = master.get("weapon_types", []); e_order = master.get("elements", [])
    merged_df['weapon_type'] = pd.Categorical(merged_df['weapon_type'], categories=w_order, ordered=True)
    merged_df['element'] = pd.Categorical(merged_df['element'], categories=e_order, ordered=True)
    
    if t_f_sort == "残り回数(少)": merged_df = merged_df.sort_values(by=["remaining_count", "weapon_type", "element"])
    elif t_f_sort == "残り回数(多)": merged_df = merged_df.sort_values(by=["remaining_count", "weapon_type", "element"], ascending=[False, True, True])
    elif t_f_sort == "武器種順": merged_df = merged_df.sort_values(by=["weapon_type", "element", "remaining_count"])
    elif t_f_sort == "属性順": merged_df = merged_df.sort_values(by=["element", "weapon_type", "remaining_count"])
    else: merged_df = merged_df.sort_index(ascending=False)

    # --- Pre-calculation for all rows (O(N) outside loop) ---
    def get_slot_labels(row, prefix=""):
        return [get_abbr_item(f"{row.get(f'{prefix}rest_{i}_type','なし')}{row.get(f'{prefix}rest_{i}_level','')}" 
                               if row.get(f'{prefix}rest_{i}_type','なし') != "なし" else "なし") for i in range(1,6)]

    merged_df['curr_labels'] = merged_df.apply(lambda r: get_slot_labels(r), axis=1)
    merged_df['target_labels'] = merged_df.apply(lambda r: get_slot_labels(r, prefix="target_"), axis=1)

    def build_visual_comparison(before, after):
        # v14: ONE-LINE MICRO DIFF BAR (with spacing)
        bc = " ".join([f'<span style="color:#666; font-size:0.78rem; margin-right:4px;">{s}</span>' for s in before])
        # After labels: Highlight changes in yellow, with breathing room
        ac = []
        for i, s in enumerate(after):
            is_changed = (s != before[i])
            clr = "#f1c40f" if is_changed else "#ccc"
            fw = "bold" if is_changed else "normal"
            ac.append(f'<span style="color:{clr}; font-weight:{fw}; font-size:0.9rem; margin-right:8px; display:inline-block;">{s}</span>')
        
        h = '<div style="display:flex; align-items:center; gap:10px; white-space:nowrap;">'
        h += f'<div style="display:flex; align-items:center; opacity:0.7;">{bc}</div>'
        h += '<span style="color:#ffd700; font-size:0.85rem; flex-shrink:0;">❯❯</span>'
        h += f'<div style="display:flex; align-items:center;">{" ".join(ac)}</div>'
        h += '</div>'
        return h

    # Render Tracker Cards
    render_item_count(len(merged_df))
    
    # Localize high-density layout to ONLY the list container
    with st.container():
        st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
        for index, row in merged_df.iterrows():
            comp_html = build_visual_comparison(row['curr_labels'], row['target_labels'])
        
            rem = row['remaining_count']
            badge_html = get_badge_html(row['element'], bgcolor=ATTRIBUTE_COLORS.get(row['element'], "#444"), color=("black" if row['element'] in ["氷", "雷", "無", "睡眠"] else "white"))
            w_display = row['weapon_name'] if row['weapon_name'] and not str(row['weapon_name']).startswith("無銘の") else row['weapon_type']
            col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
            
            # REQ-026: Unify count position (Metric) and Comparison Bar position (Spec)
            sub_text = f"<span style='opacity:0.8; margin-right:12px;'>{row['current_series_skill']} / {row['current_group_skill']}</span> {comp_html}"
            metric_html = f"<b style='color:{col_c};'>あと{rem}回</b>"
            
            from src.components.cards import CARD_ACTION_RATIO, render_slim_card
            col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
            with col_card:
                render_slim_card(badge_html, w_display, sub_text, metric_html, subtitle=row['weapon_type'], mode="hud")
            with col_act:
                with st.popover("⋮", use_container_width=True, key=f"pop_{row['id']}"):
                    if st.button("🔨 進行/適用", key=f"ap_{row['id']}", use_container_width=True):
                        if execute_apply_and_advance(row['id'], user_id=user_id): st.rerun()
                    if st.button("✏️ 編集", key=f"ed_tr_{row['id']}", use_container_width=True):
                        edit_tracker_dialog(row, row, user_id)
                    st.divider()
                    if st.button("🗑️ 削除", key=f"dl_{row['id']}", type="primary", use_container_width=True):
                        if delete_tracker(row['id'], user_id=user_id): st.rerun()

# --- Content Flow ---
with st.expander("✨ 新しい強化抽選を登録する", expanded=st.session_state.get("tracker_reg_w_id") is not None):
    render_registration_section(master, eq_df)

render_active_tracker_list(master, eq_df, user_id)
