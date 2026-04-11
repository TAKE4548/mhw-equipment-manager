import streamlit as st
import pandas as pd
import numpy as np
from src.logic.master import get_master_data
from src.logic.restoration_tracker import update_tracker

@st.dialog("トラッキング内容を編集")
def edit_tracker_dialog(row, w_row, user_id):
    """トラッキング中の強化抽選内容を編集するダイアログ"""
    master = get_master_data()
    st.markdown(f"**{w_row['weapon_name']}** のトラッキング編集")
    
    new_count = st.number_input("残り回数", min_value=1, value=int(row['remaining_count']))
    
    sel_w_type = w_row['weapon_type']
    sel_element = w_row['element']
    is_bow = ("弓" in sel_w_type and "ボウガン" not in sel_w_type)
    is_bowgun = ("ボウガン" in sel_w_type)
    
    # 選択肢の構築ロジック
    dyn_opts = ["なし"]
    for rt, lvs in master.get("restoration_bonuses", {}).items():
        if rt == "なし": continue
        if rt == "切れ味強化" and (is_bow or is_bowgun): continue
        if rt == "装填強化" and not is_bowgun: continue
        if rt == "属性強化" and (sel_element == "無" or (is_bow and sel_element in ["毒", "麻痺", "睡眠", "爆破"])): continue
        for lv in lvs:
            dyn_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
            
    def get_rb_label(t, l):
        if t == "なし": return "なし"
        return t if l == "無印" else f"{t} [{l}]"
    
    rb_vals = []
    for i in range(5):
        curr_t = row.get(f'target_rest_{i+1}_type', 'なし')
        curr_l = row.get(f'target_rest_{i+1}_level', 'なし')
        
        # NaN 対策
        curr_t = "なし" if pd.isna(curr_t) else curr_t
        curr_l = "なし" if pd.isna(curr_l) else curr_l
        
        curr_label = get_rb_label(curr_t, curr_l)
        default_idx = dyn_opts.index(curr_label) if curr_label in dyn_opts else 0
        val = st.selectbox(f"枠{i+1}", dyn_opts, index=default_idx, key=f"etrb{i+1}_{row['id']}")
        rb_vals.append(val)
        
    if st.button("保存", type="primary", use_container_width=True):
        parsed_rbs = []
        for rb in rb_vals:
            if rb == "なし": parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else: parsed_rbs.append({"type": rb, "level": "無印"})
            
        try:
            if update_tracker(row['id'], new_count, parsed_rbs, user_id=user_id):
                st.toast("更新しました")
                st.rerun()
            else: st.error("更新に失敗しました")
        except Exception as e:
            st.error(f"更新失敗: {str(e)}")
