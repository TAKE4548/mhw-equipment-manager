import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    load_equipment, register_equipment, delete_equipment, 
    validate_restoration_bonuses, get_weapon_label, format_bonus_summary, normalize_bonus,
    ATTRIBUTE_COLORS
)

def init_session_state():
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

st.set_page_config(page_title="Equipment Box", page_icon="📦", layout="wide")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the Home page sidebar.")
    st.stop()

st.title("Equipment Box 📦")
st.markdown("巨戟アーティア武器のステータスやボーナス状況を詳細に管理します。")
st.divider()

st.subheader("新しい武器を登録")

master = get_master_data()
series_skills_master = master.get("series_skills", [])
series_skill_labels = [f"{s['skill_parts']} ({s['skill_name']})" if s['skill_parts'] != "なし" else "なし" for s in series_skills_master]
group_skills_master = master.get("group_skills", [])
group_skill_labels = [f"{g['group_name']} ({g['skill_name']})" if g['group_name'] != "なし" else "なし" for g in group_skills_master]

p_bonus_opts = master.get("production_bonuses", [])
enhancement_opts = master.get("kyogeki_enhancements", [])

with st.expander("➕ 武器を新規登録する", expanded=False):
    st.markdown("##### 基本情報")
    weapon_name = st.text_input("武器の識別名 (任意)", placeholder="例: 火竜大剣用")
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        w_type = st.selectbox("Weapon Type", master.get("weapon_types", []))
    with c2:
        element = st.selectbox("Element", master.get("elements", []))
    with c3:
        enhancement = st.selectbox("巨戟強化種別", enhancement_opts)

    st.markdown("##### 付与されているスキル")
    sc1, sc2 = st.columns(2)
    with sc1:
        sel_s = st.selectbox("シリーズスキル", range(len(series_skill_labels)), format_func=lambda i: series_skill_labels[i])
        current_series = series_skills_master[sel_s]["skill_parts"]
    with sc2:
        sel_g = st.selectbox("グループスキル", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
        current_group = group_skills_master[sel_g]["group_name"]
        
    st.markdown("##### 生産ボーナス (必ず3枠設定)")
    pc1, pc2, pc3 = st.columns(3)
    with pc1: pb1 = st.selectbox("枠1", p_bonus_opts, key="pb1")
    with pc2: pb2 = st.selectbox("枠2", p_bonus_opts, key="pb2")
    with pc3: pb3 = st.selectbox("枠3", p_bonus_opts, key="pb3")
    
    # Dynamic Restoration Options based on Weapon Type
    is_bow = ("弓" in w_type and "ボウガン" not in w_type)
    is_bowgun = ("ボウガン" in w_type)
    
    dynamic_rest_options = ["なし"]
    for r_type, levels in master.get("restoration_bonuses", {}).items():
        if r_type == "なし": continue
        if r_type == "切れ味強化" and (is_bow or is_bowgun):
            continue
        if r_type == "装填強化" and not is_bowgun:
            continue
            
        for lv in levels:
            label = r_type if lv == "無印" else f"{r_type} [{lv}]"
            dynamic_rest_options.append(label)
            
    st.markdown("##### 復元ボーナス (最大5枠)")
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    with rc1: rb1 = st.selectbox("枠1", dynamic_rest_options, key="rb1")
    with rc2: rb2 = st.selectbox("枠2", dynamic_rest_options, key="rb2")
    with rc3: rb3 = st.selectbox("枠3", dynamic_rest_options, key="rb3")
    with rc4: rb4 = st.selectbox("枠4", dynamic_rest_options, key="rb4")
    with rc5: rb5 = st.selectbox("枠5", dynamic_rest_options, key="rb5")
    
    if st.button("武器を登録", type="primary"):
        # Auto-generate a name if none is provided
        final_weapon_name = weapon_name.strip() or f"無銘の{w_type}"
        
        # Parse Rest bonuses
        parsed_rbs = []
        for rb in [rb1, rb2, rb3, rb4, rb5]:
            if rb == "なし":
                parsed_rbs.append({"type": "なし", "level": "なし"})
            elif " [" in rb:
                parts = rb.split(" [")
                parsed_rbs.append({"type": parts[0], "level": parts[1][:-1]})
            else:
                # "無印" case
                parsed_rbs.append({"type": rb, "level": "無印"})
        
        is_valid, err_msg = validate_restoration_bonuses(parsed_rbs)
        if not is_valid:
            st.error(err_msg)
        else:
            record_id = register_equipment(
                final_weapon_name, w_type, element, 
                current_series, current_group, enhancement,
                [pb1, pb2, pb3], parsed_rbs
            )
            if record_id:
                st.success(f"{final_weapon_name} を登録しました！")
                st.rerun()
            else:
                st.error("登録に失敗しました。")

st.divider()
st.subheader("所持武器一覧")

df = load_equipment()

# Badge CSS helper
def get_badge_html(text, bgcolor="#444", color="white"):
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 2px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 8px; display: inline-block;">{text}</span>'

if df.empty:
    st.info("登録されている武器がありません。")
else:
    for index, row in df.iterrows():
        with st.container(border=True):
            # Header Row: [Badge] Weapon Name [Delete]
            h_col1, h_col2 = st.columns([7, 1])
            with h_col1:
                elem = row['element']
                bg = ATTRIBUTE_COLORS.get(elem, "#444")
                txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
                badge_html = get_badge_html(f"{row['weapon_type']} | {elem}", bgcolor=bg, color=txt_c)
                
                display_name = row['weapon_name']
                is_named = display_name and not display_name.startswith("無銘の")
                title_html = f"<span style='font-size: 1.15em; font-weight: bold;'>{display_name if is_named else row['weapon_type']}</span>"
                
                st.markdown(f"{badge_html} {title_html}", unsafe_allow_html=True)
            with h_col2:
                if st.button("削除🗑️", key=f"del_{row['id']}", use_container_width=True):
                    delete_equipment(row['id'])
                    st.rerun()
            
            # Info Row: Enhancement & Skills
            st.markdown(f"""
            <div style='margin: 8px 0; font-size: 0.9em; opacity: 0.9;'>
                <span title='巨戟強化'>📋 <b>{row['enhancement_type']}</b></span> &nbsp;&nbsp; | &nbsp;&nbsp; 
                <span title='シリーズスキル'>🛡️ {row['current_series_skill']}</span> &nbsp;&nbsp; | &nbsp;&nbsp; 
                <span title='グループスキル'>👥 {row['current_group_skill']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Bonus Box
            st.markdown("<div style='background-color: rgba(255,255,255,0.04); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                # Production
                pbs = [row.get(f'p_bonus_{i}', 'なし') for i in range(1,4)]
                st.markdown(f"<small>🛠️ <b>生産</b>: {format_bonus_summary(pbs)}</small>", unsafe_allow_html=True)
            with b_col2:
                # Restoration
                rbs_list = []
                for i in range(1, 6):
                    rt = row.get(f'rest_{i}_type', 'なし')
                    rl = row.get(f'rest_{i}_level', 'なし')
                    if rt != 'なし':
                        suffix = rl if rl and rl != "無印" else ""
                        rbs_list.append(f"{rt}{suffix}")
                st.markdown(f"<small>✨ <b>復元</b>: {format_bonus_summary(rbs_list)}</small>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
