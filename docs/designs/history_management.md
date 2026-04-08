# 履歴管理システム設計 (History Management Design)

## 目的
アプリケーション全体で Undo/Redo (元に戻す/やり直し) 操作の一貫性を保証し、データ破損や予期せぬエラーを防止する。

## 設計原則

1. **Snapshot-based History**:
    - 履歴は「操作後のスナップショット」ではなく、「操作前後の DataFrame 全体」を保存する方式（Snapshot方式）に統一する。
    - これにより、個別の操作（追加、削除、更新）の逆操作ロジックを個別に実装する必要がなくなり、堅牢性が向上する。

2. **Logic Layer Responsibility (SSoT)**:
    - 履歴の記録 (`push_action`) は、データ更新を担当する `src/logic/*.py` 内の関数でのみ行う。
    - **UI 層 (`pages/`, `src/components/`) は履歴の記録を一切行わない。** UI 層は単にロジック関数を呼び出し、成功/失敗のフィードバックのみに集中する。

3. **In-Memory Session State**:
    - `undo_stack` および `redo_stack` は `streamlit.session_state` で管理する。
    - 各スタックの最大保持数は 20 件とする。

## データ構造

履歴スタックに保存される各アイテムは以下の形式を遵守する：

```python
{
    'action_type': str,  # デバッグおよび通知用ラベル (例: "ADD_EQUIPMENT")
    'table': str,        # 更新対象のテーブル名 (例: "weapons")
    'prev_df': pd.DataFrame, # 操作前のデータスナップショット
    'next_df': pd.DataFrame  # 操作後のデータスナップショット
}
```

## 実装ガイドライン

### ロジック層の実装パターン
データを変更するすべての関数は以下のパターンに従う：

```python
def modify_data(..., user_id="local"):
    df = load_data()
    prev_df = df.copy() # 変更前のスナップショット
    
    # ... データの変更処理 (df を更新) ...
    
    if save_data(TABLE_NAME, df):
        clear_cache()
        push_action("ACTION_LABEL", TABLE_NAME, prev_df, df)
        return True
    return False
```

### UI層の実装パターン
UI は履歴を意識せず、単に関数を呼び出し、必要に応じて `st.rerun()` を行う。

```python
# GOOD
if st.button("削除"):
    if delete_logic(id):
        st.toast("削除しました")
        st.rerun()

# BAD (直接スタックを操作しない)
if st.button("削除"):
    st.session_state['undo_stack'].append(...) 
    delete_logic(id)
```

## 適用対象

### 優先対応 (整合性修正)
- `pages/0_skill_lottery.py` (手動スタック操作の削除)
- `src/components/tables.py` (手動スタック操作の削除)
- `src/logic/equipment.py` (既存の push_action の維持と確認)

### 新規適用
- `src/logic/favorites.py` (お気に入り操作の履歴対応)
- `src/logic/equipment_box.py` (一部関数の push_action 確認)

## 例外
- 「お気に入りの切り替え」や「フィルタ設定」など、アプリケーションの主データに影響を与えないUI状態の変更は、履歴管理の対象外とする場合がある（現状の `toggle_favorite` 等）。
