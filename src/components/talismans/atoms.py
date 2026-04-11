import streamlit as st
import pandas as pd

def render_rarity_badge(rarity):
    """レア度に応じたデザインのバッジを生成する (HTML)"""
    # デザイン方針: v14 HUD システムに準拠した高コントラスト設計
    bg = "#e74c3c" if rarity == 8 else "#9b59b6" if rarity == 7 else "#3498db"
    return f'<div style="background:{bg}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; width:max-content;">R{rarity}</div>'

def format_slot_icon(level, is_weapon=False):
    """スロットレベルをアイコン的な表記に変換する"""
    if pd.isna(level) or level == 0:
        return "ー"
    if is_weapon:
        return f"[{int(level)}]"
    # Unicode サークル数字による視認性向上
    return {1: "①", 2: "②", 3: "③", 4: "④"}.get(int(level), "ー")

def build_talisman_visual_info(row):
    """護石の1行分の表示用テキストとバッジを構築する (O(N)ループ外での実行を想定)"""
    # スキル文字列
    skills = []
    for i in [1, 2, 3]:
        name = row.get(f'skill_{i}_name')
        level = row.get(f'skill_{i}_level')
        if pd.notna(name) and name != "" and name != "なし":
            skills.append(f"{name} Lv{int(level)}")
    
    disp_skill = skills
    
    # スロット文字列
    w_sl_val = row.get('weapon_slot_level', 0)
    w_sl = format_slot_icon(w_sl_val, is_weapon=True) if w_sl_val > 0 else ""
    
    a_sl = "".join([format_slot_icon(row.get(f'armor_slot_{i}_level', 0)) for i in [1, 2, 3]])
    disp_slot = f"Slot: {w_sl}{a_sl}"
    
    # バッジ HTML
    disp_badge = render_rarity_badge(row['rarity'])
    
    return disp_skill, disp_slot, disp_badge
