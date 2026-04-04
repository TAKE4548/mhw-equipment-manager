import streamlit as st
from src.logic.equipment import execute_upgrade, execute_all_upgrades, delete_upgrade

def render_active_upgrades(df):
    if df.empty:
        st.info("登録されている強化抽選結果はありません。'Register' から追加してください。")
        return

    from src.logic.master import get_master_data
    from src.logic.equipment_box import ATTRIBUTE_COLORS, load_equipment, update_equipment_skills
    
    master = get_master_data()
    series_map = {s['skill_parts']: s['skill_name'] for s in master.get("series_skills", [])}
    group_map = {g['group_name']: g['skill_name'] for g in master.get("group_skills", [])}

    def get_badge_html(text, bgcolor="#444", color="white"):
        return f'<span style="background-color: {bgcolor}; color: {color}; padding: 1px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold; display: inline-block; min-width: 45px; text-align: center;">{text}</span>'

    for _, row in df.iterrows():
        rem = row['remaining_count']
        with st.container(border=True):
            # Compact table-like row
            cols = st.columns([0.6, 0.6, 1.4, 3.2, 2.0], vertical_alignment="center")
            
            # 1. Remaining Count
            col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
            cols[0].markdown(f"<div style='text-align:center; background:{col_c}22; border-radius:4px; padding:2px;'><small style='color:{col_c};'>あと<b>{rem}</b></small></div>", unsafe_allow_html=True)

            # 2. Attribute Badge
            elem = row['element']
            bg = ATTRIBUTE_COLORS.get(elem, "#444")
            txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
            cols[1].markdown(get_badge_html(elem, bgcolor=bg, color=txt_c), unsafe_allow_html=True)
            
            # 3. Weapon Type
            cols[2].markdown(f"**{row['weapon_type']}**")
            
            # 4. Skills (Stacked)
            skill_part = row['series_skill']
            skill_name = series_map.get(skill_part, "")
            display_ser = f"{skill_part} ({skill_name})" if skill_name and skill_part != "なし" else skill_part
            
            group_part = row['group_skill']
            group_name = group_map.get(group_part, "")
            display_grp = f"{group_part} ({group_name})" if group_name and group_part != "なし" else group_part
            cols[3].markdown(f"<small>🛡️ {display_ser}<br>👥 {display_grp}</small>", unsafe_allow_html=True)
            
            # 5. Actions (Unified Design: Execute Upgrade & Delete)
            ac1, ac2 = cols[4].columns([3, 1])
            with ac1:
                with st.popover("🔨 強化実施", use_container_width=True):
                    st.markdown("##### 武器への割り当て選択")
                    eq_df = load_equipment()
                    matching_df = eq_df[ (eq_df['weapon_type'] == row['weapon_type']) & (eq_df['element'] == row['element']) ]
                    
                    if matching_df.empty:
                        st.info("対象の武器が装備BOXにありません。")
                    else:
                        for _, w in matching_df.iterrows():
                            # Show Mini-Card for weapon identification
                            with st.container(border=True):
                                mc_c1, mc_c2 = st.columns([4, 1], vertical_alignment="center")
                                w_display = f"**{w['weapon_name']}**" if not w['weapon_name'].startswith("無銘") else f"**{w['weapon_type']}**"
                                mc_c1.markdown(f"{w_display}<br><small>現在: {w['current_series_skill']} / {w['current_group_skill']}</small>", unsafe_allow_html=True)
                                if mc_c2.button("🔨", key=f"assign_{row['id']}_{w['id']}", help="この武器に付与して進行"):
                                    # Logic copied from original: 
                                    # 1. Capture state for Undo, 2. Execute all, 3. Apply to weapon
                                    previous_states = df[['id', 'remaining_count']].to_dict('records')
                                    st.session_state['undo_stack'].append({'action_type': 'EXECUTE_ALL', 'decrement': rem, 'previous_states': previous_states})
                                    st.session_state['redo_stack'].clear()
                                    
                                    execute_all_upgrades(rem)
                                    update_equipment_skills(w['id'], skill_part, group_part)
                                    st.toast(f"{w['weapon_name']} にスキルを適用し、テーブルを進行させました。")
                                    st.rerun()

                    st.divider()
                    if st.button("割り当てずに進行 (-1のみ)", key=f"skip_{row['id']}", use_container_width=True):
                        previous_states = df[['id', 'remaining_count']].to_dict('records')
                        st.session_state['undo_stack'].append({'action_type': 'EXECUTE_ALL', 'decrement': rem, 'previous_states': previous_states})
                        st.session_state['redo_stack'].clear()
                        execute_all_upgrades(rem)
                        st.rerun()

            if ac2.button("🗑️", key=f"del_upg_{row['id']}", use_container_width=True):
                if delete_upgrade(row['id']):
                    st.toast("強化目標を削除しました")
                    st.rerun()
