import streamlit as st
import pandas as pd
from src.logic.talismans import (
    load_talismans, update_talisman, validate_talisman, 
    get_valid_skill_names, get_valid_levels_for_skill
)
from src.logic.favorites import get_favorite_list, add_favorite, remove_favorite
from src.components.talismans.state import (
    reset_from_s1, reset_from_s2, reset_from_s3
)

@st.dialog("🎯 スキル選択")
def skill_dialog_root(key: str):
    f = st.session_state["r_form"]
    rarity = f["rarity"]
    idx = int(key[1])
    
    # Calculate phase
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
            st.session_state["active_dialog"] = None 
            st.rerun()
            
        st.divider()
        for n in sorted_names:
            c1, c2 = st.columns([5, 1])
            with c1:
                if st.button(n, key=f"sel_n_{n}_{key}", use_container_width=True):
                    lvls = get_valid_levels_for_skill(rarity, prev, n)
                    if len(lvls) == 1:
                        f[f"{key}_name"] = n; f[f"{key}_level"] = lvls[0]
                        if key == "s1": reset_from_s1()
                        elif key == "s2": reset_from_s2()
                        elif key == "s3": reset_from_s3()
                        st.session_state["active_dialog"] = None
                        if f"dialog_phase_{key}" in st.session_state: del st.session_state[f"dialog_phase_{key}"]
                        st.rerun()
                    else:
                        st.session_state[f"temp_name_{key}"] = n
                        st.session_state[f"dialog_phase_{key}"] = "level"
                        st.rerun()
            with c2:
                is_f = n in favs
                if st.button("⭐" if is_f else "☆", key=f"fav_n_{n}_{key}", use_container_width=True):
                    if is_f: remove_favorite("talisman_skill", n)
                    else: add_favorite("talisman_skill", n)
                    st.rerun()
    
    elif phase == "level":
        n = st.session_state[f"temp_name_{key}"]
        st.subheader(f"2. レベルを選択 ({n})")
        lvls = get_valid_levels_for_skill(rarity, prev, n)
        
        if st.button("⬅️ 名前を選び直す", use_container_width=True):
            st.session_state[f"dialog_phase_{key}"] = "name"
            st.rerun()
            
        st.divider()
        for l in lvls:
            if st.button(f"Lv{l}", key=f"btn_l_{l}_{key}", use_container_width=True):
                f[f"{key}_name"] = n; f[f"{key}_level"] = l
                if key == "s1": reset_from_s1()
                elif key == "s2": reset_from_s2()
                elif key == "s3": reset_from_s3()
                st.session_state["active_dialog"] = None
                if f"dialog_phase_{key}" in st.session_state: del st.session_state[f"dialog_phase_{key}"]
                st.rerun()

@st.dialog("✏️ 護石を編集")
def edit_talisman_dialog(talisman_id: str, user_id: str):
    df = load_talismans(user_id)
    target = df[df["id"] == talisman_id]
    if target.empty:
        st.error("エラー: 対象の護石が見つかりませんでした。")
        return
    
    row = target.iloc[0]
    
    if "edit_form" not in st.session_state or st.session_state.get("edit_target_id") != talisman_id:
        st.session_state["edit_target_id"] = talisman_id
        st.session_state["edit_form"] = {
            "rarity": int(row["rarity"]),
            "s1_name": row["skill_1_name"] if pd.notna(row["skill_1_name"]) and row["skill_1_name"] != "" else "なし",
            "s1_level": int(row["skill_1_level"]),
            "s2_name": row["skill_2_name"] if pd.notna(row["skill_2_name"]) and row["skill_2_name"] != "" else "なし",
            "s2_level": int(row["skill_2_level"]),
            "s3_name": row["skill_3_name"] if pd.notna(row["skill_3_name"]) and row["skill_3_name"] != "" else "なし",
            "s3_level": int(row["skill_3_level"]),
            "slot_1": int(row["weapon_slot_level"]) if int(row["rarity"]) == 8 else int(row["armor_slot_1_level"]),
            "slot_2": int(row["armor_slot_1_level"]) if int(row["rarity"]) == 8 else int(row["armor_slot_2_level"]),
            "slot_3": int(row["armor_slot_2_level"]) if int(row["rarity"]) == 8 else int(row["armor_slot_3_level"]),
        }

    ef = st.session_state["edit_form"]
    st.markdown(f"レア度 **R{ef['rarity']}** の護石を編集しています。")
    st.info("※編集モードではスキルの組み合わせ整合性チェックのみ行われます。構成を根本から変える場合は再登録を推奨します。")
    
    st.write(f"第1: {ef['s1_name']} {ef['s1_level']} / 第2: {ef['s2_name']} {ef['s2_level']} / 第3: {ef['s3_name']} {ef['s3_level']}")
    st.write(f"スロット: {ef['slot_1']} - {ef['slot_2']} - {ef['slot_3']}")

    if st.button("更新を保存 💾", type="primary", use_container_width=True):
        final_slots = [ef["slot_1"], ef["slot_2"], ef["slot_3"], 0] if ef["rarity"] == 8 else [0, ef["slot_1"], ef["slot_2"], ef["slot_3"]]
        skills_p = [{"name": ef[f"s{i}_name"], "level": ef[f"s{i}_level"]} for i in [1, 2, 3] if ef[f"s{i}_name"] != "なし"]
        
        is_v, msg = validate_talisman(ef["rarity"], skills_p, final_slots)
        if not is_v:
            st.error(f"整合性エラー: {msg}")
        else:
            try:
                if update_talisman(talisman_id, ef["rarity"], skills_p, final_slots, user_id=user_id):
                    st.toast("更新しました！")
                    st.rerun()
                else:
                    st.error("保存に失敗しました。")
            except Exception as e:
                st.error(f"更新失敗: {str(e)}")
