import streamlit as st
import pandas as pd
from src.logic.equipment import get_active_upgrades, register_upgrade, filter_upgrades
from src.logic.equipment_box import load_equipment
from src.logic.master import get_master_data
from src.components.tables import render_active_upgrades
from src.components.sidebar import render_shared_sidebar
from src.components.auth import get_current_user_id
from src.logic.history import undo_last_action, redo_last_action
from src.logic.favorites import add_favorite, remove_favorite, get_favorite_list, is_favorite, prepare_skill_choices
from src.components.pickers import render_skill_picker

st.set_page_config(page_title="スキル抽選結果", page_icon="⚔️", layout="wide")

# Render shared sidebar (boots from cookie instantly)
render_shared_sidebar()

st.title("スキル抽選結果 🏹")
st.markdown("巨戟強化の抽選順序を確認し、スキルを武器に割り当てます。")
 
user_id = get_current_user_id()

@st.fragment
def render_registration_form(master, user_id):
    with st.expander("🆕 未登録の強化抽選結果を追加する", expanded=False):
        series_skills_master = master.get("series_skills", [])
        group_skills_master = master.get("group_skills", [])
        
        # Favorites for sorting
        fav_series = get_favorite_list("series")
        fav_groups = get_favorite_list("group")
        
        sorted_series, series_skill_labels = prepare_skill_choices(series_skills_master, fav_series, "skill_parts")
        sorted_groups, group_skill_labels = prepare_skill_choices(group_skills_master, fav_groups, "group_name")

        c1, c2 = st.columns(2)
        with c1: w_type = st.selectbox("武器種", master.get("weapon_types", []), key="lottery_reg_wt")
        with c2: element = st.selectbox("属性", master.get("elements", []), key="lottery_reg_elem")
            
        st.markdown("##### 抽選スキル (横並び表示)")
        c_lot_s, c_lot_g = st.columns(2)
        with c_lot_s: series_skill = render_skill_picker("シリーズスキル", master.get("series_skills", []), "series", "lot_reg_s")
        with c_lot_g: group_skill = render_skill_picker("グループスキル", master.get("group_skills", []), "group", "lot_reg_g")
        
        count = st.number_input("残り回数 (到達まで)", min_value=1, value=1, step=1, key="lot_reg_count")
        
        if st.button("登録の確定", type="primary", use_container_width=True):
            if not series_skill.strip() or not group_skill.strip():
                st.error("スキルを正しく選択してください。")
            else:
                record_id = register_upgrade(w_type, element, series_skill, group_skill, count, user_id=user_id)
                if record_id:
                    st.toast("抽選結果を登録しました！", icon="✅")
                    st.rerun()
                else:
                    st.error("登録に失敗しました。")

master = get_master_data()
render_registration_form(master, user_id)

st.divider()

@st.fragment
def render_tracker_list(master, user_id):
    # --- Search & Filter UI ---
    st.subheader("検索とフィルタ 🔍")
    series_skills_master = master.get("series_skills", [])
    group_skills_master = master.get("group_skills", [])

    with st.expander("🔎 表示内容を絞り込む", expanded=False):
        fl_c1, fl_c2, fl_c3 = st.columns(3)
        with fl_c1:
            f_types = st.multiselect("武器種", master.get("weapon_types", []))
        with fl_c2:
            f_elements = st.multiselect("属性", master.get("elements", []))
        with fl_c3:
            f_sort = st.selectbox("並び替え", ["残り回数順", "武器種順", "属性順"])

        fs_c1, fs_c2 = st.columns(2)
        with fs_c1:
            f_series = st.multiselect("シリーズスキル", [s['skill_parts'] for s in series_skills_master if s['skill_parts'] != "なし"])
        with fs_c2:
            f_groups = st.multiselect("グループスキル", [g['group_name'] for g in group_skills_master if g['group_name'] != "なし"])

    # --- Dashboard Actions ---
    h_col1, h_col2, h_col3 = st.columns([1, 1, 6], vertical_alignment="center")
    with h_col1:
        undo_disabled = not st.session_state.get('undo_stack', [])
        if st.button("Undo ↩️", disabled=undo_disabled, use_container_width=True):
            undo_last_action()
            st.rerun()
    with h_col2:
        redo_disabled = not st.session_state.get('redo_stack', [])
        if st.button("Redo ↪️", disabled=redo_disabled, use_container_width=True):
            redo_last_action()
            st.rerun()

    # --- Main Dashboard List ---
    df_raw = get_active_upgrades(user_id=user_id)
    df = filter_upgrades(
        df_raw,
        weapon_types=f_types,
        elements=f_elements,
        series_skills=f_series,
        group_skills=f_groups,
        sort_by=f_sort
    )
    eq_df_all = load_equipment(user_id)
    render_active_upgrades(df, user_id, eq_df_all)

render_tracker_list(master, user_id)
