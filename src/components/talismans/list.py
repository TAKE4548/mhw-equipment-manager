import streamlit as st
import pandas as pd
from src.logic.talismans import (
    load_talismans, toggle_favorite as toggle_talisman_fav,
    delete_talisman, get_all_skills_flat, filter_and_sort_talismans
)
from src.components.common import render_item_count
from src.components.cards import render_slim_card, CARD_ACTION_RATIO
from src.components.talismans.atoms import build_talisman_visual_info
from src.components.talismans.dialogs import edit_talisman_dialog

@st.fragment
def render_talisman_list(user_id):
    """護石の一覧表示とフィルタUIを描画する (Fragment化)"""
    df = load_talismans(user_id)
    if df.empty:
        st.info("登録済みの護石はありません。")
        return

    # --- Filter & Sort UI ---
    with st.expander("🔎 所持護石を絞り込む・並べ替え", expanded=False):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.multiselect("レア度", [5, 6, 7, 8], key="f_rarity")
        with c2:
            all_skills = get_all_skills_flat()
            st.multiselect("スキル (いずれかを含む)", all_skills, key="f_skills")
        
        st.write("最低スロットレベル:")
        s1, s2, s3, s4 = st.columns(4)
        slot_opts = [0, 1, 2, 3, 4]
        s1.selectbox("武器", slot_opts, key="f_slot_w")
        s2.selectbox("防具①", slot_opts, key="f_slot_a1")
        s3.selectbox("防具②", slot_opts, key="f_slot_a2")
        s4.selectbox("防具③", slot_opts, key="f_slot_a3")
        
        st.checkbox("お気に入りのみ表示", key="f_fav_only")
        sort_opts = ["登録順 (新しい順)", "登録順 (古い順)", "レア度 (高→低)", "レア度 (低→高)", "スキル名順"]
        st.selectbox("並べ替え", sort_opts, key="f_sort_by")

    # --- Applying Filter & Sort ---
    df = filter_and_sort_talismans(
        df,
        rarity=st.session_state["f_rarity"],
        skills=st.session_state["f_skills"],
        slot_w_min=st.session_state["f_slot_w"],
        slot_a1_min=st.session_state["f_slot_a1"],
        slot_a2_min=st.session_state["f_slot_a2"],
        slot_a3_min=st.session_state["f_slot_a3"],
        fav_only=st.session_state["f_fav_only"],
        sort_by=st.session_state["f_sort_by"]
    )

    if df.empty:
        st.warning("条件に一致する護石が見つかりませんでした。")
        return

    # --- Main Results Grid ---
    render_item_count(len(df))
    
    with st.container():

        # Pre-calculate visual info using atom component
        results = df.apply(build_talisman_visual_info, axis=1)
        df['disp_skill'], df['disp_slot'], df['disp_badge'] = zip(*results)

        for _, row in df.iterrows():
            col_card, col_act = st.columns(CARD_ACTION_RATIO, vertical_alignment="center")
            with col_card:
                render_slim_card(row['disp_badge'], row['disp_skill'], row['disp_slot'], "", mode="long-text")
            with col_act:
                with st.popover("⋮", key=f"pop_t_{row['id']}"):
                    if st.button("⭐" if row.get('is_favorite', False) else "☆", key=f"f_{row['id']}", use_container_width=True):
                        toggle_talisman_fav(row['id'], user_id=user_id)
                        st.rerun()
                    if st.button("✏️", key=f"e_{row['id']}", use_container_width=True):
                        edit_talisman_dialog(row['id'], user_id)
                    if st.button("🗑️", key=f"d_{row['id']}", type="primary", use_container_width=True):
                        delete_talisman(row['id'], user_id=user_id)
                        st.rerun()
