# Design: REQ-028 リストアイテム間の表示間隔の安定化と制約回避

## 1. 目的と背景
現状、リストカード間の余白（8px）は `:has` セレクタを用いたマージン制御に依存しており、以下の課題がある：
- **表示の不安定さ**: 見えないマーカー要素（`st.markdown`）が Streamlit の垂直ブロック内に新たな子要素として追加され、意図しない 2 重、3 重のギャップが発生している。
- **ブラウザ互換性**: モダンブラウザ以外での `:has` セレクタの動作不安。
- **保守性**: Streamlit の内部構造（`data-testid` の入れ子構造）への依存度が高すぎる。

本設計では、Streamlit のネイティブなレイアウト機構（Vertical Block Gap）を最大限活用し、CSS ハックなしで堅牢かつ一貫した 8px 間隔を実現する。

## 2. アーキテクチャ設計

### 2.1 垂直間隔の制御 (Global Vertical Flow)
Streamlit の `.stVerticalBlock` (または `[data-testid="stVerticalBlock"]`) の `gap` プロパティをグローバルに **8px (0.5rem)** に統一する。
これにより：
- 全てのウィジェット、コンテナ間の基本距離が 8px に固定される。
- マージンによる個別調整が不要になり、リストの密度が完璧に保たれる。
- 隙間を増やしたい場合は、従来通り `render_v_spacer` 等で明示的に調整可能。

### 2.2 マーカースタックの解消
現在 `render_selectable_card` 等で行っているマーカー用の `st.markdown` 出力を廃止する。
- 理由: `st.markdown` 自体が `stVerticalBlock` 内の一つのウィジェットとして扱われ、その前後に `gap` が発生するため、垂直方向の距離計算が複雑化する原因となっている。
- 対策: 必要最小限のクラス情報を本体の HTML 文字列に統合する。

### 2.3 選択状態のスタイリング (No-Has Selection)
`:has` を使わずに「選択されたカードに対応するボタン」を強調するため、Streamlit の `type="primary"` を活用する。

1. **Python 層**: 
   - `is_selected=True` の場合、`st.button(..., type="primary")` を使用する。
   - それ以外の場合は `type="secondary"` (デフォルト) を使用。
2. **CSS 層**:
   - `button[kind="primary"]` (およびホバー状態) を HUD 標準のゴールドカラー (`#f1c40f`) でオーバーライドする。

## 3. 修正方針 (具体例)

### src/components/cards.py

#### [MODIFY] `inject_card_css`
```css
/* グローバルな垂直間隔の定義 */
[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important; /* 8px 固定 */
}

/* 選択済みボタンの HUD スタイル適用 (no-has) */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #f1c40f !important;
    border: 1px solid #f1c40f !important;
    color: #000 !important;
}
```

#### [MODIFY] `render_selectable_card`
```python
def render_selectable_card(..., is_selected=False):
    # マーカーの st.markdown を削除 (ギャップの原因)
    
    # ボタンのタイプを動的に切り替え
    btn_type = "primary" if is_selected else "secondary"
    
    with st.container():
        c_tag, c_btn = st.columns(CARD_ACTION_RATIO, gap="small")
        with c_tag:
            # HTML 内に直接マーカークラスを埋め込む
            st.markdown(_render_v14_tag_body(..., is_selected=is_selected), unsafe_allow_html=True)
        with c_btn:
            clicked = st.button(icon, key=key, type=btn_type, use_container_width=True)
    return clicked
```
