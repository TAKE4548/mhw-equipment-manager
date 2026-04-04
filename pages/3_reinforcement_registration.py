import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    load_equipment, validate_restoration_bonuses, 
    get_weapon_label, format_bonus_summary, normalize_bonus,
    ATTRIBUTE_COLORS
)
from src.logic.restoration_tracker import (
    load_trackers, register_tracker, advance_all_trackers, 
    delete_tracker, execute_apply_and_advance, undo_action, redo_action
)

def init_session_state():
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets
    if 'history_undo' not in st.session_state:
        st.session_state.history_undo = []
    if 'history_redo' not in st.session_state:
        st.session_state.history_redo = []
    # Persistent selection for registration
    if 'tracker_reg_w_id' not in st.session_state:
        st.session_state.tracker_reg_w_id = None

init_session_state()

st.set_page_config(page_title="強化厳選登録", page_icon="✨", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

# Helper for badges
def get_badge_html(text, bgcolor="#444", color="white"):
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 1px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold; display: inline-block; min-width: 45px; text-align: center;">{text}</span>'

# --- Header ---
st.title("強化厳選登録 ✨")
st.markdown("武器ごとに、未来の抽選結果（複数）をトラッキングします。")

# History Controls
h_col1, h_col2, h_col3 = st.columns([1, 1, 6])
with h_col1:
    undo_disabled = not st.session_state.history_undo
    if st.button("Undo ↩️", disabled=undo_disabled, use_container_width=True):
        if undo_action():
            st.toast("元に戻しました")
            st.rerun()
with h_col2:
    redo_disabled = not st.session_state.history_redo
    if st.button("Redo ↪️", disabled=redo_disabled, use_container_width=True):
        if redo_action():
            st.toast("やり直しました")
            st.rerun()

st.divider()

eq_df = load_equipment()
if eq_df.empty:
    st.warning("まず Equipment Box に武器を登録してください。")
    st.stop()

master = get_master_data()

st.subheader("新しい強化抽選結果を記録")
# Multi-stage registration with visual selection
exp_expanded = st.session_state.tracker_reg_w_id is not None
with st.expander("➕ 抽選結果を登録する", expanded=exp_expanded):
    # Step 1: Weapon Selection List
    st.markdown("##### 1. 対象の武器を選択")
    
    # Render mini-cards for selection
    # Limit number shown or use scroll if many, but let's just render all for now
    for idx, w_row in eq_df.iterrows():
        is_selected = (st.session_state.tracker_reg_w_id == w_row['id'])
        row_bg = "rgba(255, 255, 255, 0.05)" if is_selected else "transparent"
        border_c = "#4d90fe" if is_selected else "#444"
        
        with st.container(border=True):
            # Compact row for selection
            sc1, sc2, sc3, sc4, sc5 = st.columns([0.6, 2.5, 2.0, 3.0, 0.6], vertical_alignment="center")
            
            # Badge
            elem = w_row['element']
            bg = ATTRIBUTE_COLORS.get(elem, "#444")
            txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
            sc1.markdown(get_badge_html(elem, bgcolor=bg, color=txt_c), unsafe_allow_html=True)
            
            # Name
            w_name = w_row['weapon_name'] if w_row['weapon_name'] and not w_row['weapon_name'].startswith("無銘の") else w_row['weapon_type']
            sc2.markdown(f"**{w_name}**")
            
            # Enhancement / Skill brief
            sc3.markdown(f"<small>📋 {w_row['enhancement_type']}<br>🛡️ {w_row['current_series_skill']}</small>", unsafe_allow_html=True)
            
            # Current Restoration
            curr_rbs = []
            for i in range(1, 6):
                rt, rl = w_row[f'rest_{i}_type'], w_row[f'rest_{i}_level']
                if rt != "なし":
                    curr_rbs.append(f"{rt}{rl if rl != '無印' else ''}")
                else: curr_rbs.append("なし")
            from src.logic.equipment_box import format_bonus_list
            sc4.markdown(f"✨ <small>{format_bonus_list(curr_rbs)}</small>", unsafe_allow_html=True)
            
            # Select button
            if sc5.button("選択", key=f"sel_{w_row['id']}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.tracker_reg_w_id = w_row['id']
                st.rerun()

    # Step 2: Show form only if selected
    if st.session_state.tracker_reg_w_id:
        st.divider()
        sel_row = eq_df[eq_df['id'] == st.session_state.tracker_reg_w_id].iloc[0]
        st.markdown(f"##### 2. 「{sel_row['weapon_name']}」の抽選結果を入力")
        
        sel_w_type = sel_row['weapon_type']
        is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
        is_bowgun = ("ボウガン" in sel_w_type)
        
        dynamic_rest_options = ["なし"]
        for r_type, levels in master.get("restoration_bonuses", {}).items():
            if r_type == "なし": continue
            if r_type == "切れ味強化" and (is_bow or is_bowgun): continue
            if r_type == "装填強化" and not is_bowgun: continue
            for lv in levels:
                label = r_type if lv == "無印" else f"{r_type} [{lv}]"
                dynamic_rest_options.append(label)
                
        rc1, rc2, rc3, rc4, rc5 = st.columns(5)
        with rc1: tb1 = st.selectbox("枠1", dynamic_rest_options, key="tb1")
        with rc2: tb2 = st.selectbox("枠2", dynamic_rest_options, key="tb2")
        with rc3: tb3 = st.selectbox("枠3", dynamic_rest_options, key="tb3")
        with rc4: tb4 = st.selectbox("枠4", dynamic_rest_options, key="tb4")
        with rc5: tb5 = st.selectbox("枠5", dynamic_rest_options, key="tb5")
        
        count_val = st.number_input("残り回数", min_value=1, value=1, step=1)
        if st.button("トラッキングに追加", type="primary"):
            parsed_rbs = []
            for rb in [tb1, tb2, tb3, tb4, tb5]:
                if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
                elif " [" in rb:
                    parts = rb.split(" [")
                    parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
                else: parsed_rbs.append({"type": rb, "level": "無印"})
            
            is_valid, err_msg = validate_restoration_bonuses(parsed_rbs)
            if not is_valid: st.error(err_msg)
            else:
                if register_tracker(st.session_state.tracker_reg_w_id, count_val, parsed_rbs):
                    st.session_state.tracker_reg_w_id = None # Clear after success
                    st.success("追加しました")
                    st.rerun()

st.divider()
st.subheader("トラッキング中の抽選結果 (残り回数順)")
tracker_df = load_trackers()

if tracker_df.empty:
    st.info("トラッキング中の強化抽選結果はありません。")
else:
    tracker_df = tracker_df.sort_values(by=["remaining_count"])
    for index, row in tracker_df.iterrows():
        w_id = row['weapon_id']
        w_info = eq_df[eq_df['id'] == w_id]
        if w_info.empty: continue
        w_row = w_info.iloc[0]
        rem = row['remaining_count']
        
        with st.container(border=True):
            cols = st.columns([0.6, 0.6, 1.2, 1.1, 1.4, 3.4, 1.7], vertical_alignment="center")
            
            # Remaining Count
            col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
            cols[0].markdown(f"<div style='text-align:center; background:{col_c}22; border-radius:4px; padding:2px;'><small style='color:{col_c};'><b>{rem}</b>回</small></div>", unsafe_allow_html=True)
            
            # Badge
            elem = w_row['element']
            bg = ATTRIBUTE_COLORS.get(elem, "#444")
            txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
            cols[1].markdown(get_badge_html(elem, bgcolor=bg, color=txt_c), unsafe_allow_html=True)
            
            # Name
            w_name = w_row['weapon_name'] if w_row['weapon_name'] and not w_row['weapon_name'].startswith("無銘の") else w_row['weapon_type']
            cols[2].markdown(f"**{w_name}**")
            
            # Enhancement / PB (Stacked)
            pbs = [w_row.get(f'p_bonus_{i}', 'なし') for i in range(1,4)]
            from src.logic.equipment_box import format_bonus_list
            cols[3].markdown(f"<small>📋 {w_row['enhancement_type']}<br>🛠️ {format_bonus_list(pbs)}</small>", unsafe_allow_html=True)

            # Skills (Stacked)
            cols[4].markdown(f"<small>🛡️ {w_row['current_series_skill']}<br>👥 {w_row['current_group_skill']}</small>", unsafe_allow_html=True)

            # Comparison Table (Current vs Target)
            from src.logic.equipment_box import get_abbr_item
            curr_slots = [get_abbr_item(f"{w_row.get(f'rest_{i}_type','なし')}{w_row.get(f'rest_{i}_level','')}" if w_row.get(f'rest_{i}_type','なし') != "なし" else "なし") for i in range(1,6)]
            target_slots = [get_abbr_item(f"{row.get(f'target_rest_{i}_type','なし')}{row.get(f'target_rest_{i}_level','')}" if row.get(f'target_rest_{i}_type','なし') != "なし" else "なし") for i in range(1,6)]

            def build_comparison_row(title, slots, diff_against=None):
                row_html = f'<tr><td style="padding-right:8px; color:#aaa; font-size:0.75em; border:none; text-align:right;">{title}</td>'
                for i, s in enumerate(slots):
                    is_diff = diff_against and s != diff_against[i]
                    style = "min-width:65px; padding:0 8px; font-size:0.75em; border:none;"
                    if is_diff:
                        style += " font-weight:bold; color:white; background-color:rgba(255,255,255,0.15); border-radius:4px;"
                    row_html += f'<td style="{style}">{s}</td>'
                row_html += '</tr>'
                return row_html

            table_html = f"""
            <table style="border-collapse:separate; border-spacing:0 2px; border:none; background:transparent; margin:0;">
                {build_comparison_row('現:', curr_slots)}
                {build_comparison_row('目:', target_slots, diff_against=curr_slots)}
            </table>
            """
            cols[5].markdown(table_html, unsafe_allow_html=True)
            
            # Actions
            ac1, ac2 = cols[6].columns([3, 1])
            if ac1.button("🔨 強化実施", key=f"ap_{row['id']}", use_container_width=True):
                if execute_apply_and_advance(row['id']): st.rerun()
            if ac2.button("🗑️", key=f"dl_{row['id']}", use_container_width=True):
                if delete_tracker(row['id']): st.rerun()
