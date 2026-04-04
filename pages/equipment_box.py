import streamlit as st
import pandas as pd
from src.logic.master import get_master_data
from src.logic.equipment_box import (
    load_equipment, register_equipment, delete_equipment, 
    validate_restoration_bonuses, get_weapon_label, format_bonus_summary, normalize_bonus,
    format_bonus_list, filter_equipment,
    ATTRIBUTE_COLORS
)
from src.logic.favorites import get_favorite_list, prepare_skill_choices

from src.components.sidebar import render_shared_sidebar

st.set_page_config(page_title="所有巨戟アーティア一覧", page_icon="📦", layout="wide")

# Render shared sidebar (also performs browser boot handshake)
render_shared_sidebar()

# Wait for localStorage data to be available
if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
    st.info("⏳ データを読み込み中...")
    st.stop()

st.title("所有巨戟アーティア一覧 📦")
st.markdown("巨戟アーティア武器のステータスやボーナス状況を詳細に管理します。")

st.divider()

st.subheader("新しい武器を登録")

master = get_master_data()
# Favorites for sorting
fav_series = get_favorite_list("series")
fav_groups = get_favorite_list("group")

sorted_series, series_skill_labels = prepare_skill_choices(master.get("series_skills", []), fav_series, "skill_parts")
sorted_groups, group_skill_labels = prepare_skill_choices(master.get("group_skills", []), fav_groups, "group_name")

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
        current_series = sorted_series[sel_s]["skill_parts"]
    with sc2:
        sel_g = st.selectbox("グループスキル", range(len(group_skill_labels)), format_func=lambda i: group_skill_labels[i])
        current_group = sorted_groups[sel_g]["group_name"]
        
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
        if r_type == "属性強化":
            if element == "無":
                continue
            if is_bow and element in ["毒", "麻痺", "睡眠", "爆破"]:
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
                st.toast(f"{final_weapon_name} を登録しました！", icon="✅")
                st.rerun()
            else:
                st.error("登録に失敗しました。")

st.divider()

# --- Search & Filter UI ---
st.subheader("検索とフィルタ 🔍")

with st.expander("🔎 条件を指定して絞り込む", expanded=False):
    f_c1, f_c2, f_c3 = st.columns(3)
    with f_c1:
        f_name = st.text_input("武器名で検索", placeholder="キーワード入力...")
        f_types = st.multiselect("武器種", master.get("weapon_types", []))
    with f_c2:
        f_elements = st.multiselect("属性", master.get("elements", []))
        f_enhancements = st.multiselect("巨戟強化", enhancement_opts)
    with f_c3:
        f_sort = st.selectbox("並び替え", ["武器種順", "属性順", "新着順"], index=0)

    sf_c1, sf_c2 = st.columns(2)
    with sf_c1:
        f_series = st.multiselect("シリーズスキル", [s['skill_parts'] for s in master.get("series_skills", []) if s['skill_parts'] != "なし"])
    with sf_c2:
        f_groups = st.multiselect("グループスキル", [g['group_name'] for g in master.get("group_skills", []) if g['group_name'] != "なし"])

    st.markdown("##### ボーナスによる絞り込み (順番不問 / 全て含むものにヒット)")
    b_c1, b_c2 = st.columns(2)
    with b_c1:
        # Get unique production bonuses from master
        f_pbs = st.multiselect("生産ボーナス", p_bonus_opts)
    with b_c2:
        # Build dynamic list of restoration bonuses for filtering
        f_rbs_opts = []
        for rt, lvs in master.get("restoration_bonuses", {}).items():
            if rt == "なし": continue
            for lv in lvs:
                f_rbs_opts.append(rt if lv == "無印" else f"{rt} [{lv}]")
        f_rbs = st.multiselect("復元ボーナス", f_rbs_opts)

st.subheader("所持武器一覧")

# Load and Filter
df_raw = load_equipment()
df = filter_equipment(
    df_raw, 
    search_name=f_name,
    weapon_types=f_types,
    elements=f_elements,
    series_skills=f_series,
    group_skills=f_groups,
    enhancements=f_enhancements,
    p_bonuses=f_pbs,
    r_bonuses=f_rbs,
    sort_by=f_sort
)

# Badge CSS helper (Upgraded for slim design)
def get_badge_html(text, bgcolor="#444", color="white"):
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 1px 6px; border-radius: 3px; font-size: 0.75em; font-weight: bold; display: inline-block; min-width: 35px; text-align: center; margin-right: 8px;">{text}</span>'

if df.empty:
    st.info("条件に一致する武器がありません。")
else:
    # Use custom HTML for slim design
    st.markdown("""
        <style>
        .slim-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 6px;
            margin-bottom: 6px;
            gap: 12px;
        }
        .slim-main {
            display: flex;
            align-items: center;
            flex-grow: 1;
            min-width: 0;
        }
        .slim-info {
            display: flex;
            flex-direction: column;
            min-width: 0;
            flex-grow: 1;
        }
        .slim-title {
            font-weight: bold;
            font-size: 0.95em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .slim-sub {
            font-size: 0.75em;
            color: #888;
            margin-top: 2px;
        }
        .slim-bonus {
            font-size: 0.75em;
            background: #2a2a2a;
            padding: 2px 8px;
            border-radius: 4px;
            color: #ccc;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 350px;
        }
        .slim-actions {
            display: flex;
            gap: 4px;
        }
        @media (max-width: 600px) {
            .slim-card {
                flex-wrap: wrap;
                padding: 10px;
            }
            .slim-bonus {
                max-width: 100%;
                margin-top: 4px;
                width: 100%;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    for index, row in df.iterrows():
        # Get details
        elem = row['element']
        bg = ATTRIBUTE_COLORS.get(elem, "#444")
        txt_c = "black" if elem in ["氷", "雷", "無", "睡眠"] else "white"
        badge_html = get_badge_html(elem, bgcolor=bg, color=txt_c)
        
        display_name = row['weapon_name']
        is_named = display_name and not display_name.startswith("無銘の")
        title_text = display_name if is_named else row['weapon_type']
        
        enh = row['enhancement_type']
        series = row['current_series_skill']
        group = row['current_group_skill']
        
        # Summary of bonuses
        pbs = [row.get(f'p_bonus_{i}', 'なし') for i in range(1,4)]
        rbs_with_lv = []
        for i in range(1, 6):
            rt = row.get(f'rest_{i}_type', 'なし')
            rl = row.get(f'rest_{i}_level', 'なし')
            if rt != 'なし':
                suffix = rl if rl and rl != "無印" else ""
                rbs_with_lv.append(f"{rt}{suffix}")
        
        bonus_html = f"🛠️ {format_bonus_summary(pbs)} / ✨ {format_bonus_summary(rbs_with_lv)}"
        
        # Action columns
        c_left, c_right = st.columns([9, 1], vertical_alignment="center")
        
        with c_left:
            card_html = f"""
            <div class="slim-card">
                <div class="slim-main">
                    {badge_html}
                    <div class="slim-info">
                        <div class="slim-title">{title_text} <span style="font-weight: normal; color: #666; font-size: 0.8em;">({row['weapon_type']})</span></div>
                        <div class="slim-sub">📋 {enh} | 🛡️ {series} | 👥 {group}</div>
                    </div>
                </div>
                <div class="slim-bonus" title="{bonus_html}">{bonus_html}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
        with c_right:
            # We still need dedicated Streamlit buttons for actions (rerun/switch)
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.button("🎯", key=f"tr_{row['id']}", help="この武器の強化登録へ"):
                st.session_state.tracker_reg_w_id = row['id']
                st.switch_page("pages/reinforcement_registration.py")
            if btn_col2.button("🗑️", key=f"del_{row['id']}"):
                if delete_equipment(row['id']):
                    st.rerun()
