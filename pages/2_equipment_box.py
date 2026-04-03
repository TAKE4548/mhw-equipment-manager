import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import load_equipment, register_equipment, delete_equipment

def init_session_state():
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

st.set_page_config(page_title="Equipment Box", page_icon="📦", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

st.title("Equipment Box 📦")
st.markdown("ここで所持している巨戟アーティア武器を管理します。")

st.divider()

st.subheader("新しい武器を登録")

master = get_master_data()
series_skills_master = master.get("series_skills", [])
series_skill_labels = [f"{s['skill_parts']} ({s['skill_name']})" if s['skill_parts'] != "なし" else "なし" for s in series_skills_master]

group_skills_master = master.get("group_skills", [])
group_skill_labels = [f"{g['group_name']} ({g['skill_name']})" if g['group_name'] != "なし" else "なし" for g in group_skills_master]

with st.expander("➕ 武器を登録する", expanded=False):
    with st.form("register_weapon_form"):
        weapon_name = st.text_input("武器の識別名 (例: 火竜大剣用)")
        
        col1, col2 = st.columns(2)
        with col1:
            w_type = st.selectbox("Weapon Type", master.get("weapon_types", []))
        with col2:
            element = st.selectbox("Element", master.get("elements", []))

        st.markdown("**現在のスキル状態**")
        col3, col4 = st.columns(2)
        with col3:
            selected_series_idx = st.selectbox("現在のシリーズスキル", range(len(series_skill_labels)), format_func=lambda i: series_skill_labels[i])
            current_series = series_skills_master[selected_series_idx]["skill_parts"]
        with col4:
            selected_group_idx = st.selectbox("現在のグループスキル", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
            current_group = group_skills_master[selected_group_idx]["group_name"]
            
        st.markdown("**復元ボーナス厳選**")
        col5, col6 = st.columns(2)
        with col5:
            target_bonus = st.selectbox("目標の復元ボーナス", master.get("restoration_bonuses", []))
        with col6:
            count = st.number_input("完了までの残り回数", min_value=1, value=1, step=1)
            
        submitted = st.form_submit_button("武器を登録")
        if submitted:
            if not weapon_name.strip():
                st.error("武器の識別名を入力してください。")
            else:
                record_id = register_equipment(
                    weapon_name, w_type, element, target_bonus, 
                    current_series, current_group, target_bonus, count
                )
                if record_id:
                    st.success(f"{weapon_name} を登録しました！")
                    st.rerun()
                else:
                    st.error("登録に失敗しました。")

st.divider()
st.subheader("所持武器一覧")

df = load_equipment()

if df.empty:
    st.info("登録されている武器がありません。")
else:
    # 削除操作用
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 3, 2, 1])
            with col1:
                st.markdown(f"**{row['weapon_name']}**<br><small>{row['weapon_type']} | {row['element']}</small>", unsafe_allow_html=True)
            with col2:
                st.metric("目標ボーナス", row['target_restoration_bonus'], f"残り {row['remaining_count_for_bonus']} 回")
            with col3:
                st.markdown(f"**Skill 1**: {row['current_series_skill']}<br>**Skill 2**: {row['current_group_skill']}", unsafe_allow_html=True)
            with col5:
                if st.button("削除🗑️", key=f"del_{row['id']}"):
                    delete_equipment(row['id'])
                    st.rerun()
        st.divider()
