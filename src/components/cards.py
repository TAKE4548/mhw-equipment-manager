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

        /* Heading Margin Compression (Polished for balance) */
        h1, h2, h3, h4, h5 {
            margin-top: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* 0. List Item Spacing - Direct margin for reliability */
        [data-testid="stHorizontalBlock"]:has(.v12-marker),
        [data-testid="stHorizontalBlock"]:has(.v15-marker) {
            align-items: center !important;
            margin-bottom: 8px !important;
            gap: 12px !important;
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
            padding: 8px 16px;
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
        /* v15 Button Sync */
        [data-testid="stHorizontalBlock"]:has(.v15-marker) div[data-testid="stButton"] button {
            height: 64px !important;
        }

        /* Selection */
        .v12-tag-card.v12-selected { border: 1px solid #f1c40f !important; background: #222 !important; }
        [data-testid="stHorizontalBlock"]:has(.v12-unit-selected) button { background: #f1c40f !important; border: 1px solid #f1c40f !important; color: #000 !important; }

        /* HUD STREAMS & ALIGNMENT */
        .v12-stream { display: flex; align-items: center; width: 100%; white-space: nowrap; overflow: hidden; height: 100%; }
        .v15-mode .v12-stream { white-space: normal; }
        
        /* v15 ID Cluster (Stacked) */
        .v15-id-stack {
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 140px;
            flex-shrink: 0;
            overflow: hidden;
            margin-right: 12px;
        }
        .v15-type-label { font-size: 0.85rem; font-weight: 700; color: #fff; text-transform: uppercase; line-height: 1.2; }
        .v15-name-label { font-size: 0.7rem; color: #888; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }

        /* v15 Attribute/Enhancement (Center) - Refined: Stacked */
        .v15-col-center {
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 140px;
            flex-shrink: 0;
            overflow: hidden;
            margin-right: 8px;
        }
        .v15-enh-label { font-size: 0.72rem; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .v15-attr-label { font-size: 0.65rem; color: #666; text-transform: uppercase; }

        /* v15 Spec/Bonus stacks */
        .v15-stack {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2px;
            overflow: hidden;
        }
        .v15-col-skills { flex: 1; min-width: 0; }
        .v15-col-bonuses { width: 280px; flex-shrink: 0; align-items: flex-start; } /* Expanded to prevent 5-slot clipping */
        
        .v15-row {
            font-size: 0.72rem;
            color: #ccc;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .v15-row.muted { color: #888; font-size: 0.68rem; }

        /* Legacy HUD Alignment (for Talismans/Slim) */
        .v12-col-id { display: flex; align-items: center; flex-shrink: 0; overflow: hidden; height: 40px; }
        .v14-mode-hud .v12-col-id { width: 180px; } 
        .v14-mode-long .v12-col-id { width: auto; max-width: 60px; margin-right: 12px; }

        /* v12-col-spec: Base spec area */
        .v12-col-spec { display: flex; align-items: center; flex-shrink: 0; overflow: hidden; height: 40px; }
        .v14-mode-long .v12-col-spec { width: 260px; } /* Adjusted width for X-axis alignment */

        .v12-main-label { font-weight: 600; font-size: 0.9rem; color: #fff; overflow: hidden; text-overflow: ellipsis; }
        .v12-col-metric { display: flex; align-items: center; width: 100px; flex-shrink: 0; overflow: hidden; font-size: 0.75rem; justify-content: center; }
        .v12-skill-label { font-size: 0.85rem; color: #eee; display: flex; align-items: center; gap: 8px; flex-wrap: nowrap; white-space: nowrap; overflow: hidden; line-height: 40px; }
        .v14-mode-long .v12-skill-label { font-size: 0.85rem; color: #eee; }
        .v11-sep { color: #333; margin: 0 8px; font-weight: 300; flex-shrink: 0; }
        .v12-bonus-area { font-size: 0.76rem; color: #888; flex: 1; overflow: hidden; text-overflow: ellipsis; }
        .v12-sub-label { font-size: 0.65rem; color: #666; text-transform: uppercase; min-width: 60px; flex-shrink: 0; }
        
        /* v12-col-slots: Specialized fixed-width column for X-axis alignment in slim cards */
        .v12-col-slots {
            width: 120px;
            flex-shrink: 0;
            font-size: 0.75rem;
            color: #888;
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }

        /* Sync container heights - NO line-height:0 as it squashes text */
        [data-testid="stHorizontalBlock"]:has(.v12-marker) [data-testid="stMarkdownContainer"] { padding: 0 !important; margin: 0 !important; }
        [data-testid="stHorizontalBlock"]:has(.v12-marker) > div { padding: 0 !important; margin: 0 !important; }
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stPopover"] button,
        [data-testid="stHorizontalBlock"]:has(.v12-marker) div[data-testid="stPopover"] { height: 40px !important; min-height: 40px !important; }

        /* v15 Height Sync */
        [data-testid="stHorizontalBlock"]:has(.v15-marker) div[data-testid="stPopover"] button,
        [data-testid="stHorizontalBlock"]:has(.v15-marker) div[data-testid="stPopover"] { height: 64px !important; min-height: 64px !important; }

        /* v14 Responsive Grid Container */
        .v14-grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 8px;
            width: 100%;
            margin-top: 0.5rem;
        }

        @media (max-width: 1000px) { .v15-col-center { display: none; } }
        @media (max-width: 800px) { .v15-col-skills { display: none; } }
        </style>
    """, unsafe_allow_html=True)

def _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode):
    """v15: Unified Multi-line Card (Supports 'hud', 'long', and 'reinforcement')."""
    selected_cls = "v12-selected" if is_selected else ""
    is_long = mode.startswith("long")
    v15_cls = "v15-mode" if not is_long else ""
    card_mode_cls = "v14-mode-long" if is_long else ""
    
    html = f'<div class="v12-tag-card {selected_cls} {v15_cls} {card_mode_cls}"><div class="v12-stream">'
    
    if is_long:
        # Legacy/Talisman Long mode (Stay 40px)
        html += f'<div class="v12-col-id">{badge_html}</div>'
        html += f'<div class="v12-col-spec"><div class="v12-skill-label" style="color:#aaa;">{title_text}</div></div>'
        html += f'<span class="v11-sep">|</span><div class="v12-col-slots">{sub_text}</div>'
        html += f'<span class="v11-sep">|</span><div class="v12-bonus-area">{bonus_html}</div>'
    
    elif mode == "hud":
        # Standard V15 (Used in Equipment Box / Lottery)
        # 0. Attribute Icon (Badge)
        html += f'<div style="flex-shrink:0; margin-right:8px;">{badge_html}</div>'

        # 1. ID Cluster (Type above Name)
        html += f'<div class="v15-id-stack"><div class="v15-type-label">{subtitle or "UNKNOWN"}</div><div class="v15-name-label">{title_text}</div></div>'
        
        # 2. Center: Enhancement (Top) + Attribute Name (Bottom)
        enh_type = ""
        skills_raw = sub_text
        if "📋" in sub_text:
            parts = sub_text.split("|", 1)
            enh_type = parts[0].strip()
            skills_raw = parts[1].strip() if len(parts) > 1 else ""
        
        # Extract Attribute Name from badge_html
        import re
        attr_match = re.search(r'>(.*?)</span>', badge_html)
        attr_name = attr_match.group(1) if attr_match else ""
        
        html += f'<div class="v15-col-center"><div class="v15-enh-label">{enh_type}</div><div class="v15-attr-label">{attr_name}属性</div></div>'
        
        # 3. Skills Stack
        s_parts = skills_raw.split("|")
        s1 = s_parts[0].strip() if len(s_parts) > 0 else ""
        s2 = s_parts[1].strip() if len(s_parts) > 1 else ""
        html += f'<div class="v15-stack v15-col-skills"><div class="v15-row">{s1}</div><div class="v15-row">{s2}</div></div>'
        
        # 4. Bonuses Stack
        b_parts = bonus_html.split("||")
        b1 = b_parts[0].strip() if len(b_parts) > 0 else ""
        b2 = b_parts[1].strip() if len(b_parts) > 1 else ""
        html += f'<div class="v15-stack v15-col-bonuses"><div class="v15-row">{b1}</div><div class="v15-row">{b2}</div></div>'

    elif mode == "reinforcement":
        # Special Reinforcement comparison mode
        # 0. Badge
        html += f'<div style="flex-shrink:0; margin-right:8px;">{badge_html}</div>'

        # 1. ID Cluster
        html += f'<div class="v15-id-stack" style="width:120px;"><div class="v15-type-label">{subtitle or "UNKNOWN"}</div><div class="v15-name-label">{title_text}</div></div>'
        
        # 2. Center Cluster: Attribute Name stack
        import re
        attr_match = re.search(r'>(.*?)</span>', badge_html)
        attr_name = attr_match.group(1) if attr_match else ""
        html += f'<div class="v15-col-center" style="width:70px;"><div class="v15-attr-label">{attr_name}属性</div></div>'
        
        # 3. Info Cluster (Prod Bonus + Enh Type)
        prod_bonus = ""
        enh_type = ""
        if "📋" in sub_text:
            parts = sub_text.split("📋")
            if len(parts) > 1:
                sub_parts = parts[1].split("|")
                enh_type = f"📋 {sub_parts[0].strip()}"
                if len(sub_parts) > 1: prod_bonus = sub_parts[1].strip()
        
        if not prod_bonus and "🛠️" in sub_text:
            p_parts = sub_text.split("🛠️")
            prod_bonus = f"🛠️ {p_parts[1].strip()}"
            
        html += f'<div class="v15-stack" style="width:160px; margin-right:12px;">'
        html += f'<div class="v15-row">{prod_bonus}</div><div class="v15-row muted">{enh_type}</div></div>'
        
        # 4. Comparison Area (Before/After Restoration)
        # We wrap it in its own stream to treat it as a block
        clean_bonus = re.sub(r'<div.*?残り.*?回.*?</div>', '', bonus_html)
        html += f'<div class="v15-stack v15-col-bonuses" style="flex:1;">{clean_bonus}</div>'

        # 5. Remaining Count (Right End)
        count_html = ""
        # Match "残り X 回" with or without space/stars
        c_match = re.search(r'残り\s*(\d+)\s*回', bonus_html)
        if c_match:
            c_val = c_match.group(1)
            count_html = f'<div class="v15-stack" style="width:100px; align-items:flex-end;"><div class="v15-row" style="color:#ff4b4b; font-weight:bold;">残り {c_val} 回</div></div>'
        html += count_html

    html += f'</div></div>'
    return html

def render_slim_card(badge_html, title_text, sub_text, bonus_html, subtitle=None, is_selected=False, mode="hud"):
    """Displays the v14 context-aware tag without button."""
    marker_cls = "v15-marker" if not mode.startswith("long") else "v12-marker"
    st.markdown(f'<div class="{marker_cls}" style="display:none"></div>', unsafe_allow_html=True)
    html = _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode)
    st.markdown(html, unsafe_allow_html=True)

def render_selectable_card(badge_html, title_text, sub_text, bonus_html, key, subtitle=None, is_selected=False, mode="hud"):
    """v14: Context-aware selection tag."""
    selected_cls = "v12-unit-selected" if is_selected else ""
    icon = "✔" if is_selected else "❯"
    
    marker_cls = "v15-marker" if mode != "long" else "v12-marker"
    
    with st.container():
        st.markdown(f'<div class="{marker_cls} {selected_cls}" style="display:none"></div>', unsafe_allow_html=True)
        # Always use the unified ratio defined in v14
        c_tag, c_btn = st.columns(CARD_ACTION_RATIO, gap="small")
        
        with c_tag:
            html = _render_v14_tag_body(badge_html, title_text, sub_text, bonus_html, subtitle, is_selected, mode)
            st.markdown(html, unsafe_allow_html=True)
            
        with c_btn:
            clicked = st.button(icon, key=key, use_container_width=True)
            
        return clicked
