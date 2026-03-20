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
    
    from src.logic.equipment import execute_all_upgrades
    for _, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns(cols_ratio, vertical_alignment="center")
        c1.write(f"{row['weapon_type']}")
        c2.write(f"{row['element']}")
        c3.write(f"{row['series_skill']}")
        c4.write(f"{row['group_skill']}")
        c5.write(f"**{row['remaining_count']}**")
        with c6:
            if st.button("Execute", key=f"exec_{row['id']}", type="primary", use_container_width=True):
                # Save the state of all records for Undo
                previous_states = df[['id', 'remaining_count']].to_dict('records')
                st.session_state['undo_stack'].append({
                    'action_type': 'EXECUTE_ALL',
                    'decrement': row['remaining_count'],
                    'previous_states': previous_states
                })
                st.session_state['redo_stack'].clear()
                
                execute_all_upgrades(row['remaining_count'])
                st.rerun()
