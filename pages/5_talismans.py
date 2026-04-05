import streamlit as st
import pandas as pd
from src.logic.talismans import (
    load_talismans, add_talisman, delete_talisman, toggle_favorite as toggle_talisman_fav,
    validate_talisman, get_all_skills_flat, get_skill_level_from_master, load_talisman_master, parse_master_slot,
    get_valid_skill_names, get_valid_levels_for_skill, get_valid_slot_levels
)
from src.logic.favorites import get_favorite_list, add_favorite, remove_favorite
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css, render_slim_card
from src.logic.history import undo_last_action, redo_last_action, get_history

st.set_page_config(page_title="鑑定護石管理", page_icon="📿", layout="wide")
inject_card_css()
render_shared_sidebar()

# --- 1. Session State Initialization ---
if "r_form" not in st.session_state:
    st.session_state["r_form"] = {
        "rarity": None,
        "s1_name": "なし", "s1_level": 0,
        "s2_name": "なし", "s2_level": 0,
        "s3_name": "なし", "s3_level": 0,
        "slot_1": 0, "slot_2": 0, "slot_3": 0
    }

if "active_dialog" not in st.session_state:
    st.session_state["active_dialog"] = None

# --- 2. Forced Reset Helpers ---
def reset_from_rarity():
    st.session_state["r_form"]["s1_name"] = "なし"; st.session_state["r_form"]["s1_level"] = 0
    reset_from_s1()

def reset_from_s1():
    st.session_state["r_form"]["s2_name"] = "なし"; st.session_state["r_form"]["s2_level"] = 0
    reset_from_s2()

def reset_from_s2():
    st.session_state["r_form"]["s3_name"] = "なし"; st.session_state["r_form"]["s3_level"] = 0
    reset_from_s3()

def reset_from_s3():
    st.session_state["r_form"]["slot_1"] = 0
    reset_from_slot1()

def reset_from_slot1():
    st.session_state["r_form"]["slot_2"] = 0
    reset_from_slot2()

def reset_from_slot2():
    st.session_state["r_form"]["slot_3"] = 0

# --- 3. Dialog Implementation with Fragment for Seamless Phase Switching ---
@st.dialog("🎯 スキル選択")
def skill_dialog_root(key: str):
    # Use a fragment to isolate internal dialog reruns (phase switching)
    @st.fragment
    def dialog_body():
        f = st.session_state["r_form"]
        rarity = f["rarity"]
        idx = int(key[1])
        
        # Local phase within the dialog (can use session state to persist across fragment reruns)
        if f"dialog_phase_{key}" not in st.session_state:
            st.session_state[f"dialog_phase_{key}"] = "name"
        phase = st.session_state[f"dialog_phase_{key}"]
        
        # Calculate context
        prev = []
        for i in range(1, idx):
            n = f[f"s{i}_name"]; l = f[f"s{i}_level"]
            if n != "なし": prev.append((n, l))
        
        if phase == "name":
            st.subheader("1. スキル名を選択")
            names = get_valid_skill_names(rarity, prev)
            favs = get_favorite_list("talisman_skill")
            sorted_names = sorted(names, key=lambda x: (x not in favs, x))
            
            if st.button("🚫 なしを選択", use_container_width=True):
                f[f"{key}_name"] = "なし"; f[f"{key}_level"] = 0
                if key == "s1": reset_from_s1()
                elif key == "s2": reset_from_s2()
                elif key == "s3": reset_from_s3()
                st.session_state["active_dialog"] = None # Clear trigger
                st.rerun() # Full Rerun to update main UI and close dialog
                
            st.divider()
            for n in sorted_names:
                c1, c2 = st.columns([5, 1])
                with c1:
                    # Clicking this button triggers a FRAGMENT rerun, not a full app rerun
                    if st.button(n, key=f"sel_n_{n}_{key}", use_container_width=True):
                        st.session_state[f"temp_name_{key}"] = n
                        st.session_state[f"dialog_phase_{key}"] = "level"
                        st.rerun(scope="fragment")
                with c2:
                    is_f = n in favs
                    if st.button("⭐" if is_f else "☆", key=f"fav_n_{n}_{key}", use_container_width=True):
                        if is_f: remove_favorite("talisman_skill", n)
                        else: add_favorite("talisman_skill", n)
                        st.rerun(scope="fragment")
        
        elif phase == "level":
            n = st.session_state[f"temp_name_{key}"]
            st.subheader(f"2. レベルを選択 ({n})")
            lvls = get_valid_levels_for_skill(rarity, prev, n)
            
            if st.button("⬅️ 名前を選び直す", use_container_width=True):
                st.session_state[f"dialog_phase_{key}"] = "name"
                st.rerun(scope="fragment")
                
            st.divider()
            for l in lvls:
                # Selecting a level completes the process -> Full Rerun to close dialog
                if st.button(f"Lv{l}", key=f"btn_l_{l}_{key}", use_container_width=True):
                    f[f"{key}_name"] = n; f[f"{key}_level"] = l
                    if key == "s1": reset_from_s1()
                    elif key == "s2": reset_from_s2()
                    elif key == "s3": reset_from_s3()
                    st.session_state["active_dialog"] = None
                    # Clean up local dialog state
                    if f"dialog_phase_{key}" in st.session_state: del st.session_state[f"dialog_phase_{key}"]
                    st.rerun() # Full app rerun to close dialog and show results

    dialog_body()

# Trigger dialog if state is active
if st.session_state["active_dialog"]:
    skill_dialog_root(st.session_state["active_dialog"])

# --- 4. Main App UI ---
st.title("鑑定護石管理 📿")
st.markdown("マカ錬金の「鑑定」で入手した護石を登録・管理します。")

# History
h1, h2, h3 = st.columns([1, 1, 6])
u, r = get_history()
with h1:
    if st.button("Undo ↩️", disabled=not u, use_container_width=True):
        if undo_last_action(): st.rerun()
with h2:
    if st.button("Redo ↪️", disabled=not r, use_container_width=True):
        if redo_last_action(): st.rerun()

st.divider()

# Registration Form
with st.expander("➕ 新しい鑑定護石を登録する", expanded=True):
    f = st.session_state["r_form"]
    st.markdown("#### 1. レア度とスキル構成")
    
    # Rarity (The Root)
    opts = [None, 5, 6, 7, 8]
    idx = opts.index(f["rarity"]) if f["rarity"] in opts else 0
    new_r = st.selectbox("レア度", opts, index=idx, format_func=lambda x: str(x) if x is not None else "選択してください")
    if new_r != f["rarity"]:
        f["rarity"] = new_r
        reset_from_rarity()
        st.rerun()
        
    st.info("スキルを左から順に決定してください。上流を変更すると下流はリセットされます。")
    c1, c2, c3 = st.columns(3)
    
    def skill_btn(idx, disabled=False):
        n = f[f"s{idx}_name"]; l = f[f"s{idx}_level"]
        lbl = f"第{idx}: **{n} ({l})**" if n != "なし" else f"第{idx}: **未選択**"
        st.write(lbl)
        if st.button("選択", key=f"open_{idx}", disabled=disabled, use_container_width=True):
            st.session_state["active_dialog"] = f"s{idx}"
            st.rerun()

    with c1: skill_btn(1, disabled=(f["rarity"] is None))
    with c2: skill_btn(2, disabled=(f["rarity"] is None or f["s1_name"] == "なし"))
    with c3: skill_btn(3, disabled=(f["rarity"] is None or f["s2_name"] == "なし"))

    st.divider()
    st.markdown("#### 2. スロット構成")
    
    # Context for slots
    s_tuples = []
    for i in range(1, 4):
        if f[f"s{i}_name"] != "なし": s_tuples.append((f[f"s{i}_name"], f[f"s{i}_level"]))
    
    # Slots only active after rarity and at least one skill
    slots_active = (f["rarity"] is not None) and (len(s_tuples) > 0)
    
    c_sl1, c_sl2, c_sl3 = st.columns(3)
    l1 = "武器" if f["rarity"] == 8 else "防具①"
    l2 = "防具①" if f["rarity"] == 8 else "防具②"
    l3 = "防具②" if f["rarity"] == 8 else "防具③"

    # Slot 1
    o1 = get_valid_slot_levels(f["rarity"], s_tuples, []) if slots_active else [0]
    if f["slot_1"] not in o1: f["slot_1"] = o1[0]; reset_from_slot1()
    
    v1 = c_sl1.selectbox(l1, o1, index=o1.index(f["slot_1"]), disabled=not slots_active, key="s1_sel")
    if v1 != f["slot_1"]:
        f["slot_1"] = v1
        reset_from_slot1()
        st.rerun() # Full rerun to recalculate downstream options
        
    # Slot 2
    o2 = get_valid_slot_levels(f["rarity"], s_tuples, [f["slot_1"]]) if slots_active else [0]
    if f["slot_2"] not in o2: f["slot_2"] = o2[0]; reset_from_slot2()
    
    v2 = c_sl2.selectbox(l2, o2, index=o2.index(f["slot_2"]), disabled=not slots_active or (len(o2) <= 1 and o2[0] == 0 and f["slot_1"] == 0), key="s2_sel")
    if v2 != f["slot_2"]:
        f["slot_2"] = v2
        reset_from_slot2()
        st.rerun()

    # Slot 3
    o3 = get_valid_slot_levels(f["rarity"], s_tuples, [f["slot_1"], f["slot_2"]]) if slots_active else [0]
    if f["slot_3"] not in o3: f["slot_3"] = o3[0]
    
    v3 = c_sl3.selectbox(l3, o3, index=o3.index(f["slot_3"]), disabled=not slots_active or (len(o3) <= 1 and o3[0] == 0 and f["slot_2"] == 0), key="s3_sel")
    if v3 != f["slot_3"]:
        f["slot_3"] = v3
        st.rerun()

    st.write("---")
    if st.button("この鑑定護石を登録する 💾", type="primary", use_container_width=True, disabled=not slots_active):
        final_slots = [f["slot_1"], f["slot_2"], f["slot_3"], 0] if f["rarity"] == 8 else [0, f["slot_1"], f["slot_2"], f["slot_3"]]
        skills_p = [{"name": f[f"s{i}_name"], "level": f[f"s{i}_level"]} for i in [1, 2, 3] if f[f"s{i}_name"] != "なし"]
        
        is_v, msg = validate_talisman(f["rarity"], skills_p, final_slots)
        if not is_v: st.error(f"整合性エラー: {msg}")
        else:
            nid = add_talisman(f["rarity"], skills_p, final_slots)
            if nid:
                st.toast("登録完了！", icon="✅")
                f["rarity"] = None; reset_from_rarity(); st.rerun()
            else: st.error("保存失敗")

st.divider()

# List
st.subheader("所持護石一覧")
df = load_talismans()
if not df.empty:
    df = df.sort_values(by=["rarity", "is_favorite"], ascending=[False, False])
    for _, row in df.iterrows():
        s_txt = " / ".join([f"{row[f'skill_{i}_name']} Lv{row[f'skill_{i}_level']}" for i in [1,2,3] if pd.notna(row[f'skill_{i}_name']) and row[f'skill_{i}_name'] != ""])
        def sc(v, is_w=False):
            if pd.isna(v) or v == 0: return "ー"
            if is_w: return f"[{int(v)}]"
            return {1:"①", 2:"②", 3:"③", 4:"④"}.get(int(v), "ー")
        w_sl = sc(row.get('weapon_slot_level', 0), True) if row.get('weapon_slot_level', 0) > 0 else ""
        a_sl = "".join([sc(row.get(f'armor_slot_{i}_level', 0)) for i in [1,2,3]])
        sl_txt = f"Slot: {w_sl}{a_sl}"
        bg = "#e74c3c" if row['rarity'] == 8 else "#9b59b6" if row['rarity'] == 7 else "#3498db"
        badge = f'<div style="background:{bg}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; width:max-content;">R{row["rarity"]}</div>'
        
        c1, c2 = st.columns([12, 1], vertical_alignment="center")
        with c1: render_slim_card(badge, s_txt, sl_txt, "")
        with c2:
            with st.popover("⋮"):
                if st.button("⭐" if row.get('is_favorite', False) else "☆", key=f"f_{row['id']}", use_container_width=True):
                    toggle_talisman_fav(row['id']); st.rerun()
                if st.button("🗑️", key=f"d_{row['id']}", type="primary", use_container_width=True):
                    delete_talisman(row['id']); st.rerun()
else:
    st.info("登録済みの護石はありません。")
