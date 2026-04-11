import streamlit as st
from src.logic.talismans import (
    add_talisman, validate_talisman, get_valid_slot_levels
)
from src.components.talismans.state import (
    reset_from_rarity, reset_from_slot1, reset_from_slot2
)

@st.fragment
def render_registration_form(user_id):
    """鑑定護石の登録フォームを描画する (Fragment化により高速化)"""
    with st.expander("➕ 新しい鑑定護石を登録する", expanded=False):
        f = st.session_state["r_form"]
        
        # Rarity Selection
        opts = [None, 5, 6, 7, 8]
        idx = opts.index(f["rarity"]) if f["rarity"] in opts else 0
        new_r = st.selectbox("レア度", opts, index=idx, format_func=lambda x: str(x) if x is not None else "選択してください", key="t_reg_rarity")
        if new_r != f["rarity"]:
            f["rarity"] = new_r
            reset_from_rarity()
            st.rerun()
            
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

        # Slots Configuration
        s_tuples = []
        for i in range(1, 4):
            if f[f"s{i}_name"] != "なし": s_tuples.append((f[f"s{i}_name"], f[f"s{i}_level"]))
        
        slots_active = (f["rarity"] is not None) and (len(s_tuples) > 0)
        
        c_sl1, c_sl2, c_sl3 = st.columns(3)
        l1 = "武器" if f["rarity"] == 8 else "防具①"
        l2 = "防具①" if f["rarity"] == 8 else "防具②"
        l3 = "防具②" if f["rarity"] == 8 else "防具③"

        # Slot 1
        o1 = get_valid_slot_levels(f["rarity"], s_tuples, []) if slots_active else [0]
        if f["slot_1"] not in o1: f["slot_1"] = o1[0]; reset_from_slot1()
        v1 = c_sl1.selectbox(l1, o1, index=o1.index(f["slot_1"]), disabled=not slots_active, key="s1_sel_t")
        if v1 != f["slot_1"]:
            f["slot_1"] = v1
            reset_from_slot1()
            st.rerun()
            
        # Slot 2
        o2 = get_valid_slot_levels(f["rarity"], s_tuples, [f["slot_1"]]) if slots_active else [0]
        if f["slot_2"] not in o2: f["slot_2"] = o2[0]; reset_from_slot2()
        v2 = c_sl2.selectbox(l2, o2, index=o2.index(f["slot_2"]), disabled=not slots_active or (len(o2) <= 1 and o2[0] == 0 and f["slot_1"] == 0), key="s2_sel_t")
        if v2 != f["slot_2"]:
            f["slot_2"] = v2
            reset_from_slot2()
            st.rerun()

        # Slot 3
        o3 = get_valid_slot_levels(f["rarity"], s_tuples, [f["slot_1"], f["slot_2"]]) if slots_active else [0]
        if f["slot_3"] not in o3: f["slot_3"] = o3[0]
        v3 = c_sl3.selectbox(l3, o3, index=o3.index(f["slot_3"]), disabled=not slots_active or (len(o3) <= 1 and o3[0] == 0 and f["slot_2"] == 0), key="s3_sel_t")
        if v3 != f["slot_3"]:
            f["slot_3"] = v3
            st.rerun()

        st.write("---")
        if st.button("この鑑定護石を登録する 💾", type="primary", use_container_width=True, disabled=not slots_active, key="btn_reg_t"):
            final_slots = [f["slot_1"], f["slot_2"], f["slot_3"], 0] if f["rarity"] == 8 else [0, f["slot_1"], f["slot_2"], f["slot_3"]]
            skills_p = [{"name": f[f"s{i}_name"], "level": f[f"s{i}_level"]} for i in [1, 2, 3] if f[f"s{i}_name"] != "なし"]
            
            is_v, msg = validate_talisman(f["rarity"], skills_p, final_slots)
            if not is_v: st.error(f"整合性エラー: {msg}")
            else:
                try:
                    nid = add_talisman(f["rarity"], skills_p, final_slots, user_id=user_id)
                    if nid:
                        st.toast("登録完了！", icon="✅")
                        f["rarity"] = None; reset_from_rarity(); st.rerun()
                    else: st.error("保存失敗")
                except Exception as e:
                    st.error(f"保存失敗: {str(e)}")
