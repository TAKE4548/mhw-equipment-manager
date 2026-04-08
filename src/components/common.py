import streamlit as st
from src.logic.history import undo_last_action, redo_last_action, get_history

def render_lean_header(title: str, description: str = None, icon: str = None):
    """
    Renders a compact page header with integrated Undo/Redo toolbar.
    """
    # Vertical spacer for better layout balance (Increased for Polish)
    st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)

    # Use columns to align title and history buttons horizontally
    c1, c2, c3 = st.columns([10, 1, 1], vertical_alignment="center")
    
    with c1:
        # Title with optional icon
        display_title = f"{icon} {title}" if icon else title
        st.markdown(f"### {display_title}", help=description)
        # We use st.caption for description if provided, but it's often better as a tooltip
        if description:
            # Inline description to save vertical space
             st.markdown(f"<p style='font-size:0.8rem; color:#666; margin:-5px 0 10px 0;'>{description}</p>", unsafe_allow_html=True)
             
    u_stack, r_stack = get_history()
    
    with c2:
        if st.button("↩️", key="h_undo", disabled=not u_stack, use_container_width=True, help="Undo (元に戻す)"):
            if undo_last_action():
                st.toast("元に戻しました")
                st.rerun()
                
    with c3:
        if st.button("↪️", key="h_redo", disabled=not r_stack, use_container_width=True, help="Redo (やり直し)"):
            if redo_last_action():
                st.toast("やり直しました")
                st.rerun()
                
    # Add the lean separator (Increased margin for balance)
    st.markdown('<div class="lean-sep" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

def render_item_count(count: int, unit: str = "件"):
    """Displays a standardized item count label, left-aligned."""
    st.markdown(f"<p style='text-align:left; font-size:0.8rem; color:#888; margin: -5px 0 5px 0;'>該当件数: {count} {unit}</p>", unsafe_allow_html=True)
