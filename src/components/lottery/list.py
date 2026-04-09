import streamlit as st
from src.logic.equipment import get_active_upgrades, filter_upgrades
from src.logic.equipment_box import load_equipment
from src.components.common import render_item_count
from src.components.tables import render_active_upgrades

@st.fragment
def render_tracker_list(master, user_id):
    """登録済みの抽選結果一覧を表示・管理する (Fragment化)"""
    # --- Search & Filter UI ---
    series_skills_master = master.get("series_skills", [])
    group_skills_master = master.get("group_skills", [])

    with st.expander("🔎 抽選結果を絞り込む・並べ替え", expanded=False):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            f_types = st.multiselect("武器種", master.get("weapon_types", []), key="f_lot_types")
        with f_c2:
            f_elements = st.multiselect("属性", master.get("elements", []), key="f_lot_elems")
        with f_c3:
            f_sort = st.selectbox("並び替え", ["残り回数順", "武器種順", "属性順"], key="f_lot_sort")

        fs_c1, fs_c2 = st.columns(2)
        with fs_c1:
            f_series = st.multiselect("シリーズスキル", [s['skill_parts'] for s in series_skills_master if s['skill_parts'] != "なし"], key="f_lot_ser")
        with fs_c2:
            f_groups = st.multiselect("グループスキル", [g['group_name'] for g in group_skills_master if g['group_name'] != "なし"], key="f_lot_grp")

    # --- Main List Rendering ---
    df_raw = get_active_upgrades(user_id=user_id)
    df = filter_upgrades(
        df_raw,
        weapon_types=f_types,
        elements=f_elements,
        series_skills=f_series,
        group_skills=f_groups,
        sort_by=f_sort
    )
    render_item_count(len(df))
    eq_df_all = load_equipment(user_id)
    
    with st.container():
        st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
        render_active_upgrades(df, user_id, eq_df_all)
