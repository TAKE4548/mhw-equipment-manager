import streamlit as st
import base64
import os
from pathlib import Path

# Mapping for icons
# Keys should be consistent and used by atoms/components
ICON_MAP = {
    # Weapons
    "大剣": "大剣.png",
    "太刀": "太刀.png",
    "片手剣": "片手剣.png",
    "双剣": "双剣.png",
    "ハンマー": "ハンマー.png",
    "狩猟笛": "狩猟笛.png",
    "ランス": "ランス.png",
    "ガンランス": "ガンランス.png",
    "スラッシュアックス": "スラッシュアックス.png",
    "チャージアックス": "チャージアックス.png",
    "操虫棍": "操虫棍.png",
    "ライトボウガン": "ライトボウガン.png",
    "ヘビィボウガン": "ヘビィボウガン.png",
    "弓": "弓.png",
    
    # Elements
    "火": "火.jpg",
    "水": "水.jpg",
    "雷": "雷.jpg",
    "氷": "氷.jpg",
    "龍": "龍.jpg",
    "毒": "毒.jpg",
    "麻痺": "麻痺.jpg",
    "睡眠": "睡眠.jpg",
    "爆破": "爆破.jpg",
    "無": None,
    
    # Skills
    "series": "グループスキル.png",
    "group": "シリーズスキル.png",
    "護石": "護石.png"
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
                mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
        except Exception:
            return None

    @staticmethod
    def get_style_sheet():
        """Generates a CSS style sheet for all icons to avoid redundant Base64 transfer."""
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
        """)
        
        for key, filename in ICON_MAP.items():
            if not filename: continue
            b64 = Icon.get_base64(filename)
            if b64:
                # Use escaped key for class name
                safe_key = base64.b16encode(key.encode()).decode()
                styles.append(f'.mhw-icon-{safe_key} {{ background-image: url("{b64}"); }}')
        
        return "\n".join(styles)

    @staticmethod
    def get_html(key, size=24, style=""):
        """Returns a lightweight HTML div for the icon using CSS classes."""
        filename = ICON_MAP.get(key)
        if not filename:
            return ""
        
        safe_key = base64.b16encode(key.encode()).decode()
        return f'<div class="mhw-icon mhw-icon-{safe_key}" style="width:{size}px; height:{size}px; {style}"></div>'

    @staticmethod
    def get_weapon_icon(weapon_type, size=28):
        return Icon.get_html(weapon_type, size=size)

    @staticmethod
    def get_element_icon(element, size=20):
        return Icon.get_html(element, size=size, style="border-radius: 4px;")

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
