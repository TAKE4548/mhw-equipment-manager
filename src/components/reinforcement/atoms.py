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
    v14: 強化前後の比較バー(HTML)を構築する。
    差分がある箇所を強調表示する。
    """
    # Before labels: 控えめな色で表示
    bc = " ".join([f'<span style="color:#666; font-size:0.78rem; margin-right:4px;">{s}</span>' for s in before_labels])
    
    # After labels: 変更箇所を強調（黄色/太字）
    ac = []
    for i, s in enumerate(after_labels):
        is_changed = (s != before_labels[i])
        clr = "#f1c40f" if is_changed else "#ccc"
        fw = "bold" if is_changed else "normal"
        ac.append(f'<span style="color:{clr}; font-weight:{fw}; font-size:0.9rem; margin-right:8px; display:inline-block;">{s}</span>')
    
    h = '<div style="display:flex; align-items:center; gap:10px; white-space:nowrap;">'
    h += f'<div style="display:flex; align-items:center; opacity:0.7;">{bc}</div>'
    h += '<span style="color:#ffd700; font-size:0.85rem; flex-shrink:0;">❯❯</span>'
    h += f'<div style="display:flex; align-items:center;">{" ".join(ac)}</div>'
    h += '</div>'
    return h

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
