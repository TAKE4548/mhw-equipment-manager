import streamlit as st
import pandas as pd
import altair as alt
from src.logic.equipment_box import load_equipment, ATTRIBUTE_COLORS
from src.components.sidebar import render_shared_sidebar
from src.logic.master import get_master_data

st.set_page_config(page_title="分析ダッシュボード", page_icon="📊", layout="wide")

# Sidebar & Handshake
render_shared_sidebar()

if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
    st.info("⏳ データを読み込み中...")
    st.stop()

st.title("所有アーティア分析ダッシュボード 📊")
st.markdown("所持している武器の傾向を統計的に分析し、今後の厳選の参考にします。")

df_raw = load_equipment()

if df_raw.empty:
    st.warning("分析するデータがありません。武器を登録してください。")
    st.stop()

master = get_master_data()

st.divider()

# --- Section 1: Overall Summary (Pie Chart) ---
st.subheader("⚔️ 武器種別シェア (所持数・比率)")

# Calculate counts and percentages
w_counts = df_raw['weapon_type'].value_counts().reset_index()
w_counts.columns = ['武器種', '本数']
total_weapons = len(df_raw)
w_counts['割合'] = (w_counts['本数'] / total_weapons * 100).round(1)

# Pie chart using Altair (Legend-based to prevent overlap)
base = alt.Chart(w_counts).encode(
    theta=alt.Theta("本数:Q", stack=True),
    color=alt.Color(
        "武器種:N", 
        scale=alt.Scale(scheme='tableau20'), 
        legend=alt.Legend(
            title="武器種 (本数 / 割合)",
            labelLimit=250, # Ensure long labels don't cut off
            orient='right'
        ),
        sort=alt.SortField("本数", order="descending")
    ),
    order=alt.Order("本数:Q", sort='descending'),
    tooltip=['武器種', '本数', alt.Tooltip('割合', format='.1f', title='割合(%)')]
)

# Legend text customization via dummy column or just tooltips. 
# For standard legend, we'll use '武器種' as is, 
# but for premium feel, let's create a display label.

w_counts['表示ラベル'] = w_counts.apply(lambda r: f"{r['武器種']}: {r['本数']}本 ({r['割合']}%)", axis=1)

# Re-define chart with better legend
base = alt.Chart(w_counts).encode(
    theta=alt.Theta("本数:Q", stack=True),
    color=alt.Color(
        "表示ラベル:N", 
        scale=alt.Scale(scheme='tableau20'), 
        sort=alt.SortField("本数", order="descending"),
        legend=alt.Legend(
            title="武器種内訳", 
            labelLimit=500,     # Expand for clarity
            labelFontSize=15,    # Larger font
            titleFontSize=18,    # Even larger title
            symbolSize=150,      # Much larger color symbols
            orient='right'
        )
    ),
    order=alt.Order("本数:Q", sort='descending'),
    tooltip=['武器種', '本数', alt.Tooltip('割合', format='.1f', title='割合(%)')]
)

pie = base.mark_arc(outerRadius=160, innerRadius=0)
chart = pie.properties(width=700, height=500)
st.altair_chart(chart, use_container_width=True)

st.markdown(f"**総所持数:** `{total_weapons}` 本")

st.divider()

# --- Section 2: Drill-down Analysis ---
st.subheader("🔍 武器種別ドリルダウン")
c_f1, c_f2 = st.columns([1, 2])
with c_f1:
    selected_w_type = st.selectbox("分析対象の武器種を選択", ["全て"] + master.get("weapon_types", []))

# Filter data
if selected_w_type == "全て":
    df = df_raw
else:
    df = df_raw[df_raw['weapon_type'] == selected_w_type]

if df.empty:
    st.info(f"{selected_w_type} のデータはありません。")
else:
    # 2-column breakdown
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"**🔮 {selected_w_type} の属性内訳**")
        e_counts = df['element'].value_counts().reset_index()
        e_counts.columns = ['属性', '本数']
        
        # Sort by elements master order
        e_order = master.get("elements", [])
        e_counts['属性'] = pd.Categorical(e_counts['属性'], categories=e_order, ordered=True)
        e_counts = e_counts.sort_values('属性')
        
        # Build color mapping for chart
        color_domain = [e for e in e_order if e in e_counts['属性'].unique()]
        color_range = [ATTRIBUTE_COLORS.get(e, "#444") for e in color_domain]
        
        e_chart = alt.Chart(e_counts).mark_bar().encode(
            x=alt.X('本数:Q', title="所有数"),
            y=alt.Y('属性:N', sort=None, title=None),
            color=alt.Color('属性:N', scale=alt.Scale(domain=color_domain, range=color_range), legend=None),
            tooltip=['属性', '本数']
        ).properties(height=300)
        st.altair_chart(e_chart, use_container_width=True)

    with col_right:
        st.markdown(f"**🛡️ {selected_w_type} のシリーズスキル内訳**")
        s_counts = df['current_series_skill'].value_counts().reset_index()
        s_counts.columns = ['スキル', '本数']
        s_chart = alt.Chart(s_counts.head(10)).mark_bar(color="#4d90fe").encode(
            x=alt.X('本数:Q', title="所有数"),
            y=alt.Y('スキル:N', sort='-x', title=None),
            tooltip=['スキル', '本数']
        ).properties(height=300)
        st.altair_chart(s_chart, use_container_width=True)

    st.markdown(f"**👥 {selected_w_type} のグループスキル内訳**")
    g_counts = df['current_group_skill'].value_counts().reset_index()
    g_counts.columns = ['グループスキル', '本数']
    g_chart = alt.Chart(g_counts.head(10)).mark_bar(color="#27ae60").encode(
        x=alt.X('本数:Q', title="所有数"),
        y=alt.Y('グループスキル:N', sort='-x', title=None),
        tooltip=['グループスキル', '本数']
    ).properties(height=200)
    st.altair_chart(g_chart, use_container_width=True)

st.divider()

# --- Raw Data Export ---
with st.expander("📥 データのダウンロード"):
    csv = df_raw.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "CSV形式でダウンロード",
        csv,
        "mhw_equipment_data.csv",
        "text/csv",
        key='download-csv'
    )
