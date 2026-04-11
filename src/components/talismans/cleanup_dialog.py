import streamlit as st
import pandas as pd
from src.logic.talismans import load_talismans, delete_talisman
from src.logic.talismans_analysis import find_redundant_talismans
from src.components.talismans.atoms import build_talisman_visual_info
from src.components.cards import render_slim_card

def cleanup_talismans_dialog(user_id: str):
    """
    重複・下位互換の護石を抽出し、整理するためのダイアログ。
    """
    @st.dialog("重複・下位互換の整理 (Cleanup)")
    def show_dialog():
        df = load_talismans(user_id)
        if df.empty:
            st.info("登録済みの護石はありません。")
            return

        redundants = find_redundant_talismans(df)
        
        if not redundants:
            st.success("重複や下位互換の護石は見つかりませんでした！")
            if st.button("閉じる", use_container_width=True):
                st.rerun()
            return

        st.warning(f"{len(redundants)} 件の整理候補が見つかりました。\nこれらは他の所持護石によって完全に代用可能です。")
        
        # Action all
        if st.button("全件削除", type="primary", use_container_width=True):
            success_count = 0
            for r in redundants:
                # Check for favorite as last resort protection
                if r['talisman'].get('is_favorite', False):
                    continue
                if delete_talisman(r['talisman']['id'], user_id=user_id):
                    success_count += 1
            st.success(f"{success_count} 件の護石を削除しました。")
            st.rerun()

        st.divider()

        for i, r in enumerate(redundants):
            t = r['talisman']
            is_fav = t.get('is_favorite', False)
            
            # Identify superior talisman info
            sup_ids = r.get('superior_ids', [])
            eq_ids = r.get('equivalent_ids', [])
            reason_text = "上位互換が存在します" if r['reason'] == "SUPERIOR" else "同等品が存在します"
            
            # Find the first superior/eq for display
            ref_t = None
            if sup_ids:
                ref_t = df[df['id'] == sup_ids[0]].iloc[0]
            elif eq_ids:
                ref_t = df[df['id'] == eq_ids[0]].iloc[0]

            with st.container(border=True):
                # Candidate Section
                st.caption("🗑️ 整理候補 (下位/重複)")
                skills, slots, badge = build_talisman_visual_info(pd.Series(t))
                render_slim_card(badge, skills, slots, "", mode="long-cleanup")
                
                # Visual Indicator
                if ref_t is not None:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: center; margin: 4px 0; color: #888; font-size: 0.8rem; gap: 8px;">
                            <div style="flex: 1; height: 1px; background: #333;"></div>
                            <span>▼ {reason_text} ▼</span>
                            <div style="flex: 1; height: 1px; background: #333;"></div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    # Superior Section
                    skills_s, slots_s, badge_s = build_talisman_visual_info(ref_t)
                    render_slim_card(badge_s, skills_s, slots_s, "", mode="long-cleanup")
                
                st.write("") # Spacer

                # Delete individual button
                if st.button(f"この護石を削除する {'(⭐お気に入りにつき保護中)' if is_fav else ''}", key=f"del_clean_{t['id']}", type="primary", use_container_width=True, disabled=is_fav):
                    if delete_talisman(t['id'], user_id=user_id):
                        st.rerun()
                
                if is_fav:
                    st.caption("⚠️ お気に入り登録されている護石を削除するには、一覧画面で解除が必要です。")
        
    show_dialog()
