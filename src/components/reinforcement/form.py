import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    format_bonus_summary, format_bonus_list
)
from src.logic.restoration_tracker import register_tracker
from src.components.cards import render_selectable_weapon_card
from src.components.reinforcement.atoms import render_weapon_attribute_badge

@st.fragment
def render_registration_section(master, eq_df, user_id):
    """v14 Visual Selector: 武器選択と抽選結果の登録を行うフォーム"""
    from src.components.cards import inject_card_css
    inject_card_css()
    
    st.markdown("### 1. 武器を選択")
    
    # --- Hierarchical Filters ---
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    cur_df = eq_df.copy()
    
    with f_c1:
        w_types = ["すべて"] + sorted(cur_df['weapon_type'].unique().tolist())
        sel_type = st.selectbox("武器種", w_types, key="h_f_type")
        if sel_type != "すべて": cur_df = cur_df[cur_df['weapon_type'] == sel_type]
        
    with f_c2:
        elems = ["すべて"] + sorted(cur_df['element'].unique().tolist())
        sel_elem = st.selectbox("属性", elems, key="h_f_elem", disabled=len(elems) <= 1)
        if sel_elem != "すべて": cur_df = cur_df[cur_df['element'] == sel_elem]
        
    with f_c3:
        available_skills = set()
        for idx, r in cur_df.iterrows():
            if r['current_series_skill'] != "なし": available_skills.add(r['current_series_skill'])
            if r['current_group_skill'] != "なし": available_skills.add(r['current_group_skill'])
        
        skill_opts = ["すべて"] + sorted(list(available_skills))
        sel_skill = st.selectbox("スキル中心絞り込み", skill_opts, key="h_f_skill", disabled=len(skill_opts) <= 1)
        if sel_skill != "すべて":
            cur_df = cur_df[(cur_df['current_series_skill'] == sel_skill) | (cur_df['current_group_skill'] == sel_skill)]
            
    with f_c4:
        available_bonuses = set()
        for idx, r in cur_df.iterrows():
            for i in range(1, 4):
                if r[f'p_bonus_{i}'] != "なし": available_bonuses.add(r[f'p_bonus_{i}'])
            for i in range(1, 6):
                if r[f'rest_{i}_type'] != "なし": available_bonuses.add(r[f'rest_{i}_type'])
        
        bonus_opts = ["すべて"] + sorted(list(available_bonuses))
        sel_bonus = st.selectbox("ボーナス成分で検索", bonus_opts, key="h_f_bonus", disabled=len(bonus_opts) <= 1)
        if sel_bonus != "すべて":
            def check_bonus_exists(row):
                for i in range(1, 4):
                    if row[f'p_bonus_{i}'] == sel_bonus: return True
                for i in range(1, 6):
                    if row[f'rest_{i}_type'] == sel_bonus: return True
                return False
            cur_df = cur_df[cur_df.apply(check_bonus_exists, axis=1)]

    cur_df = cur_df.sort_values(by=["weapon_type", "element", "weapon_name"])

    # --- Render Selection Grid ---
    if cur_df.empty:
        st.info("条件に一致する武器が見つかりません。")
    else:
        st.markdown(f"**候補: {len(cur_df)} 件**")
        with st.container():
            st.markdown('<div class="v12-dense-list" style="display:none"></div>', unsafe_allow_html=True)
            for idx, w_row in cur_df.iterrows():
                is_selected = (st.session_state.get("tracker_reg_w_id") == w_row['id'])
                # Structured data for Triple-Cluster layout
                skills = [
                    w_row['current_series_skill'] if w_row['current_series_skill'] != "なし" else "なし",
                    w_row['current_group_skill'] if w_row['current_group_skill'] != "なし" else "なし"
                ]
                
                pbs = [w_row.get(f'p_bonus_{i}', 'なし') for i in range(1, 4)]
                rbs_with_lv = []
                for i in range(1, 6):
                    rt, rl = w_row.get(f'rest_{i}_type', 'なし'), w_row.get(f'rest_{i}_level', 'なし')
                    if rt != 'なし': rbs_with_lv.append(f"{rt}{rl if rl and rl != '無印' else ''}")
                
                bonuses = [f"📋 {w_row['enhancement_type']}", f"🛠️ {format_bonus_summary(pbs)}"]
                if rbs_with_lv:
                    bonuses.append(f"✨ {' / '.join(rbs_with_lv)}")
                
                # Weapon Display Name logic
                w_display = w_row['weapon_name'] if w_row['weapon_name'] and not str(w_row['weapon_name']).startswith("無銘の") else w_row['weapon_type']

                if render_selectable_weapon_card(
                    weapon_type=w_row['weapon_type'],
                    weapon_name=w_display,
                    element=w_row['element'],
                    element_val=f"{w_row['element']}属性",
                    skills=skills,
                    bonuses=bonuses,
                    key=f"hsel_{w_row['id']}", 
                    is_selected=is_selected,
                    mode="hud"
                ):
                    st.session_state.tracker_reg_w_id = w_row['id']
                    st.rerun()

    # --- Step 2: Registration Input ---
    if st.session_state.get("tracker_reg_w_id"):
        st.markdown("---")
        st.markdown("### 2. 抽選結果を入力")
        sel_row = eq_df[eq_df['id'] == st.session_state.tracker_reg_w_id].iloc[0]
        st.info(f"選択中: **{sel_row['weapon_name']}** ({sel_row['weapon_type']})")
        
        sel_w_type, sel_element = sel_row['weapon_type'], sel_row['element']
        is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
        is_bowgun = ("ボウガン" in sel_w_type)
        
        dynamic_rest_options = ["なし"]
        for r_type, levels in master.get("restoration_bonuses", {}).items():
            if r_type == "なし": continue
            if r_type == "切れ味強化" and (is_bow or is_bowgun): continue
            if r_type == "装填強化" and not is_bowgun: continue
            if r_type == "属性強化" and (sel_element == "無" or (is_bow and sel_element in ["毒", "麻痺", "睡眠", "爆破"])): continue
            for lv in levels: dynamic_rest_options.append(r_type if lv == "無印" else f"{r_type} [{lv}]")
                
        rc1, rc2, rc3, rc4, rc5 = st.columns(5)
        tb1 = rc1.selectbox("枠1", dynamic_rest_options, key="tb1")
        tb2 = rc2.selectbox("枠2", dynamic_rest_options, key="tb2")
        tb3 = rc3.selectbox("枠3", dynamic_rest_options, key="tb3")
        tb4 = rc4.selectbox("枠4", dynamic_rest_options, key="tb4")
        tb5 = rc5.selectbox("枠5", dynamic_rest_options, key="tb5")
        
        count_val = st.number_input("残り回数 (目標までのスキップ数)", min_value=1, value=1, step=1, key="tr_count")
        
        b_c1, b_c2 = st.columns([7, 3])
        if b_c1.button("トラッキングに追加", type="primary", use_container_width=True):
            parsed_rbs = []
            for rb in [tb1, tb2, tb3, tb4, tb5]:
                if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
                elif " [" in rb:
                    parts = rb.split(" [")
                    parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
                else: parsed_rbs.append({"type": rb, "level": "無印"})
            if register_tracker(st.session_state.tracker_reg_w_id, count_val, parsed_rbs, user_id=user_id):
                st.session_state.tracker_reg_w_id = None
                st.toast("トラッキングに追加しました", icon="📋")
                st.rerun()
            else: st.error("保存に失敗しました")
        
        if b_c2.button("キャンセル", use_container_width=True):
            st.session_state.tracker_reg_w_id = None
            st.rerun()
