import streamlit as st
import re
from src.components.icons import Icon

# v14 Unified Layout Ratios
# Use these constants across all list pages to ensure menu vertical alignment
CARD_ACTION_RATIO = [11.5, 1.0]

def get_badge_html(text, bgcolor="#444", color="white"):
    """Returns a simple HTML badge for element types."""
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 0px 5px; border-radius: 3px; font-size: 0.7rem; font-weight: bold; display: inline-block; min-width: 32px; text-align: center; margin-right: 8px;">{text}</span>'

def inject_card_css():
    """Injects high-precision CSS for v15 (Triple-Cluster Layout)."""
    # Performance opt: Icon Base64 data is now centralized in a single CSS block
    icon_styles = Icon.get_style_sheet()
    
    # Inject Icon Styles
    st.markdown(f"<style>{icon_styles}</style>", unsafe_allow_html=True)
    
    # Inject Layout Styles
    st.markdown("""
        <style>
        /* v15: TRIPLE-CLUSTER LAYOUT */
        
        /* 0. Global Lean UI Adjustments */
        [data-testid="stForm"] {
            padding: 1rem !important;
        }

        /* Lean Separator */
        .lean-sep {
            border-top: 1px solid #333;
            margin: 0.5rem 0;
            width: 100%;
        }

        /* 0. List Item Spacing - Target only main card containers (v15 only) */
        .v12-tag-card.v15-mode {
            margin-bottom: 8px;
        }

        /* 1. The Card - v15 Multi-line (64px) / v14 Slim (40px) */
        .v12-tag-card {
            display: flex;
            align-items: center;
            padding: 0 16px;
            background: #222;
            border: 1px solid #333;
            border-radius: 6px;
            height: 40px !important;
            box-sizing: border-box !important;
            width: 100%;
            overflow: hidden;
            transition: all 0.2s ease;
        }
        .v12-tag-card.v15-mode {
            height: 64px !important;
            padding: 4px 12px;
        }

        /* Cluster System */
        .v15-cluster {
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
            height: 100%;
        }
        
        /* Col 1: Weapon Anchor */
        .v15-col-anchor {
            width: 42px;
            flex-shrink: 0;
            align-items: center;
            margin-right: 8px;
        }
        
        /* Col 2: Elemental Specs */
        .v15-col-spec {
            width: 58px;
            flex-shrink: 0;
            align-items: center;
            text-align: center;
            margin-right: 12px;
            gap: 1px;
        }
        .v15-spec-label { font-size: 0.68rem; color: #888; text-transform: uppercase; font-weight: 600; line-height: 1; }

        /* Col 3: Identity Stack (Narrower to shift bonus left) */
        .v15-col-id {
            flex: 0 0 160px;
            margin-right: 8px;
            gap: 0px;
            overflow: hidden;
        }
        .v15-name-label { font-size: 0.9rem; font-weight: 600; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.2; }
        .v15-type-label { font-size: 0.68rem; color: #777; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.2; margin-top: 1px; }

        /* Col 4: Skills Stack */
        .v15-col-skills { width: 130px; flex-shrink: 0; gap: 2px; }
        .v15-row { font-size: 0.72rem; color: #ccc; display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        /* Col 5: Bonuses Stack (Flexible to fill space) */
        .v15-col-bonuses { flex: 1; min-width: 150px; gap: 2px; align-items: flex-start; }
        .v15-row.muted { color: #888; font-size: 0.68rem; }

        /* Col 6: Remaining Count */
        .v15-col-count { width: 90px; flex-shrink: 0; align-items: flex-end; }
        .v15-count-label { color: #ff4b4b; font-weight: bold; font-size: 0.75rem; }

        /* Unified Button Heights */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stButton"] button { height: 40px !important; }
        [data-testid="stHorizontalBlock"]:has(.v15-marker) div[data-testid="stButton"] button { height: 64px !important; }

        .v12-tag-card.v12-unit-selected { border: 1px solid #f1c40f !important; }
        .v12-stream { display: flex; align-items: center; width: 100%; height: 100%; }
        
        /* Legacy Slim Card Support (Talismans) */
        .legacy-col-id { display: flex; align-items: center; flex-shrink: 0; overflow: hidden; height: 40px; }
        .v14-mode-long .legacy-col-id { width: auto; max-width: 60px; margin-right: 12px; }
        .v12-col-spec-legacy { display: flex; align-items: center; flex-shrink: 0; overflow: hidden; height: 40px; width: 260px; }
        .v12-col-slots { width: 120px; flex-shrink: 0; display: flex; align-items: center; }
        .v12-bonus-area { flex: 1; overflow: hidden; font-size: 0.76rem; color: #888; }
        .v11-sep { color: #333; margin: 0 8px; }

        /* Streamlit Padding Overrides */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) [data-testid="stMarkdownContainer"] { padding: 0 !important; margin: 0 !important; }
        [data-testid="stHorizontalBlock"]:has(.v12-marker) > div { padding: 0 !important; margin: 0 !important; }
        
        /* Responsive */
        /* Responsive - Keep skills visible but hide less critical specs */
        @media (max-width: 1000px) { .v15-col-spec { display: none; } }
        /* Removed auto-hide for skills as they are critical in v15 HUD */
        </style>
    """, unsafe_allow_html=True)

def _render_v14_tag_body(
    badge_html=None, title_text=None, sub_text=None, bonus_html=None, subtitle=None, 
    is_selected=False, mode="hud", marker_cls="", 
    weapon_type=None, weapon_name=None, element=None, element_val=None, 
    skills=None, bonuses=None, remaining_count=None, comparison=None
):
    """v15+: Triple-Cluster Layout Engine."""
    selected_cls = "v12-unit-selected" if is_selected else ""
    is_long = mode.startswith("long")
    is_cleanup = (mode == "long-cleanup")
    is_v15 = True # v15 Unified height (64px) for all, except maybe explicitly slim items
    v15_cls = "v15-mode"
    card_mode_cls = "v14-mode-long" if is_long else ""
    
    # Handle skill list passed as title_text (common in legacy calls)
    if skills is None and isinstance(title_text, list):
        skills = title_text
        title_text = ""
    elif skills is None and isinstance(title_text, str) and "[" in title_text:
        # Emergency fix for stringified lists
        try:
            import ast
            skills = ast.literal_eval(title_text)
            title_text = ""
        except: pass
    
    html = f'<div class="v12-tag-card {marker_cls} {selected_cls} {v15_cls} {card_mode_cls}"><div class="v12-stream">'
    
    if is_v15:
        # Cluster 1: Icon Anchor (Composite Weapon + Element)
        if is_long:
            # No icon for talismans as requested
            pass
        else:
            w_type = weapon_type or subtitle or ""
            # NEW: Using composite icon with element overlay for weapons
            comp_icon = Icon.get_composite_html(w_type, element, size=46)
            html += f'<div class="v15-cluster v15-col-anchor">{comp_icon}</div>'

        # Cluster 2: Elemental Specs or Rarity Badge (Talisman)
        if is_long:
            # Place Rarity Badge next to icon for talismans
            html += f'<div class="v15-cluster v15-col-spec">{badge_html}</div>'
        else:
            # NEW: Hidden icon since it's now part of the composite anchor
            e_label = element_val or element or "無"
            html += f'<div class="v15-cluster v15-col-spec"><div class="v15-spec-label" style="font-size: 0.75rem; color: #fff; margin-top: 4px;">{e_label}</div></div>'

        # Cluster 3: Skills (New priority for Talismans)
        if is_long:
            skill_list = skills if isinstance(skills, list) else ([title_text] if title_text else [])
            if is_cleanup:
                # Vertical 3 rows for Dialog Comparison - Compact Fixed Width
                s_html = ""
                for s in skill_list[:3]: 
                    s_html += f'<div class="v15-row" style="font-size:0.75rem; color:#fff; line-height:1.1;">{s}</div>'
                html += f'<div class="v15-cluster v15-col-skills" style="width:200px; gap:1px;">{s_html}</div>'
            else:
                # Horizontal joined string for Main List - Flexible width to prevent cutoff
                s_text = " / ".join(skill_list)
                html += f'<div class="v15-cluster v15-col-skills" style="flex: 1; margin-right: 20px;"><div class="v15-name-label" style="font-size:0.85rem; color:#fff;">{s_text}</div></div>'
        else:
            name = weapon_name or title_text or "UNKNOWN"
            w_type = weapon_type or subtitle or ""
            html += f'<div class="v15-cluster v15-col-id"><div class="v15-name-label">{name}</div><div class="v15-type-label">{w_type}</div></div>'

        # Cluster 4: Content Stack (Slots or Skills)
        if mode == "reinforcement" and comparison:
            html += f'<div class="v15-cluster v15-col-skills" style="width:200px;">{comparison}</div>'
        elif is_long:
            # Slot info - Differentiated widths for list vs cleanup
            slot_width = "100px" if is_cleanup else "140px"
            html += f'<div class="v15-cluster v15-col-id" style="flex:0 0 {slot_width}; text-align: right;"><div class="v15-type-label" style="font-size:0.75rem; color:#888;">{sub_text}</div></div>'
        else:
            skill_list = skills if isinstance(skills, list) else (sub_text.split("|") if sub_text else [])
            s_html = ""
            if len(skill_list) > 0:
                s1 = skill_list[0].strip()
                if s1 != "なし":
                    s_icon = Icon.get_series_icon()
                    s_html += f'<div class="v15-row">{s_icon}{s1}</div>'
            if len(skill_list) > 1:
                s1_2 = skill_list[1].strip()
                if s1_2 != "なし":
                    s_icon = Icon.get_group_icon()
                    s_html += f'<div class="v15-row">{s_icon}{s1_2}</div>'
            html += f'<div class="v15-cluster v15-col-skills">{s_html}</div>'

        # Cluster 5: Bonuses Stack
        bonus_list = bonuses if isinstance(bonuses, list) else (bonus_html.split("||") if bonus_html else [])
        b_html = ""
        for b in bonus_list:
            if b.strip():
                b_html += f'<div class="v15-row">{b.strip()}</div>'
        html += f'<div class="v15-cluster v15-col-bonuses">{b_html}</div>'

        # Cluster 6: Remaining Count (Right Aligned)
        count_val = remaining_count
        if not count_val and bonus_html and not is_long:
            # Fallback for legacy calls in reinforcement mode
            c_match = re.search(r"残り\s*(\d+)\s*回", bonus_html)
            if c_match: count_val = c_match.group(1)
        
        if count_val:
            html += f'<div class="v15-cluster v15-col-count"><div class="v15-count-label">残り {count_val} 回</div></div>'
        
        # Talisman badge is now in Cluster 2, Cluster 6 stays empty or for actions

    html += f'</div></div>'
    return html

def render_weapon_card(
    weapon_type, weapon_name, element=None, element_val=None, 
    skills=None, bonuses=None, remaining_count=None, comparison=None,
    is_selected=False, mode="hud"
):
    """v15+: Dedicated Weapon Card."""
    marker_cls = "v15-marker"
    html = _render_v14_tag_body(
        weapon_type=weapon_type, weapon_name=weapon_name, 
        element=element, element_val=element_val,
        skills=skills, bonuses=bonuses, remaining_count=remaining_count, comparison=comparison,
        is_selected=is_selected, mode=mode, marker_cls=marker_cls
    )
    st.markdown(html, unsafe_allow_html=True)

def render_selectable_weapon_card(
    weapon_type, weapon_name, key, element=None, element_val=None, 
    skills=None, bonuses=None, remaining_count=None, comparison=None,
    is_selected=False, mode="hud"
):
    """v15+: Selectable Weapon Card."""
    icon = "✔" if is_selected else "❯"
    btn_type = "primary" if is_selected else "secondary"
    marker_cls = "v15-marker"
    
    with st.container():
        c_tag, c_btn = st.columns(CARD_ACTION_RATIO, gap="small")
        with c_tag:
            html = _render_v14_tag_body(
                weapon_type=weapon_type, weapon_name=weapon_name, 
                element=element, element_val=element_val,
                skills=skills, bonuses=bonuses, remaining_count=remaining_count, comparison=comparison,
                is_selected=is_selected, mode=mode, marker_cls=marker_cls
            )
            st.markdown(html, unsafe_allow_html=True)
        with c_btn:
            clicked = st.button(icon, key=key, type=btn_type, use_container_width=True)
        return clicked

# --- LEGACY WRAPPERS ---

def render_slim_card(badge_html, title_text, sub_text, bonus_html, subtitle=None, is_selected=False, mode="hud"):
    """Legacy wrapper for backward compatibility."""
    marker_cls = "v15-marker" if not mode.startswith("long") else "v12-marker"
    html = _render_v14_tag_body(
        badge_html=badge_html, title_text=title_text, sub_text=sub_text, bonus_html=bonus_html, 
        subtitle=subtitle, is_selected=is_selected, mode=mode, marker_cls=marker_cls
    )
    st.markdown(html, unsafe_allow_html=True)

def render_selectable_card(badge_html, title_text, sub_text, bonus_html, key, subtitle=None, is_selected=False, mode="hud"):
    """Legacy wrapper for backward compatibility."""
    icon = "✔" if is_selected else "❯"
    btn_type = "primary" if is_selected else "secondary"
    marker_cls = "v15-marker" if mode != "long" else "v12-marker"
    
    with st.container():
        c_tag, c_btn = st.columns(CARD_ACTION_RATIO, gap="small")
        with c_tag:
            html = _render_v14_tag_body(
                badge_html=badge_html, title_text=title_text, sub_text=sub_text, bonus_html=bonus_html, 
                subtitle=subtitle, is_selected=is_selected, mode=mode, marker_cls=marker_cls
            )
            st.markdown(html, unsafe_allow_html=True)
        with c_btn:
            clicked = st.button(icon, key=key, type=btn_type, use_container_width=True)
        return clicked
