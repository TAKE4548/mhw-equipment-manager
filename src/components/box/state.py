import streamlit as st

def init_box_state():
    """装備ボックスページの Session State を確認・初期化する"""
    if "tracker_reg_w_id" not in st.session_state:
        st.session_state["tracker_reg_w_id"] = None
    
    # 必要に応じて他の初期状態をここに追加可能

def check_data_ready():
    """localStorage からのデータ読み込みが完了しているか確認する"""
    if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
        st.info("⏳ データを読み込み中...")
        st.stop()
        return False
    return True
