import streamlit as st
from src.logic.equipment import execute_upgrade

def render_active_upgrades(df):
    if df.empty:
        st.info("No active upgrades. Go to 'Register' to add some.")
        return

    # Header Row
    cols_ratio = [2, 1, 3, 2, 2, 2]
    h1, h2, h3, h4, h5, _ = st.columns(cols_ratio)
    h1.write("**武器種**")
    h2.write("**属性**")
    h3.write("**シリーズスキル**")
    h4.write("**グループスキル**")
    h5.write("**残り回数**")
    st.divider()
    
    from src.logic.master import get_master_data
    master = get_master_data()
    series_map = {s['skill_parts']: s['skill_name'] for s in master.get("series_skills", [])}
    group_map = {g['group_name']: g['skill_name'] for g in master.get("group_skills", [])}
    
    from src.logic.equipment import execute_all_upgrades
    for _, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns(cols_ratio, vertical_alignment="center")
        c1.write(f"{row['weapon_type']}")
        c2.write(f"{row['element']}")
        
        # Display series skill part and its effect name
        skill_part = row['series_skill']
        skill_name = series_map.get(skill_part, "")
        display_series = f"{skill_part} ({skill_name})" if skill_name and skill_part != "なし" else skill_part
        c3.write(display_series)
        
        # Display group skill and its effect name
        group_part = row['group_skill']
        group_name = group_map.get(group_part, "")
        display_group = f"{group_part} ({group_name})" if group_name and group_part != "なし" else group_part
        c4.write(display_group)
        
        c5.write(f"**{row['remaining_count']}**")
        with c6:
            # st.popover to select a weapon to assign the skill to
            with st.popover("Execute", use_container_width=True):
                st.markdown("**武器への割り当て (任意)**")
                
                # Fetch matching equipment from Equipment Box
                from src.logic.equipment_box import load_equipment, update_equipment_skills
                eq_df = load_equipment()
                matching_weapons = []
                if not eq_df.empty:
                    matching_df = eq_df[ (eq_df['weapon_type'] == row['weapon_type']) & (eq_df['element'] == row['element']) ]
                    matching_weapons = matching_df.to_dict('records')
                
                options = [{"id": None, "label": "割り当てない (スキップ)"}]
                for w in matching_weapons:
                    options.append({"id": w['id'], "label": f"{w['weapon_name']} (現在: {w['current_series_skill']}/{w['current_group_skill']})"})
                
                selected_opt = st.selectbox(
                    "対象の武器", 
                    options, 
                    format_func=lambda x: x["label"],
                    key=f"sel_weap_{row['id']}"
                )
                
                if st.button("確定して進行 (-1)", key=f"exec_{row['id']}", type="primary", use_container_width=True):
                    # Save the state of all records for Undo
                    previous_states = df[['id', 'remaining_count']].to_dict('records')
                    st.session_state['undo_stack'].append({
                        'action_type': 'EXECUTE_ALL',
                        'decrement': row['remaining_count'],
                        'previous_states': previous_states
                    })
                    st.session_state['redo_stack'].clear()
                    
                    execute_all_upgrades(row['remaining_count'])
                    
                    if selected_opt["id"] is not None:
                        update_equipment_skills(selected_opt["id"], skill_part, group_part)
                        st.toast(f"スキルを武器に割り当てました！")
                    
                    st.rerun()
