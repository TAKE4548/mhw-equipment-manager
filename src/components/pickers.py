import streamlit as st
from src.logic.favorites import is_favorite, add_favorite, remove_favorite, prepare_skill_choices

# UI Version: 3.0 (Dialog-based Picker for Guaranteed Auto-close)

def render_skill_picker(label, choices, fav_type, key_prefix, current_val=None):
    """
    Renders a skill picker trigger button. Clicking opens a st.dialog.
    - Select -> Auto-close (Rerun)
    - Favorite -> Stay open (Fragment)
    """
    state_key = f"psel_{key_prefix}"
    if state_key not in st.session_state:
        st.session_state[state_key] = current_val if current_val else "なし"
    
    # Sync if external current_val changes
    if current_val and st.session_state[state_key] != current_val:
        st.session_state[state_key] = current_val

    selected_val = st.session_state[state_key]

    # --- The Dialog UI ---
    @st.dialog(f"{label}の選択", width="large")
    def open_picker_dialog():
        st.markdown(f"**{label}** をリストから選択してください。⭐でお気に入りを管理できます。")
        
        # Wrap the searchable list in a fragment to allow independent star management
        @st.fragment
        def dialog_content():
            search_query = st.text_input("スキルを検索...", key=f"dsrc_{key_prefix}", placeholder="入力して絞り込み...")
            val_attr = "skill_parts" if fav_type == "series" else "group_name"
            
            import src.logic.favorites as fav_logic
            fav_choices, _ = prepare_skill_choices(choices, fav_logic.get_favorite_list(fav_type), val_attr)
            
            if search_query:
                filtered = [c for c in fav_choices if search_query.lower() in c.get(val_attr, "").lower() or search_query.lower() in c.get("skill_name", "").lower()]
            else:
                filtered = fav_choices

            st.markdown("---")
            with st.container(height=450):
                if not filtered:
                    st.info("該当するスキルがありません。")
                
                for item in filtered:
                    val = item.get(val_attr)
                    disp_name = item.get("skill_name", "")
                    full_label = f"{val} ({disp_name})" if disp_name and val != "なし" else val
                    is_this_selected = (val == selected_val)
                    
                    c_btn, c_fav = st.columns([8.5, 1.5])
                    
                    # 1. Selection Button -> Closes Dialog on Rerun
                    if c_btn.button(
                        full_label, 
                        key=f"db_{key_prefix}_{val}", 
                        use_container_width=True, 
                        type="primary" if is_this_selected else "secondary"
                    ):
                        st.session_state[state_key] = val
                        # st.rerun() inside a dialog closes it while updating the app state
                        st.rerun() 
                    
                    # 2. Favorite Toggle -> Stays in Dialog
                    is_fav = is_favorite(fav_type, val)
                    if c_fav.button("⭐" if is_fav else "☆", key=f"df_{key_prefix}_{val}"):
                        if is_fav: remove_favorite(fav_type, val)
                        else: add_favorite(fav_type, val)
                        st.rerun(scope="fragment")
        
        dialog_content()
        if st.button("閉じる", use_container_width=True):
            st.rerun()

    # --- The Trigger Button ---
    btn_label = f"{label}: **{selected_val}**"
    if st.button(btn_label, use_container_width=True, key=f"trig_{key_prefix}"):
        open_picker_dialog()
                    
    return selected_val
