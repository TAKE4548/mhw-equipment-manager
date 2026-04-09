import streamlit as st
from src.components.cards import get_badge_html
from src.logic.equipment_box import ATTRIBUTE_COLORS

def render_weapon_badge(element):
    """武器属性に応じたバッジ HTML を生成する"""
    bg = ATTRIBUTE_COLORS.get(element, "#444")
    txt_c = "black" if element in ["氷", "雷", "無", "睡眠"] else "white"
    return get_badge_html(element, bgcolor=bg, color=txt_c)
