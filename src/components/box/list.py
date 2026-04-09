import streamlit as st
import pandas as pd
from src.logic.equipment_box import (
    load_equipment, delete_equipment,
    format_bonus_summary, filter_equipment
)
from src.components.common import render_item_count
from src.components.cards import render_slim_card, CARD_ACTION_RATIO
from src.components.box.atoms import render_weapon_badge
from src.components.box.dialogs import edit_equipment_dialog

@st.fragment
def render_equipment_list(master, user_id):
    """登録済みの武器一覧を表示・管理する (Fragment化)"""
    enhancement_opts = master.get("kyogeki_enhancements", [])
    p_bonus_opts = master.get("production_bonuses", [])

    with st.expander("🔎 条件を指定して絞り込む・並べ替え", expanded=False):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            f_name = st.text_input("武器名検索", placeholder="キーワード...", key="f_w_name_list")
            f_types = st.multiselect("武器種", master.get("weapon_types", []), key="f_w_types_list")
        with f_c2:
            f_elements = st.multiselect("属性", master.get("elements", []), key="f_w_elems_list")
            f_enhancements = st.multiselect("巨戟強化", enhancement_opts, key="f_w_enhs_list")
        with f_c3:
            f_sort = st.selectbox("並び替え", ["武器種順", "属性順", "新着順"], index=0, key="f_w_sort_list")

        sf_c1, sf_c2 = st.columns(2)
        with sf_c1:
            f_series = st.multiselect("シリーズスキル", [s['skill_parts'] for s in master.get("series_skills", []) if s['skill_parts'] != "なし"], key="f_w_ser_list")
        with sf_c2:
            f_groups = st.multiselect("グループスキル", [g['group_name'] for g in master.get("group_skills", []) if g['group_name'] != "なし"], key="f_w_grp_list")

        st.markdown("**ボーナス絞り込み**")
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            f_pbs = st.multiselect("生産ボーナス", p_bonus_opts, key="f_w_pbs_list")
        with b_c2:
            f_rbs_opts = []
            for rt, lvs in master.get("restoration_bonuses", {}).items():
                if rt == "なし": continue
                for lv in lvs: f_rbs_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            f_rbs = st.multiselect("復元ボーナス", f_rbs_opts, key="f_w_rbs_list")

    df_raw = load_equipment(user_id)
    df = filter_equipment(df_raw, search_name=f_name, weapon_types=f_types, elements=f_elements, series_skills=f_series, group_skills=f_groups, enhancements=f_enhancements, production_bonuses=f_pbs, restoration_bonuses=f_rbs, sort_by=f_sort)

    render_item_count(len(df))

    if df.empty:
        st.info("条件に一致する武器がありません。")
    else:
        with st.container():
            for index, row in df.iterrows():
                badge_html = render_weapon_badge(row['element'])
                w_display = row['weapon_name'] if row['weapon_name'] and not str(row['weapon_name']).startswith("無銘の") else row['weapon_type']
                
                # Bonus Formatting
                pbs = [row.get(f'p_bonus_{i}', 'なし') for i in range(1,4)]
                prod_bonus_text = f"🛠️ {format_bonus_summary(pbs)}"
                
                # Restoration Bonuses
                rbs_with_lv = []
                for i in range(1, 6):
                    rt, rl = row.get(f'rest_{i}_type', 'なし'), row.get(f'rest_{i}_level', 'なし')
                    if rt != 'なし': rbs_with_lv.append(f"{rt}{rl if rl and rl != '無印' else ''}")
                rest_bonus_text = f"✨ {format_bonus_summary(rbs_with_lv)}"
                
                # Combined strings for v15 parser
                bonus_html = f"{prod_bonus_text} || {rest_bonus_text}"
                sub_text = f"📋 {row['enhancement_type']} | 🛡️ {row['current_series_skill']} | 👥 {row['current_group_skill']}"
                
                col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
                with col_card:
                    render_slim_card(badge_html, w_display, sub_text, bonus_html, subtitle=row['weapon_type'], mode="hud")
                    
                with col_act:
                    with st.popover("⋮", help="操作メニュー", use_container_width=True, key=f"pop_w_{row['id']}"):
                        if st.button("✏️ 編集", key=f"edit_{row['id']}", use_container_width=True):
                            edit_equipment_dialog(row, user_id)
                        if st.button("🎯 強化厳選へ", key=f"tr_{row['id']}", use_container_width=True):
                            st.session_state.tracker_reg_w_id = row['id']
                            st.switch_page("pages/reinforcement_registration.py")
                        st.divider()
                        if st.button("🗑️ 削除", key=f"del_{row['id']}", type="primary", use_container_width=True):
                            if delete_equipment(row['id'], user_id=user_id):
                                st.toast("武器を削除しました。")
                                st.rerun()
