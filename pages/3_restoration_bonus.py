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

init_session_state()

st.set_page_config(page_title="Restoration Bonus Tracker", page_icon="✨", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

# Badge CSS helper
def get_badge_html(text, bgcolor="#444", color="white"):
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; font-weight: bold; margin-right: 8px; display: inline-block;">{text}</span>'

# --- Header ---
st.title("Restoration Bonus Tracker ✨")
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

# Build dropdown with simplified labels
weapon_options = {}
for _, row in eq_df.iterrows():
    weapon_options[row['id']] = get_weapon_label(row)

master = get_master_data()

st.subheader("新しい目標組み合わせを記録")
with st.expander("➕ 目標を登録する", expanded=False):
    sel_w_id = st.selectbox("対象の武器を選択", list(weapon_options.keys()), format_func=lambda x: weapon_options[x], key="reg_sel_w")
    
    # Get selected weapon type for filtering
    sel_row = eq_df[eq_df['id'] == sel_w_id].iloc[0]
    sel_w_type = sel_row['weapon_type']
    is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
    is_bowgun = ("ボウガン" in sel_w_type)
    
    dynamic_rest_options = ["なし"]
    for r_type, levels in master.get("restoration_bonuses", {}).items():
        if r_type == "なし": continue
        if r_type == "切れ味強化" and (is_bow or is_bowgun):
            continue
        if r_type == "装填強化" and not is_bowgun:
            continue
        for lv in levels:
            label = r_type if lv == "無印" else f"{r_type} [{lv}]"
            dynamic_rest_options.append(label)
            
    st.markdown("##### 目標の復元ボーナス (最大5枠)")
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    with rc1: tb1 = st.selectbox("枠1", dynamic_rest_options, key="tb1")
    with rc2: tb2 = st.selectbox("枠2", dynamic_rest_options, key="tb2")
    with rc3: tb3 = st.selectbox("枠3", dynamic_rest_options, key="tb3")
    with rc4: tb4 = st.selectbox("枠4", dynamic_rest_options, key="tb4")
    with rc5: tb5 = st.selectbox("枠5", dynamic_rest_options, key="tb5")
    
    count_val = st.number_input("この組み合わせが出るまでの残り回数", min_value=1, value=1, step=1)
        
    if st.button("トラッキングに追加", type="primary"):
        parsed_rbs = []
        for rb in [tb1, tb2, tb3, tb4, tb5]:
            if rb == "なし":
                parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else:
                parsed_rbs.append({"type": rb, "level": "無印"})
        
        is_valid, err_msg = validate_restoration_bonuses(parsed_rbs)
        if not is_valid:
            st.error(err_msg)
        else:
            record_id = register_tracker(sel_w_id, count_val, parsed_rbs)
            if record_id:
                st.success("トラッキング情報を追加しました！")
                st.rerun()
            else:
                st.error("登録に失敗しました。")

st.divider()
st.subheader("現在トラッキング中の目標")

tracker_df = load_trackers()

if tracker_df.empty:
    st.info("トラッキング中の復元ボーナスはありません。")
else:
    st.caption("※適用により他武器のチャンスが追い越された場合、それらの目標はリストから自動削除されます。")
    
    # Pre-map weapon info for the cards
    tracker_df = tracker_df.sort_values(by=["remaining_count"])
    
    for index, row in tracker_df.iterrows():
        w_id = row['weapon_id']
        w_info = eq_df[eq_df['id'] == w_id]
        if w_info.empty: continue
        w_row = w_info.iloc[0]
        
        with st.container(border=True):
            # Layout: [Remaining Count Box] | [Weapon Detail Card] | [Apply Button]
            c1, c2, c3 = st.columns([1.5, 5, 2], vertical_alignment="center")
            
            with c1:
                rem = row['remaining_count']
                col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <p style='margin:0; font-size:0.8em; opacity:0.8;'>残り</p>
                        <h2 style='color:{col_c}; margin:0; font-weight:bold;'>{rem} <span style='font-size:0.5em;'>回</span></h2>
                        {"<p style='color:#ff4b4b; font-size:0.7em; margin-top:5px; font-weight:bold;'>⚠️ NEXT SKIP</p>" if rem <= 1 else ""}
                    </div>
                """, unsafe_allow_html=True)
                
            with c2:
                # Weapon Badge and Target
                elem = w_row['element']
                bg = ATTRIBUTE_COLORS.get(elem, "#444")
                txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
                badge_html = get_badge_html(f"{w_row['weapon_type']} | {elem}", bgcolor=bg, color=txt_c)
                
                # Format Target Bonuses as a row of small chips
                target_rbs_list = []
                for i in range(1, 6):
                    rt = row.get(f'target_rest_{i}_type', 'なし')
                    rl = row.get(f'target_rest_{i}_level', 'なし')
                    if rt != 'なし':
                        nt, nl = normalize_bonus(rt, rl, is_restoration=True)
                        suffix = nl if nl and nl != "無印" else ""
                        target_rbs_list.append(f"{nt}{suffix}")
                
                target_str = format_bonus_summary(target_rbs_list)
                
                display_name = w_row['weapon_name']
                is_named = display_name and not display_name.startswith("無銘の")
                
                st.markdown(f"""
                    {badge_html} **{display_name if is_named else w_row['weapon_type']}**
                    <div style='margin-top:8px; background-color:rgba(255,255,255,0.05); padding:8px; border-radius:6px; font-size:0.9em;'>
                        ✨ <b>目標</b>: <code style='background:none;'>{target_str}</code>
                    </div>
                """, unsafe_allow_html=True)
                
            with c3:
                btn_label = f"適用 🎁 (-{row['remaining_count']})"
                if st.button(btn_label, key=f"apply_{row['id']}", use_container_width=True, type="primary"):
                    if execute_apply_and_advance(row['id']):
                        st.success("適用完了")
                        st.rerun()
                
                if st.button("削除 🗑️", key=f"del_track_{row['id']}", use_container_width=True):
                    if delete_tracker(row['id']):
                        st.rerun()
