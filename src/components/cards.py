import streamlit as st

# v14 Unified Layout Ratios
# Use these constants across all list pages to ensure menu vertical alignment
# Standard List: [CardArea, ActionArea]
CARD_ACTION_RATIO = [11.5, 1.0]

def get_badge_html(text, bgcolor="#444", color="white"):
    """Returns a simple HTML badge for element types."""
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 0px 5px; border-radius: 3px; font-size: 0.7rem; font-weight: bold; display: inline-block; min-width: 32px; text-align: center; margin-right: 8px;">{text}</span>'

def inject_card_css():
    """Injects high-precision CSS for v14 (Context-Aware HUD & Unified Alignment)."""
    st.markdown("""
        <style>
        /* v14: CONTEXT-AWARE SMART HUD (Weapons & Talismans) */

        /* 0. List Container Setup */
        div[data-testid="stVerticalBlock"]:has(.v12-marker) {
            gap: 2px !important;
        }
        
        [data-testid="stHorizontalBlock"]:has(.v12-marker) {
            align-items: center !important;
            margin-bottom: 2px !important;
            gap: 12px !important;
        }

        /* 1. The Card - 40px High Tag */
        .v12-tag-card {
            display: flex;
            align-items: center;
            padding: 0 16px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 6px;
            height: 40px !important;
            box-sizing: border-box !important;
            width: 100%;
            overflow: hidden;
        }

        /* 2. Unified Button Height & Style */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stButton"] button {
            height: 40px !important;
            border-radius: 6px !important;
            border: 1px solid #333 !important;
            background: #252525 !important;
            color: #ccc !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Selection */
        .v12-tag-card.v12-selected { border: 1px solid #f1c40f !important; background: #222 !important; }
        [data-testid="stHorizontalBlock"]:has(.v12-unit-selected) button { background: #f1c40f !important; border: 1px solid #f1c40f !important; color: #000 !important; }

        /* HUD STREAMS & ALIGNMENT */
        .v12-stream { display: flex; align-items: center; width: 100%; white-space: nowrap; overflow: hidden; }
        
        /* Column 1: Identity (Weapon Name / Badge) */
        .v12-col-id { display: flex; align-items: center; flex-shrink: 0; overflow: hidden; }
        .v14-mode-hud .v12-col-id { width: 180px; } /* Weapon fixed width name */
        .v14-mode-long .v12-col-id { width: auto; max-width: 60px; margin-right: 12px; } /* Talisman badge-only id */

        .v12-main-label { font-weight: 600; font-size: 0.9rem; color: #eee; overflow: hidden; text-overflow: ellipsis; }

        /* Column 2: Spec (HUD Icons or Long Text) */
        .v12-col-spec { display: flex; align-items: center; overflow: hidden; gap: 10px; margin-right: 10px; }
        .v14-mode-hud .v12-col-spec { min-width: 320px; flex-shrink: 0; } /* Aligned HUD Icons */
        .v14-mode-long .v12-col-spec { flex: 1; min-width: 0; } /* Expand skill text to all space */

        .v12-sub-label { font-size: 0.65rem; color: #666; text-transform: uppercase; min-width: 60px; }
        .v12-skill-label { font-size: 0.72rem; color: #555; overflow: hidden; text-overflow: ellipsis; }
        .v14-mode-long .v12-skill-label { font-size: 0.85rem; color: #888; } /* Larger skill text for Talismans */

        .v11-sep { color: #333; margin: 0 10px; font-weight: 300; flex-shrink: 0; }
        .v12-bonus-area { font-size: 0.76rem; color: #888; flex: 1; overflow: hidden; text-overflow: ellipsis; }

        /* 3. Collapse Streamlit's internal wrapper padding around markdown cards
              so card column height == button column height == 40px exactly */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) [data-testid="stMarkdownContainer"] {
            line-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        /* Also flatten the column elements themselves */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        /* Popover button height sync */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stPopover"] button,
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stPopover"] {
            height: 40px !important;
            min-height: 40px !important;
        }

        @media (max-width: 900px) { .v12-col-spec { display: none; } }
        </style>
    """, unsafe_allow_html=True)

def _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode):
    """v14: Smart HUD Layout (Supports 'hud' and 'long-text' modes)."""
    selected_cls = "v12-selected" if is_selected else ""
    mode_cls = "v14-mode-hud" if mode == "hud" else "v14-mode-long"
    
    html = f'<div class="v12-tag-card {selected_cls} {mode_cls}"><div class="v12-stream">'
    
    # Mode-dependent identity (Weapon vs Talisman)
    if mode == "hud":
        html += f'<div class="v12-col-id">{badge_html}<div class="v12-main-label">{title_text}</div></div>'
        html += f'<div class="v12-col-spec"><div class="v12-sub-label">{subtitle or ""}</div><div class="v12-skill-label">{sub_text}</div></div>'
    else:
        # Long text mode for talismans - prioritizing skill list
        html += f'<div class="v12-col-id">{badge_html}</div>'
        html += f'<div class="v12-col-spec"><div class="v12-skill-label" style="color:#aaa;">{title_text}</div></div>'
        # sub_text (slots) moved to bonus area for better balance in Talismans
        bonus_html = f"{sub_text} {bonus_html}"
        
    html += f'<span class="v11-sep">|</span><div class="v12-bonus-area">{bonus_html}</div></div></div>'
    return html

def render_slim_card(badge_html, title_text, sub_text, bonus_html, subtitle=None, is_selected=False, mode="hud"):
    """Displays the v14 context-aware tag without button."""
    html = _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode)
    st.markdown(html, unsafe_allow_html=True)

def render_selectable_card(badge_html, title_text, sub_text, bonus_html, key, subtitle=None, is_selected=False, mode="hud"):
    """v14: Context-aware selection tag."""
    selected_cls = "v12-unit-selected" if is_selected else ""
    icon = "✔" if is_selected else "❯"
    
    with st.container():
        st.markdown(f'<div class="v12-marker {selected_cls}" style="display:none"></div>', unsafe_allow_html=True)
        # Always use the unified ratio defined in v14
        c_tag, c_btn = st.columns(CARD_ACTION_RATIO, gap="small")
        
        with c_tag:
            html = _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode)
            st.markdown(html, unsafe_allow_html=True)
            
        with c_btn:
            clicked = st.button(icon, key=key, use_container_width=True)
            
        return clicked
