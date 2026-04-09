import streamlit as st

def init_talisman_state():
    """鑑定護石管理ページの Session State を初期化する"""
    if "r_form" not in st.session_state:
        st.session_state["r_form"] = {
            "rarity": None,
            "s1_name": "なし", "s1_level": 0,
            "s2_name": "なし", "s2_level": 0,
            "s3_name": "なし", "s3_level": 0,
            "slot_1": 0, "slot_2": 0, "slot_3": 0
        }

    if "t_filter" not in st.session_state:
        st.session_state["t_filter"] = {
            "rarity": [],
            "skills": [],
            "slot_w": 0, "slot_a1": 0, "slot_a2": 0, "slot_a3": 0,
            "fav_only": False,
            "sort_by": "登録順 (新しい順)"
        }
    
    # Sync individual keys for 1-click filter response (REQ-070)
    for k, v in st.session_state["t_filter"].items():
        if f"f_{k}" not in st.session_state:
            st.session_state[f"f_{k}"] = v

    if "active_dialog" not in st.session_state:
        st.session_state["active_dialog"] = None

# --- Forced Reset Helpers ---
# これらは AI が「リセットの連鎖」を追いやすくするため、state.py に集約します。

def reset_from_rarity():
    st.session_state["r_form"]["s1_name"] = "なし"
    st.session_state["r_form"]["s1_level"] = 0
    reset_from_s1()

def reset_from_s1():
    st.session_state["r_form"]["s2_name"] = "なし"
    st.session_state["r_form"]["s2_level"] = 0
    reset_from_s2()

def reset_from_s2():
    st.session_state["r_form"]["s3_name"] = "なし"
    st.session_state["r_form"]["s3_level"] = 0
    reset_from_s3()

def reset_from_s3():
    st.session_state["r_form"]["slot_1"] = 0
    reset_from_slot1()

def reset_from_slot1():
    st.session_state["r_form"]["slot_2"] = 0
    reset_from_slot2()

def reset_from_slot2():
    st.session_state["r_form"]["slot_3"] = 0
