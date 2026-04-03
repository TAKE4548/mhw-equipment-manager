import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import load_equipment, validate_restoration_bonuses
from src.logic.restoration_tracker import load_trackers, register_tracker, advance_all_trackers, delete_tracker

def init_session_state():
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

st.set_page_config(page_title="Restoration Bonus Tracker", page_icon="✨", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

st.title("Restoration Bonus Tracker ✨")
st.markdown("武器ごとに、未来の引く回数と付与される復元ボーナスの組み合わせ（複数）をトラッキングします。")
st.divider()

eq_df = load_equipment()
if eq_df.empty:
    st.warning("まず Equipment Box に武器を登録してください。")
    st.stop()

# Build dropdown of available weapons
weapon_options = {}
for _, row in eq_df.iterrows():
    label = f"{row['weapon_name']} / {row['weapon_type']} ({row['element']})"
    weapon_options[row['id']] = label

master = get_master_data()

st.subheader("新しい目標組み合わせを記録")
with st.expander("➕ 目標を登録する", expanded=False):
    sel_w_id = st.selectbox("対象の武器を選択", list(weapon_options.keys()), format_func=lambda x: weapon_options[x])
    
    # Get selected weapon type for filtering
    sel_w_type = eq_df[eq_df['id'] == sel_w_id].iloc[0]['weapon_type']
    is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
    is_bowgun = ("ボウガン" in sel_w_type)
    
    dynamic_rest_options = ["なし"]
    for r_type, levels in master.get("restoration_bonuses", {}).items():
        if r_type == "なし": continue
        if r_type == "切れ味(近接)" and (is_bow or is_bowgun):
            continue
        if r_type == "装填数(遠隔)" and not is_bowgun:
            continue
        for lv in levels:
            dynamic_rest_options.append(f"{r_type} [{lv}]")
            
    st.markdown("##### 目標の復元ボーナス (最大5枠)")
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    with rc1: tb1 = st.selectbox("枠1", dynamic_rest_options, key="tb1")
    with rc2: tb2 = st.selectbox("枠2", dynamic_rest_options, key="tb2")
    with rc3: tb3 = st.selectbox("枠3", dynamic_rest_options, key="tb3")
    with rc4: tb4 = st.selectbox("枠4", dynamic_rest_options, key="tb4")
    with rc5: tb5 = st.selectbox("枠5", dynamic_rest_options, key="tb5")
    
    count = st.number_input("この組み合わせが出るまでの残り回数", min_value=1, value=1, step=1)
        
    if st.button("トラッキングに追加", type="primary"):
        parsed_rbs = []
        for rb in [tb1, tb2, tb3, tb4, tb5]:
            if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
            else:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
        
        is_valid, err_msg = validate_restoration_bonuses(parsed_rbs)
        if not is_valid:
            st.error(err_msg)
        else:
            record_id = register_tracker(sel_w_id, count, parsed_rbs)
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
    # 復元テーブルは共通なので、1回引けば全部進む
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 テーブル進行 (全武器 -1)", use_container_width=True, type="primary"):
            if advance_all_trackers():
                st.toast("一斉に進行しました！")
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sort trackers by weapon, then remaining count
    # Merge to get weapon names easily, but we can just map it
    tracker_df['weapon_label'] = tracker_df['weapon_id'].map(lambda wid: weapon_options.get(wid, "不明な武器"))
    tracker_df = tracker_df.sort_values(by=["weapon_label", "remaining_count"])
    
    current_weapon = None
    for index, row in tracker_df.iterrows():
        if row['weapon_label'] != current_weapon:
            current_weapon = row['weapon_label']
            st.markdown(f"#### 🗡️ {current_weapon}")
            
        with st.container(border=True):
            tc1, tc2, tc3 = st.columns([1, 4, 1], vertical_alignment="center")
            with tc1:
                col_c = "red" if row['remaining_count'] == 0 else ("orange" if row['remaining_count'] < 5 else "green")
                st.markdown(f"<h3 style='color:{col_c}; text-align:center; margin:0;'>あと <b>{row['remaining_count']}</b></h3>", unsafe_allow_html=True)
            with tc2:
                target_rbs = []
                for i in range(1, 6):
                    rt = row.get(f'target_rest_{i}_type', 'なし')
                    rl = row.get(f'target_rest_{i}_level', 'なし')
                    if rt != 'なし':
                        target_rbs.append(f"{rt}[{rl}]")
                st.markdown(f"✨ {' | '.join(target_rbs) if target_rbs else '未付与'}")
            with tc3:
                if st.button("削除", key=f"del_track_{row['id']}"):
                    delete_tracker(row['id'])
                    st.rerun()
