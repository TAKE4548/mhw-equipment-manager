import streamlit as st
import base64
import os
from pathlib import Path

# Mapping for icons
# Keys should be consistent and used by atoms/components
# Mapping for icons (Now using SVG assets in subdirectories)
ICON_MAP = {
    # Weapons (Note: Directory name is 'wepons')
    "大剣": "wepons/大剣.svg",
    "太刀": "wepons/太刀.svg",
    "片手剣": "wepons/片手剣.svg",
    "双剣": "wepons/双剣.svg",
    "ハンマー": "wepons/ハンマー.svg",
    "狩猟笛": "wepons/狩猟笛.svg",
    "ランス": "wepons/ランス.svg",
    "ガンランス": "wepons/ガンランス.svg",
    "スラッシュアックス": "wepons/スラッシュアックス.svg",
    "チャージアックス": "wepons/チャージアックス.svg",
    "操虫棍": "wepons/操虫棍.svg",
    "ライトボウガン": "wepons/ライトボウガン.svg",
    "ヘビィボウガン": "wepons/ヘビィボウガン.svg",
    "弓": "wepons/弓.svg",
    
    # Elements
    "火": "elements/火.svg",
    "水": "elements/水.svg",
    "雷": "elements/雷.svg",
    "氷": "elements/氷.svg",
    "龍": "elements/龍.svg",
    "毒": "elements/毒.svg",
    "麻痺": "elements/麻痺.svg",
    "睡眠": "elements/睡眠.svg",
    "爆破": "elements/爆破.svg",
    "無": None,
    
    # Skills / Others
    "series": "others/グループスキル.svg",
    "group": "others/シリーズスキル.svg",
    "護石": None
}

class Icon:
    @staticmethod
    @st.cache_resource
    def get_base64(filename):
        """Loads an icon from assets/icons and returns its base64 string."""
        if not filename:
            return None
        
        try:
            icon_path = Path("assets/icons") / filename
            if not icon_path.exists():
                return None
                
            with open(icon_path, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
                ext = filename.split(".")[-1]
                mime = f"image/{ext}" if ext != "svg" else "image/svg+xml"
                return f"data:{mime};base64,{encoded}"
        except Exception:
            return None

    @staticmethod
    @st.cache_resource
    def get_style_sheet():
        """Generates a CSS style sheet for all icons including Masking support."""
        styles = []
        styles.append("""
            .mhw-icon {
                display: inline-block;
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                vertical-align: middle;
                flex-shrink: 0;
            }
            .mhw-icon-mask {
                -webkit-mask-size: contain;
                -webkit-mask-repeat: no-repeat;
                -webkit-mask-position: center;
                mask-size: contain;
                mask-repeat: no-repeat;
                mask-position: center;
                background-color: currentColor;
            }
            /* Stacked Icon Container */
            .mhw-stacked-icon {
                position: relative;
                display: inline-block;
                flex-shrink: 0;
                transition: transform 0.2s ease-out;
            }
            .mhw-stacked-icon:hover {
                transform: scale(1.15);
                z-index: 10;
            }
            .mhw-sub-icon {
                position: absolute;
                bottom: -2px;
                right: -2px;
                border-radius: 50%;
                /* Halo Effect: CSS Drop Shadow can simulate the border for complex shapes */
                filter: drop-shadow(0 0 1px #111) drop-shadow(0 0 1px #111) drop-shadow(0 0 1px #111);
                background-color: #111; /* Fallback ground */
            }
        """)
        
        for key, filename in ICON_MAP.items():
            if not filename: continue
            b64 = Icon.get_base64(filename)
            if b64:
                # Use escaped key for class name
                safe_key = base64.b16encode(key.encode()).decode()
                # Define both background (legacy/fixed) and mask (tintable)
                styles.append(f'.mhw-icon-{safe_key} {{ background-image: url("{b64}"); }}')
                styles.append(f'.mhw-icon-mask-{safe_key} {{ -webkit-mask-image: url("{b64}"); mask-image: url("{b64}"); }}')
        
        return "\n".join(styles)

    @staticmethod
    def get_html(key, size=24, style="", tint=None):
        """Returns a lightweight HTML div for the icon using CSS classes."""
        filename = ICON_MAP.get(key)
        if not filename:
            return ""
        
        safe_key = base64.b16encode(key.encode()).decode()
        if tint:
            # Use Masking for dynamic color
            return f'<div class="mhw-icon mhw-icon-mask mhw-icon-mask-{safe_key}" style="width:{size}px; height:{size}px; color:{tint}; {style}"></div>'
        else:
            # Use standard background (multi-color SVG)
            return f'<div class="mhw-icon mhw-icon-{safe_key}" style="width:{size}px; height:{size}px; {style}"></div>'

    @staticmethod
    def get_composite_html(weapon_type, element, size=48):
        """Returns a composite icon (Weapon + Element Overlay) as requested in Pattern 1."""
        # Main Weapon Icon (Large)
        # Using white/gold color for weapon depending on HUD? Let's use currentColor.
        w_icon_html = Icon.get_html(weapon_type, size=size)
        
        # Sub Element Icon (Overlay)
        if not element or element == "無":
            return f'<div class="mhw-stacked-icon" style="width:{size}px; height:{size}px;">{w_icon_html}</div>'
            
        e_size = int(size * 0.45)
        # Attribute colors (Standard MH set)
        attr_colors = {
            "火": "#ff4b00", "水": "#0099ff", "雷": "#ffe600", "氷": "#00ffff", "龍": "#9900ff",
            "毒": "#cc33ff", "麻痺": "#ffcc00", "睡眠": "#66ccff", "爆破": "#ff6600"
        }
        e_color = attr_colors.get(element, "#ffffff")
        e_icon_html = Icon.get_html(element, size=e_size, tint=e_color)
        
        html = f"""
        <div class="mhw-stacked-icon" style="width:{size}px; height:{size}px;">
            {w_icon_html}
            <div class="mhw-sub-icon" style="width:{e_size}px; height:{e_size}px;">
                {e_icon_html}
            </div>
        </div>
        """
        return html

    @staticmethod
    def get_weapon_icon(weapon_type, size=28):
        return Icon.get_html(weapon_type, size=size)

    @staticmethod
    def get_element_icon(element, size=20):
        # Apply standard MH element color via tint
        attr_colors = {
            "火": "#ff4b00", "水": "#0099ff", "雷": "#ffe600", "氷": "#00ffff", "龍": "#9900ff",
            "毒": "#cc33ff", "麻痺": "#ffcc00", "睡眠": "#66ccff", "爆破": "#ff6600"
        }
        color = attr_colors.get(element, "#ffffff")
        return Icon.get_html(element, size=size, tint=color, style="border-radius: 4px;")

    @staticmethod
    def get_series_icon(size=16):
        """Returns Series Skill icon (Light Blue)."""
        return Icon.get_html("series", size=size)

    @staticmethod
    def get_group_icon(size=16):
        """Returns Group Skill icon (Bronze)."""
        return Icon.get_html("group", size=size)

    @staticmethod
    def get_talisman_icon(size=32):
        """Returns Talisman icon (Magatama)."""
        return Icon.get_html("護石", size=size)

def get_attr_icon_stack(attr_key, size_icon=20, size_text="0.65rem", show_text=True):
    """Returns a stacked layout for attribute icon + name."""
    icon_html = Icon.get_element_icon(attr_key, size=size_icon)
    if not icon_html:
        return ""
        
    text_html = f'<div style="font-size: {size_text}; color: #888; text-align: center; line-height: 1;">{attr_key}</div>' if show_text else ""
    return f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;">{icon_html}{text_html}</div>'
