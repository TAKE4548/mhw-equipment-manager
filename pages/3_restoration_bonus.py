import streamlit as st
import pandas as pd
from src.logic.equipment_box import load_equipment, execute_bonus_upgrade

def init_session_state():
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

st.set_page_config(page_title="Restoration Bonus", page_icon="✨", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

st.title("Restoration Bonus Tracker ✨")
st.markdown("装備BOXに登録されている武器の、「復元ボーナス」厳選を進める専用画面です。")

st.divider()

df = load_equipment()

if df.empty:
    st.info("装備BOXに武器が登録されていません。")
else:
    active_df = df[df['remaining_count_for_bonus'] > 0].copy()
    active_df = active_df.sort_values(by="remaining_count_for_bonus", ascending=True)

    if active_df.empty:
        st.success("🎉 現在、復元ボーナスを厳選中の武器はありません。（すべて完了、または未登録）")
    else:
        st.subheader("現在厳選中の武器")
        
        # ヘッダー
        st.markdown("<br>", unsafe_allow_html=True)
        h1, h2, h3, h4 = st.columns([3, 2, 2, 2], vertical_alignment="bottom")
        h1.markdown("**武器**")
        h2.markdown("**狙っているボーナス**")
        h3.markdown("**残り回数**")
        h4.markdown("**アクション**")
        st.divider()

        for index, row in active_df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2], vertical_alignment="center")
                with c1:
                    st.markdown(f"**{row['weapon_name']}**<br><small>{row['weapon_type']} | {row['element']}</small>", unsafe_allow_html=True)
                with c2:
                    current_rbs = []
                    for i in range(1, 6):
                        rt = row.get(f'rest_{i}_type', 'なし')
                        rl = row.get(f'rest_{i}_level', 'なし')
                        if rt != 'なし':
                            current_rbs.append(f"{rt}[{rl}]")
                    st.markdown(f"✨ {' | '.join(current_rbs) if current_rbs else '未付与'}")
                with c3:
                    st.metric(label="", value=f"{row['remaining_count_for_bonus']} 回", label_visibility="collapsed")
                with c4:
                    if st.button("復元実行 (-1)", key=f"exec_bonus_{row['id']}", use_container_width=True):
                        if execute_bonus_upgrade(row['id']):
                            st.toast(f"{row['weapon_name']}の復元ボーナスを進めました！")
                            st.rerun()
            st.divider()
