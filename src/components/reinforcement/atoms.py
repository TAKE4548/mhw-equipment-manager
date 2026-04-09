import streamlit as st
from src.components.cards import get_badge_html
from src.logic.equipment_box import ATTRIBUTE_COLORS, get_abbr_item

def render_weapon_attribute_badge(element):
    """武器の属性に応じたバッジ HTML を生成する"""
    bg = ATTRIBUTE_COLORS.get(element, "#444")
    txt_c = "black" if element in ["氷", "雷", "無", "睡眠"] else "white"
    return get_badge_html(element, bgcolor=bg, color=txt_c)

def build_visual_comparison_bar(before_labels, after_labels):
    """
    v15: 強化前後の比較バー(HTML)を構築する。
    2段構成（Row1: Before, Row2: After）を返す。
    """
    # Build Before Row
    bc_html = "".join([f'<span style="color:#666; font-size:0.75rem; margin-right:4px;">{s}</span>' for s in before_labels])
    row1 = f'<div class="v15-row">✨ {bc_html}</div>'
    
    # Build After Row
    ac_html = []
    for i, s in enumerate(after_labels):
        is_changed = (s != before_labels[i])
        clr = "#f1c40f" if is_changed else "#ccc"
        fw = "bold" if is_changed else "normal"
        ac_html.append(f'<span style="color:{clr}; font-weight:{fw}; font-size:0.8rem; margin-right:4px;">{s}</span>')
    row2 = f'<div class="v15-row">➡️ {"".join(ac_html)}</div>'
    
    return f"{row1}{row2}"

def get_restoration_labels(row, prefix=""):
    """
    行データから復元ボーナスの略称リストを取得する。
    """
    labels = []
    for i in range(1, 6):
        r_type = row.get(f'{prefix}rest_{i}_type', 'なし')
        r_lvl = row.get(f'{prefix}rest_{i}_level', '')
        if r_type != "なし":
            labels.append(get_abbr_item(f"{r_type}{r_lvl if r_lvl != '無印' else ''}"))
        else:
            labels.append("なし")
    return labels
