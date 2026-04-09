import streamlit as st
from src.logic.equipment import execute_upgrade, execute_all_upgrades, delete_upgrade, update_upgrade
from src.components.cards import render_slim_card, get_badge_html, inject_card_css, CARD_ACTION_RATIO

@st.dialog("強化抽選結果を編集")
def edit_upgrade_dialog(row, user_id):
    from src.logic.master import get_master_data
    from src.logic.favorites import get_favorite_list, prepare_skill_choices
    master = get_master_data()
    
    st.markdown(f"**{row['weapon_type']} ({row['element']})** の抽選内容を編集")
    
    new_count = st.number_input("残り回数", min_value=1, value=int(row['remaining_count']))
    
    # Favorites for sorting
    fav_s = get_favorite_list("series")
    fav_g = get_favorite_list("group")
    sorted_s, labels_s = prepare_skill_choices(master.get("series_skills", []), fav_s, "skill_parts")
    sorted_g, labels_g = prepare_skill_choices(master.get("group_skills", []), fav_g, "group_name")
    
    curr_s_idx = next((i for i, s in enumerate(sorted_s) if s['skill_parts'] == row['series_skill']), 0)
    curr_g_idx = next((i for i, g in enumerate(sorted_g) if g['group_name'] == row['group_skill']), 0)
    
    sel_s = st.selectbox("シリーズスキル", range(len(labels_s)), index=curr_s_idx, format_func=lambda i: labels_s[i], key="upg_edit_s")
    sel_g = st.selectbox("グループスキル", range(len(labels_g)), index=curr_g_idx, format_func=lambda i: labels_g[i], key="upg_edit_g")
    
    if st.button("保存", type="primary", use_container_width=True):
        if update_upgrade(row['id'], row['weapon_type'], row['element'], 
                          sorted_s[sel_s]['skill_parts'], sorted_g[sel_g]['group_name'], new_count, user_id=user_id):
            st.toast("更新しました")
            st.rerun()
        else: st.error("更新に失敗しました")

def render_active_upgrades(df, user_id, eq_df_all):
    if df.empty:
        st.info("登録されている強化抽選結果はありません。'Register' から追加してください。")
        return

    from src.logic.master import get_master_data
    from src.logic.equipment_box import ATTRIBUTE_COLORS, update_equipment_skills
    
    inject_card_css()
    master = get_master_data()
    series_map = {s['skill_parts']: s['skill_name'] for s in master.get("series_skills", [])}
    group_map = {g['group_name']: g['skill_name'] for g in master.get("group_skills", [])}

    with st.container():
        for _, row in df.iterrows():
            rem = row['remaining_count']
            col_c = "#ff4b4b" if rem <= 1 else ("#f39c12" if rem < 5 else "#27ae60")
            
            # Badge
            elem = row['element']
            bg = ATTRIBUTE_COLORS.get(elem, "#444")
            txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
            badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
            
            # Build Content
            title_text = f"{row['weapon_type']}"
            
            skill_part = row['series_skill']
            skill_name = series_map.get(skill_part, "")
            display_ser = f"{skill_part} ({skill_name})" if skill_name and skill_part != "なし" else skill_part
            
            group_part = row['group_skill']
            group_name = group_map.get(group_part, "")
            display_grp = f"{group_part} ({group_name})" if group_name and group_part != "なし" else group_part
            
            sub_text = f"🛡️ {display_ser} | 👥 {display_grp}"
            bonus_html = f"✨ 残り {rem} 回 || "
            
            col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
            with col_card:
                render_slim_card(badge_html, title_text, sub_text, bonus_html, subtitle=row['weapon_type'], mode="hud")
                
            with col_act:
                with st.popover("⋮", help="操作メニュー", use_container_width=True):
                    # 1. Execute Action
                    with st.popover("🔨 武器へ付与", use_container_width=True):
                        st.markdown("##### 武器を選択")
                        matching_df = eq_df_all[ (eq_df_all['weapon_type'] == row['weapon_type']) & (eq_df_all['element'] == row['element']) ]
                        
                        if matching_df.empty:
                            st.info("対象の武器が装備BOXにありません。")
                        else:
                            for _, w in matching_df.iterrows():
                                # Simple Mini-Card within Popover
                                with st.container(border=True):
                                    mc_c1, mc_c2 = st.columns([4, 1], vertical_alignment="center")
                                    w_display = f"**{w['weapon_name']}**" if not w['weapon_name'].startswith("無銘") else f"**{w['weapon_type']}**"
                                    mc_c1.markdown(f"{w_display}<br><small>現在: {w['current_series_skill']} / {w['current_group_skill']}</small>", unsafe_allow_html=True)
                                    if mc_c2.button("🔨", key=f"assign_{row['id']}_{w['id']}", help="付与して進行"):
                                        execute_upgrade(row['id'], rem, weapon_id=w['id'], user_id=user_id)
                                        st.rerun()
    
                        st.divider()
                        if st.button("割り当てずに進行 (-1回)", key=f"skip_{row['id']}", use_container_width=True):
                            execute_all_upgrades(rem, user_id=user_id)
                            st.rerun()
                    
                    # 2. Edit Action
                    if st.button("✏️ 編集", key=f"ed_upg_{row['id']}", use_container_width=True):
                        edit_upgrade_dialog(row, user_id)
                    
                    st.divider()
                    # 3. Delete Action
                    if st.button("🗑️ 削除", key=f"del_upg_{row['id']}", type="primary", use_container_width=True):
                        if delete_upgrade(row['id'], user_id=user_id):
                            st.toast("削除しました")
                            st.rerun()
