import streamlit as st
import pandas as pd
from src.logic.equipment import get_active_upgrades, register_upgrade, filter_upgrades
from src.logic.master import get_master_data
from src.components.tables import render_active_upgrades
from src.components.sidebar import render_shared_sidebar
from src.logic.history import undo_last_action, redo_last_action
from src.logic.favorites import add_favorite, remove_favorite, get_favorite_list, is_favorite, prepare_skill_choices

st.set_page_config(page_title="スキル抽選結果", page_icon="⚔️", layout="wide")

# Render shared sidebar (boots from cookie instantly)
render_shared_sidebar()

st.title("スキル抽選結果 🏹")
st.markdown("巨戟強化の抽選順序を確認し、スキルを武器に割り当てます。")

# --- Registration Form (Merged from 1_register) ---
master = get_master_data()
with st.expander("🆕 未登録の強化抽選結果を追加する", expanded=False):
    series_skills_master = master.get("series_skills", [])
    group_skills_master = master.get("group_skills", [])
    
    # Favorites for sorting
    fav_series = get_favorite_list("series")
    fav_groups = get_favorite_list("group")
    
    sorted_series, series_skill_labels = prepare_skill_choices(series_skills_master, fav_series, "skill_parts")
    sorted_groups, group_skill_labels = prepare_skill_choices(group_skills_master, fav_groups, "group_name")

    with st.form("register_form_dash", border=False):
        c1, c2 = st.columns(2)
        with c1:
            w_type = st.selectbox("武器種", master.get("weapon_types", []))
        with c2:
            element = st.selectbox("属性", master.get("elements", []))
            
        sc1, sc2 = st.columns(2)
        with sc1:
            selected_series_idx = st.selectbox("シリーズスキル", range(len(series_skill_labels)), format_func=lambda i: series_skill_labels[i])
            series_skill = sorted_series[selected_series_idx]["skill_parts"]
        with sc2:
            selected_group_idx = st.selectbox("グループスキル", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
            group_skill = sorted_groups[selected_group_idx]["group_name"]
            
        # Favorite Toggles (outside form because buttons in forms are tricky)
        # But wait, user wants it "when selecting". Let's provide separate toggle buttons below the selects.
        # Actually, Streamlit forms don't support st.toggle inside for state management easily. 
        # I'll add "⭐ お気に入り" buttons BESIDE the type/element selects but outside the form?
        # No, let's keep it simple: Add a separate expander for "お気に入り管理" or just handle it in the list.
        # Actually, let's just make the sort logic work for now and add toggle buttons outside.
            
        count = st.number_input("残り回数 (到達まで)", min_value=1, value=1, step=1)
        
        if st.form_submit_button("登録の確定", type="primary"):
            if not series_skill.strip() or not group_skill.strip():
                st.error("スキルを正しく選択してください。")
            else:
                record_id = register_upgrade(w_type, element, series_skill, group_skill, count)
                if record_id:
                    st.session_state['undo_stack'].append({'action_type': 'REGISTER', 'target_id': record_id})
                    st.session_state['redo_stack'].clear()
                    st.toast("抽選結果を登録しました！", icon="✅")
                    st.rerun()

    st.markdown("---")
    st.markdown("##### ⭐ スキルのお気に入り設定")
    fav_c1, fav_c2 = st.columns(2)
    with fav_c1:
        cur_s = st.selectbox("シリーズスキルを選択", [s['skill_parts'] for s in series_skills_master if s['skill_parts'] != "なし"], key="fav_s_sel")
        if is_favorite("series", cur_s):
            if st.button(f"🌟 {cur_s} をお気に入りから外す", key="rem_s"):
                remove_favorite("series", cur_s)
                st.rerun()
        else:
            if st.button(f"☆ {cur_s} をお気に入りに追加", key="add_s"):
                add_favorite("series", cur_s)
                st.rerun()
    with fav_c2:
        cur_g = st.selectbox("グループスキルを選択", [g['group_name'] for g in group_skills_master if g['group_name'] != "なし"], key="fav_g_sel")
        if is_favorite("group", cur_g):
            if st.button(f"🌟 {cur_g} をお気に入りから外す", key="rem_g"):
                remove_favorite("group", cur_g)
                st.rerun()
        else:
            if st.button(f"☆ {cur_g} をお気に入りに追加", key="add_g"):
                add_favorite("group", cur_g)
                st.rerun()

st.divider()

# --- Search & Filter UI ---
st.subheader("検索とフィルタ 🔍")
with st.expander("🔎 条件を指定して表示を絞り込む", expanded=False):
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
with h_col2:
    redo_disabled = not st.session_state.get('redo_stack', [])
    if st.button("Redo ↪️", disabled=redo_disabled, use_container_width=True):
        redo_last_action()

# --- Main Dashboard List ---
df_raw = get_active_upgrades()
df = filter_upgrades(
    df_raw,
    weapon_types=f_types,
    elements=f_elements,
    series_skills=f_series,
    group_skills=f_groups,
    sort_by=f_sort
)
render_active_upgrades(df)
