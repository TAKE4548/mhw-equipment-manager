import streamlit as st
import pandas as pd
from src.logic.restoration_tracker import (
    load_trackers, delete_tracker, execute_apply_and_advance
)
from src.components.common import render_item_count
from src.components.cards import render_weapon_card, CARD_ACTION_RATIO
from src.logic.equipment_box import format_bonus_summary, format_bonus_list
from src.components.reinforcement.atoms import (
    render_weapon_attribute_badge, build_visual_comparison_bar, 
    get_restoration_labels
)
from src.components.reinforcement.dialogs import edit_tracker_dialog

@st.fragment
def render_active_tracker_list(master, eq_df, user_id):
    """トラッキング中の抽選結果一覧を表示・管理する」"""
    from src.components.cards import inject_card_css
    inject_card_css()
    
    tracker_df = load_trackers(user_id)
    if tracker_df.empty:
        st.info("トラッキング中の強化抽選結果はありません。")
        return

    # --- Toolbar for Tracker List ---
    with st.expander("🔎 トラッキングを絞り込む・並べ替え", expanded=False):
        t_c1, t_c2, t_c3 = st.columns(3)
        with t_c1:
            t_f_types = st.multiselect("武器種で絞り込み", master.get("weapon_types", []), key="t_filter_type")
        with t_c2:
            t_f_elems = st.multiselect("属性で絞り込み", master.get("elements", []), key="t_filter_elem")
        with t_c3:
            sort_opts = ["残り回数(少)", "残り回数(多)", "武器種順", "属性順", "新着順"]
            t_f_sort = st.selectbox("並び替え", sort_opts, index=0, key="t_sort_by")

        st.markdown("**ボーナス絞り込み**")
        t_f_rbs_opts = []
        for rt, lvs in master.get("restoration_bonuses", {}).items():
            if rt == "なし": continue
            for lv in lvs: t_f_rbs_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
        t_f_rbs = st.multiselect("目標復元ボーナス (AND検索)", t_f_rbs_opts, key="t_filter_rbs")

    # Apply Filtering
    merged_df = tracker_df.merge(eq_df, left_on='weapon_id', right_on='id', suffixes=('', '_eq'))
    if t_f_types: merged_df = merged_df[merged_df['weapon_type'].isin(t_f_types)]
    if t_f_elems: merged_df = merged_df[merged_df['element'].isin(t_f_elems)]

    if t_f_rbs:
        target_set = set()
        for s in t_f_rbs:
            if " [" in s:
                parts = s.split(" [")
                target_set.add((parts[0], parts[1][:-1]))
            else: target_set.add((s, "無印"))

        def check_tracker_rbs(row):
            tr_bonuses = set()
            for i in range(1, 6):
                if row[f'target_rest_{i}_type'] != "なし":
                    tr_bonuses.add((row[f'target_rest_{i}_type'], row[f'target_rest_{i}_level']))
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

    # --- Render Table ---
    render_item_count(len(merged_df))
    
    with st.container():
        st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
        for index, row in merged_df.iterrows():
            curr_labels = get_restoration_labels(row)
            target_labels = get_restoration_labels(row, prefix="target_")
            comp_html = build_visual_comparison_bar(curr_labels, target_labels)
        
            rem = row['remaining_count']
            # Structured data for reinforcement mode
            skills = [
                row['current_series_skill'] if row['current_series_skill'] != "なし" else "なし",
                row['current_group_skill'] if row['current_group_skill'] != "なし" else "なし"
            ]
            
            pbs = [row.get(f'p_bonus_{i}', 'なし') for i in range(1, 4)]
            # Move enhancement_type to dedicated parameter, remove from bonuses cluster
            enhancement_type = row['enhancement_type']
            bonuses = [f"🛠️ {format_bonus_summary(pbs)}"]
            
            # Weapon Display Name logic
            w_display = row['weapon_name'] if row['weapon_name'] and not str(row['weapon_name']).startswith("無銘の") else row['weapon_type']
            
            col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
            with col_card:
                render_weapon_card(
                    weapon_type=row['weapon_type'],
                    weapon_name=w_display,
                    element=row['element'],
                    element_val=f"{row['element']}属性",
                    enhancement_type=enhancement_type,
                    skills=skills,
                    bonuses=bonuses,
                    comparison=comp_html,
                    remaining_count=rem,
                    mode="reinforcement"
                )
            with col_act:
                with st.popover("⋮", use_container_width=True, key=f"pop_{row['id']}"):
                    if st.button("🔨 進行/適用", key=f"ap_{row['id']}", use_container_width=True):
                        if execute_apply_and_advance(row['id'], user_id=user_id): st.rerun()
                    if st.button("✏️ 編集", key=f"ed_tr_{row['id']}", use_container_width=True):
                        edit_tracker_dialog(row, row, user_id)
                    st.divider()
                    if st.button("🗑️ 削除", key=f"dl_{row['id']}", type="primary", use_container_width=True):
                        if delete_tracker(row['id'], user_id=user_id): st.rerun()
