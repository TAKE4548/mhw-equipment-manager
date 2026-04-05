# Performance Audit Summary: MHWs Equipment Manager

## 1. Global Bottlenecks (共通の課題)

### 🚨 Redundant Disk I/O (ディスクアクセスの重複)
- **`src/logic/master.py:get_master_data()`**
    - 概要: あらゆるページで使用される `master_data.json` を呼び出しのたびにディスクから読み込んでいます。
    - 影響: 全ページ。入力やクリックのたびに I/O が走り、全体的なもっさり感の原因になっています。

### 🚨 Uncached Heavy Calculations (重い計算処理の未キャッシュ)
- **`src/logic/equipment_box.py:get_abbr_item()`**
    - 概要: 正規表現や文字列置換を含む略称変換を、キャッシュなしでループ実行しています。
    - 影響: 「強化厳選」「装備BOX」などの一覧表示。1行あたり10回以上呼ばれるため、件数が増えると指数関数的に重くなります。

### 🚨 Broad Redraw Scope (再描画範囲の広すぎ)
- **All Pages (Registration Form vs Active List)**
    - 概要: 登録フォームと一覧リストが同一の描画スコープにあるため、フォームへの1文字入力ごとに重いリスト全体の再計算が発生しています。
    - 影響: 入力時のラグ。特にスキル抽選や強化厳選での操作感に直結しています。

---

## 2. Page-Specific Issues (ページ別の課題)

### 🏹 スキル抽選結果 (`0_skill_lottery.py` / `tables.py`)
- **Nested I/O**: `render_active_upgrades` 内のループから `load_equipment()` が間接的に呼ばれており、行数分の DB ロードが発生する可能性があります。
- **Rebuilt Maps**: スキル名変換用のマッピング辞書をループのたびにインメモリで再構築しています。

### ✨ 復元強化厳選 (`reinforcement_registration.py`)
- **Inefficient Merge**: 描画の直前に `tracker_df.merge(eq_df, ...)` を毎回実行しており、データ量が増えるとコストが無視できなくなります。
- **Loop Complexity**: `build_visual_comparison` 内での HTML 生成と略称変換の組み合わせがボトルネックです。

### 📦 所持武器一覧 (`equipment_box.py`)
- **Aggressive Filtering**: 複雑な正規化とフィルタリングロジックが、UIのわずかな変更（サイドバーの開閉など）でもすべて再実行されています。

---

## 3. Recommended Optimization Strategy (推奨される改善策)

1. **Caching (Logic Layer)**:
    - `get_master_data`, `load_equipment`, `load_trackers` へ `@st.cache_data` を適用。
    - `get_abbr_item` へ `lru_cache` を適用。
2. **Isolation (UI Layer)**:
    - 各一覧リストを `st.fragment` で包み、フォーム操作から隔離。
3. **Execution (Refactoring)**:
    - ループ内での `load_data` 呼び出しを、ループ前の「一括ロード」に変更。
