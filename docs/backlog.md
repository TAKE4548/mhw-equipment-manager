# Project Backlog (MHW Equipment Manager)

## Status Definitions
- **new**: Intake complete. Goal refinement or AC is not yet finalized.
- **ready**: Deep-dive complete. Goal is clear, and AC is defined. Ready for `/dev`.
- **in-progress**: Under development in a `/dev` session.
- **fix-needed**: Defect detected. Needs prioritization for fixing.
- **needs-investigation**: Root cause unknown. Requires investigation.
- **done**: Implementation and Review complete.
- **archived**: Deferred or cancelled.

---
## Architecture Review Items
(Structural issues and technical debt recorded here. These are for `/arch-review`, not `/dev`.)

---
## Backlog Items

### REQ-001: 強化厳選 UI の改善 (武器選択ボタンのデザイン刷新)
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Description**: 復元ボーナスの強化厳選画面において、武器を選択するボタンのデザインが「ダサい」との指摘。現状の標準的な Streamlit ボタンから、よりプレミアムで直感的なデザインに変更する。
- **Problem**: 武器選択ボタンが単調で、アプリケーション全体のモダンなデザインから浮いてしまっている。
- **Acceptance Criteria**:
    - 武器選択 UI が視覚的に強化されている（カード全体がクリック可能、またはスタイリッシュな選択ボタン）。
    - 選択状態が明確に区別できる（ボーダーの発光、影の変化など）。
    - ホバーエフェクトなどのマイクロインタラクションが追加されている。

### REQ-002: 武器選択 UI のさらなる洗練 (CARD_ACTION_RATIO 方式への統合)
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Description**: 武器選択 UI を、v14 HUD デザインシステムに統合。
- **Problem**: 選択ボタンが独立した要素として配置されており、カードデザインとの一体感が欠如していた。
- **Decision (59b52e94)**: 完全なクリッカブルカードよりも、垂直同期と安定性を優先し、`CARD_ACTION_RATIO` (11.5:1) を用いた「同期型アクションボタン」を最終解として採用。
- **Acceptance Criteria**:
    - 武器カードとアクションボタン（❯/✔）が全ページで垂直に整列している。
    - 選択されたカードにゴールド発光ボーダーが適用されている。

### REQ-003: カード一覧の操作ボタン（⋮）とカードの水平位置揃え
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: P3
- **Description**: 一覧ページにおけるカードと右端の操作ボタンの垂直中央同期。
- **Decision (59b52e94)**: `CARD_ACTION_RATIO` による比率固定と、`vertical_alignment="center"` により、Streamlit の内部構造に左右されない視覚的な一致を達成。
- **Acceptance Criteria**:
    - 任意のリスト行で、カードと `⋮` ボタンの垂直中心線が視覚的に一致している。

### REQ-004: Undo/Redo 履歴管理の一貫性修正 (History Architecture Consistency)
- **Status**: done (2026-04-08)
- **Current Step**: none
- **Type**: bug
- **Priority**: high
- **Problem**: `0_skill_lottery.py` や `src/components/tables.py` で、共通の `push_action` ロジックを介さず Session State を直接操作しており、正常に Undo が動作しない、もしくはエラーになる可能性がある。
- **Acceptance Criteria**:
    - すべての履歴操作ポイントで `src.logic.history.push_action()` を使用する。
    - 各ページで Undo/Redo を実行し、データが正しく復元されることを確認する。

### REQ-005: 表示用語の統一 (レベル表記のローマ数字適用)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Problem**: `ui_spec.md` の規定（レベルはローマ数字 Ⅰ, Ⅱ, Ⅲ）に反し、登録フォームの選択肢等で算用数字 [1], [2], [3] が表示されたままになっている。
- **Acceptance Criteria**:
    - 復元ボーナスの選択肢ピッカーにおいて、常にローマ数字が表示されている。
    - 正規化関数 `normalize_bonus` が入力レイヤー（UI）で一貫して適用されている。

### REQ-006: フラグメント隔離の再評価 (Fragment Isolation Refinement)
- **Status**: new
- **Type**: maintenance
- **Priority**: low
- **Problem**: `0_skill_lottery.py` 等で、本来フラグメント内で完結すべき更新処理がページ全体の `st.rerun()` を誘発しており、パフォーマンス上のメリットが薄れている。
- **Acceptance Criteria**:
    - リスト更新等の操作が、可能な限りページ全体ではなくフラグメント単位の再描画で完結している。

### REQ-007: UI のスリム化と視覚的密度の最適化 (Lean UI Design)
- **Status**: done (2026-04-09)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Source**: "ページレイアウト的にややスリム差に欠ける気がしている。Undo/Redoのボタンデザインとかセパレータが多すぎる感じとか"
- **Problem**: 現状の UI は標準の Streamlit コンポーネント（特に st.divider や大きなボタン）を多用しており、情報の凝縮感に欠け、スクロール量や認知負荷が増大している。
- **Requirement**: `ui_spec.md` の "Lean Design 指針" に基づき、全ページのレイアウトを刷新する。
- **Acceptance criteria**:
    - Undo/Redo がタイトル横のコンパクトなツールバーに集約されている。
    - 不要な `st.divider()` が排除され、薄いボーダーや適切な余白による区切りに変更されている。
    - ウィジェット間の余白が CSS により最適化（圧縮）されている。
- **Design doc**: `docs/ui_spec.md`

### REQ-008: モンハン専用アイコンの導入と絵文字の排除
- **Status**: done (2026-04-10)
- **Type**: enhancement
- **Priority**: mid
- **Problem**: 現在、武器種や属性の表示に汎用の絵文字を使用しているため、ゲームの世界観と乖離しており、UIの質が損なわれている。
- **Requirement**: モンスターハンターのデザインに準拠した専用アイコン（武器、属性、スロット等）を用意し、アプリケーション全体で絵文字をこれに置き換える。
- **Acceptance Criteria**:
    - 全武器種の専用アイコンが正しく表示されること。
    - 属性および状態異常の専用アイコンが正しく表示されること。
    - 装飾品スロット（Lv1-4）の専用アイコンが正しく表示されること。
    - v14 HUD システムに統合され、色調やサイズが最適化されていること。
- **Note**: アイコンアセットは着手時にユーザーより提供される。こちらで必要アセットのたたき台（仕様策定含む）を作成する場合がある。UX デザイナーとの連携も視野に入れる。

### REQ-009: ページ構成とナビゲーションの再設計 (UX Consultation)
- **Status**: done (2026-04-09)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Source**: "Homeをダッシュボードにしているが、ダッシュボードの使い道がそこまで重要ではないので、ページナビゲーションなどどのようなページ構成が使いやすいかUXデザイナーと相談して設定したい。"
- **Problem**: 現在、Home (Dashboard) がアプリケーションの入り口となっているが、分析機能は定常的に使用するものではなく、目的の作業（登録・厳選）への即時アクセスを妨げている。また、ページが個別に並んでいるため、業務フローに沿った移動がしにくい。
- **Requirement**: ユーザーの主要なタスク（武器登録→抽選確認→厳選）に基づいた最適なページ構成とナビゲーションを再設計する。
- **Acceptance Criteria**:
    - 主要なワークフローに最適化されたページ階層（グルーピング）が定義されている。
    - Home 画面が「分析結果」ではなく、主要なアクションへの「ポータル（クイックアクセス）」として機能している。
    - ナビゲーションの順序やアイコンが直感的である。
### REQ-010: スキルシミュレーター機能および防具・装飾品データの管理機能の実装
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Source**: "スキルシミュレーター機能を追加したい。今はそもそも防具管理機能もないから、その追加も必要。"
- **Problem**: スキル構成を検討するためのシミュレーターがなく、また、その基礎となる防具や装飾品のデータ（マスタデータ）を管理する仕組みも未実装であるため、装備構成の検討に時間がかかる。
- **Requirement**: 
    1. 防具（頭・胴・腕・腰・脚）および装飾品のスキル・スロット・耐性等のマスタデータ管理機能（登録・編集）。
    2. ユーザーが指定したスキル構成を満たす装備の組み合わせを、マスタデータと所持護石から高速に検索・提示する機能。
- **Acceptance Criteria**:
    - 防具・装飾品の基礎データをシステムに登録し、属性やスキル情報を持たせることができる。
    - 検索条件として、複数のスキルとそれぞれの目標レベルを設定できる。
    - 登録済みの護石（Talisman）を検索対象に含めることができる。
    - 検索結果として、全部位の装備構成、発動スキル一覧、空きスロット、トータルステータスが分かりやすく表示される。
- **Note**: 実際の開発着手時に、マスタ管理（データ整備）と検索ロジック実装を個別のタスクに分割するか再検討する。

### REQ-011: スキル・ボーナスの高度な検索サポート (UX-03)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Description**: キーボード入力による選択を高速化。
- **Acceptance Criteria**:
    - セレクトボックスでのキーワード検索性が向上している（部分一致など）。
    - 可能であれば「ひらがな・カタカナ・ローマ字」での部分一致検索をサポートする。

### REQ-012: ボーナス種別のカラーコード表示 (UX-05)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Description**: ボーナスの種類を直感的に判別可能にする。
- **Acceptance Criteria**:
    - 攻撃、属性、切れ味などのカテゴリー別にカラーコードを割り当てる。
    - 具体的な配色は開発着手時に検討。

### REQ-013: 武器カード上でのダイレクトアクションの追加 (UX-08)
- **Status**: new
- **Type**: enhancement
- **Priority**: high
- **Description**: 遷移ステップを削減し、頻繁に行う「強化」と「編集」へ即座にアクセス。
- **Acceptance Criteria**:
    - 武器カードから「✨ (強化登録)」と「✏️ (編集)」の2ボタンを露出させ、1クリックで目的の画面・ダイアログへ遷移する。

### REQ-014: 「最近チェックした武器」へのクイックアクセス (UX-09)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Description**: 作業の再開を容易にする。
- **Acceptance Criteria**:
    - 直近で操作した武器3件へのリンクをUI（サイドバー等）に保持する。
    - `localStorage` 等を用いてセッションを跨いで永続化する。

### REQ-015: 具体的・詳細な Undo/Redo フィードバック (UX-10)
- **Status**: new
- **Type**: enhancement
- **Priority**: low
- **Description**: システム状態の正確な把握。
- **Acceptance Criteria**:
    - Undo/Redo 実行時、トースト通知等で「[武器名] の削除を戻しました」といった具体的なアクションラベルを表示する。

### REQ-016: 保存・同期ステータスの常時表示 (UX-11)
- **Status**: new
- **Type**: enhancement
- **Priority**: low
- **Description**: データの安全性への信頼性向上。
- **Acceptance Criteria**:
    - ページヘッダー等で「保存済み」「同期中」「エラー」などの状況をステータス表示する。

### REQ-017: お気に入り武器の削除プロテクション (UX-12)
- **Status**: done (2026-04-10)
- **Type**: enhancement
- **Priority**: high
- **Description**: 重大な誤操作の防止。
- **Acceptance Criteria**:
    - [x] お気に入り設定された武器については、削除時に2段階の承認（追加の確認確認ボタンなど）を要求する。
- **Concerns**:
  - Cloud Sync 使用時に `PGRST204` エラーが発生する。Supabase 側の `weapons` テーブルに `is_favorite` カラム (BOOLEAN, DEFAULT FALSE) を手動で追加する必要がある。

### REQ-018: Cookie 容量制限の警告機能の実装 (Audit 1-1)
- **Status**: new
- **Type**: bug
- **Priority**: mid
- **Description**: ブラウザCookieの容量制限（約4KB）に対し、データの圧縮後サイズが80%（約3.2KB）を超えた場合に、データ破損リスクを回避するための警告を表示する。
- **Problem**: 現状、仕様および実装の双方からこのチェック機能が抜け落ちており、データ量が増加した際に音もなく保存が失敗するリスクがある。
- **Acceptance Criteria**:
    - サイドバー等で、容量が逼迫している場合に警告メッセージを表示する。
    - 未ログイン（ローカル保存）ユーザーに対し、クラウド同期（ログイン）によるバックアップを促す。

### REQ-019: ロジック層における更新処理のバリデーション強化 (Audit 2-1)
- **Status**: new
- **Type**: maintenance
- **Priority**: high
- **Description**: `src/logic/talismans.py` 等の更新関数において、最終的な保存直前にデータの整合性チェックを強制する。
- **Problem**: 現状、UI側のバリデーションに依存しており、ロジック層に直接不正なデータが渡された場合に不整合がデータベースに永続化される恐れがある。
- **Acceptance Criteria**:
    - `update_talisman` 等の内部で `validate_talisman` を呼び出し、失敗時は処理を遮断する。

### REQ-020: 護石レア度・スロット規則の集約と脱ハードコード (Audit 3-1)
- **Status**: new
- **Type**: maintenance
- **Priority**: mid
- **Description**: 護石のレア度に応じたスロット位置のオフセットや、レア度8専用の武器スロット規則をマスタデータまたはルール定義クラスに集約する。
- **Problem**: 規則が UI (pages) と Logic の両方にハードコードされており、将来のレア度追加等の仕様変更に伴うバグの温床となっている。
- **Acceptance Criteria**:
    - `pages/5_talismans.py` および `src/logic/talismans.py` 内の条件分岐（`if rarity == 8` 等）を共通定義の参照に置き換える。

### REQ-021: AIフレンドリーなコンポーネント指向リファクタリング
- **Status**: done (2026-04-09)
- **Type**: maintenance
- **Priority**: High
- **Description**: AIエージェントによるメンテナンス効率を最大化するため、主要 4 ページ（護石管理、復元強化、装備ボックス、抽選結果）を State, Atoms, Dialogs, Form, List の 5 つの役割に物理分割した。これによりトークン消費が大幅に削減された。
- **Acceptance Criteria**:
    - [x] `src/components/` 配下に各ページ専用のディレクトリ（talismans, reinforcement, box, lottery）が作成されている。
    - [x] 各ページが `pages/` からクリーンにインポート呼び出しされている。
    - [x] 手動・自動テストを通じて、既存機能の完全な維持を確認。

### REQ-022: 例外処理の握り潰し是正とエラー通知の導入 (Audit 3-3)
- **Status**: new
- **Type**: maintenance
- **Priority**: mid
- **Description**: `storage_manager.py` 等の `try-except Exception: pass` を、適切なログ記録とユーザーへのフィードバック（エラー通知）に置き換える。
- **Problem**: サイレントエラーにより、障害発生時に原因特定が困難であり、ユーザーも「保存されたつもり」になるリスクがある。
- **Acceptance Criteria**:
    - ユーザーに影響するエラーについては `st.error` 等で明示的に通知する。

### REQ-023: 描画ループ内の冗長なインポート処理の排除 (Audit 4-1)
- **Status**: new
- **Type**: maintenance
- **Priority**: low
- **Description**: `pages/5_talismans.py` 内の `for` ループ内で実行されている `import` 文をファイルの先頭へ移動する。
- **Problem**: 不要なオーバーヘッドを発生させており、コーディング規約（PEP 8）にも反する。
- **Acceptance Criteria**:
    - 描画パフォーマンスを最適化し、コードのクリーンさを保つ。
 
### REQ-024: 復元強化厳選のページの登録時の武器選択UIの見直し
- **Status**: done (2026-04-10)
- **Current step**: Complete
- **Type**: enhancement
- **Priority**: P2
- **Surface**: "復元強化厳選のページの登録時の武器選択UIの見直し"
- **Symptom**: 抽選結果を登録する際、対象の1本を膨大なリストから探し出すのが困難。エキスパンダーによる操作ラグと、1カラムリストによる極端なスクロール量が負担となっている。
- **Root Cause**: 
    - **情報設計**: 武器種 ⇒ 属性 ⇒ スキル ⇒ ボーナスという、ユーザーの探索メンタルモデルに対応した階層的なフィルタリング手段が欠如している。
    - **インタラクション**: フィルタ操作がリストに即時（リアルタイム）反映されないため、試行錯誤のコストが高い。
    - **視覚**: 単一カラムのリスト表示では一度に表示できる武器数が少なく、比較・特定に適さない。
- **Requirement**: ユーザーの探索順序に基づいた多段階フィルタ（Weapons > Elements > Skills > Bonuses）を備え、リアルタイムに絞り込まれる高密度グリッド（3カラム等）形式の武器選択UIを実装し、特定武器の登録フローを大幅に効率化する。
- **Acceptance criteria**:
    - [ ] 「武器種」「属性」「スキル」「ボーナス」の順で条件を指定できる階層フィルタが提供されている。
    - [ ] フィルタの変更が、ページ遷移なしで武器リストに即時（リアルタイム）反映される。
    - [ ] 武器リストが、従来の1カラム形式からグリッド形式（3カラム推奨）に変更され、一覧性が向上している。
    - [ ] 各武器カードに「選択/決定」のアクション（HUD v14準拠）が統合されている。
    - [ ] 武器を選択した際、即座に登録フォームへのデータ反映が行われる。


### REQ-025: UI 文言の一元管理化 (Centralized String Management)
- **Status**: done (2026-04-09)
- **Current step**: none
- **Type**: enhancement
- **Priority**: high
- **Source**: "各所の文言調整を、開発者が手動でやりやすいように一元管理できる仕組みにしておきたい。例えば、ページのタイトルを変えたいとかいう程度で、逐一この開発フローを回す程ではない。"
- **Problem**: UIの文言（タイトル、ラベル等）が各ソースコード内にハードコードされており、些細な修文であってもコードを検索・修正する必要がある。これが開発フロー上のオーバーヘッドとなり、微調整を妨げている。
- **Requirement**: 全てのUI文字列を一元管理する定義ファイル（例：`src/locales/ja.py` 等）を導入し、アプリケーション全体から参照する仕組みを構築する。
- **Acceptance Criteria**:
    - 主要なUI文字列（ページ見出し、ボタン、メトリクスラベル等）が定義ファイルに移行されている。
    - 定義ファイルを1箇所修正するだけで、該当箇所の表示が即座に反映される。
    - 文言の修正にあたり、各ページのロジックコードを直接編集する必要がなくなる。

### REQ-026: 抽選結果一覧における「回数」表示の垂直整列
- **Status**: done (2026-04-09)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: mid
- **Source**: "抽選結果一覧系のページで、回数の表示位置を縦方向にきれいに揃えたい"
- **Problem**: 各行に表示される「回数」の位置がコンテンツの長さに依存してバラついており、縦方向の整列が取れていない。
- **Requirement**: リスト内の「回数」表示パーツのレイアウトを調整し、全行で垂直方向に一致するように整列させる。
- **Acceptance Criteria**:
    - 全ての抽選結果リスト行において、「回数」の表示開始位置（または中心位置）が垂直に整列している。
    - コンテンツ（スキル名等）が長くても、回数表示の位置がズレない。

### REQ-027: リストカードの2行表示対応による視認性向上とデザイン刷新
- **Status**: done (2026-04-10)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: mid
- **Source**: "武器一覧で長いスキル名が見えないのと、スキル名による位置ずれが大きいので、カードへの2行表記を許容する方針でデザインを見直そう"
- **Problem**: 現状の Lean UI (HUD v14) は 1 行表示を前提としているが、複雑なスキル構成の情報表示時に文字が溢れて省略（...）されたり、非表示にせざるを得ない情報が発生している。
- **Acceptance criteria**:
    - [x] **2行構造の導入**: ヘッダー（武器種・属性・強化タイプ）と詳細の詳細の2段構成を実装。
    - [x] **護石スロットの整列**: 護石一覧（Longモード）において、スキル名の長さに関わらずスロット位置を垂直に整列。
    - [x] **SSoT 維持**: `docs/design_system.md` の更新（予定）。
- **Note**: 行間のクリアランス制御については Streamlit の制約により完全な解決に至らず、REQ-028 へ引き継ぎ。

### REQ-029: 所持武器一覧における復元ボーナスの個別表示化
- **Status**: new
- **Type**: ui-ux
- **Priority**: mid
- **Source**: "所持武器一覧画面で、復元ボーナスの表記は同一ボーナスでもxNじゃなくて、枠をそのままの表示にしたい"
- **Problem**: 現状、同一の復元ボーナスが `xN` と集約表示されているため、スロットの構成が直感的に把握しづらい。
- **Acceptance Criteria**:
    - 所持武器一覧のカードにおいて、復元ボーナスが `xN` 表記ではなく、個別のスロット（例: `属性 II / 属性 II`）として表示されること。
    - 「枠をそのまま」という意図に合わせ、最大5スロットの構造が視覚的に認識しやすい形式であること。
- **Note**: 生産ボーナスの扱い（集約維持か個別化か）については、着手時に再確認が必要。

### REQ-030: 護石の重複・上位互換抽出機能
- **Status**: done (2026-04-11)
- **Type**: feature
- **Priority**: mid
- **Source**: "護石の重複と上位互換があるものを抽出する機能が欲しい"
- **Problem**: 護石が増えてくると、どの護石が不要（同一性能、または完全に他で代用可能）かを手動で判別するのが困難になる。
- **Acceptance Criteria**:
    - [x] 抽出ロジック：スキルレベル・スロットの両面で厳密な「同等以上」を判定するアルゴリズムの実装。
    - [x] 整理UI：候補と上位互換品を垂直に並べて比較できるダイアログの実装。
    - [x] カード刷新：V15規格への統合（64px、3スキル対応、スロット整列）。
    - [x] 保護機能：お気に入り登録済み護石の削除防止。

### REQ-031: スキル抽選結果一覧における「残り回数」の右寄せ配置
- **Status**: archived (2026-04-11)
- **Type**: ui-ux
- **Priority**: mid
- **Source**: "スキル抽選結果の残り回数列を右側に寄せたい"
- **Problem**: 現状、抽選結果一覧では「残り回数」がカード中央付近（ボーナスエリアの左側）に配置されており、他の一覧（復元強化登録等）のレイアウトと不一致であるため、視覚的な一貫性に欠ける。
- **Acceptance Criteria**:
    - スキル抽選結果一覧の各カードにおいて、「残り回数」の表示をカードの右端（アクションボタン寄り）に配置する。
    - 復元強化登録画面（`reinforcement` モード）のレイアウトと一貫性を持たせる。
- **Note**: 他のタスク（REQ-032等）の対応により既に解消済み、または不要と判断され取り下げ。

### REQ-032: 復元強化登録画面における武器選択カードの表示崩れ修正
- **Status**: done (2026-04-10)
- **Current Step**: none
- **Type**: bug
- **Priority**: high
- **Source**: "復元強化厳選の登録時に出てくる武器一覧のカード内表示が崩れてる。"
- **Problem**: `reinforcement/form.py` が v15 デザインシステムに未対応の古いデータ形式（生の HTML タグ）をカードコンポーネントに渡しているため、カラム配置ロジックと競合して表示が崩れている。
- **Acceptance Criteria**:
    - `reinforcement/form.py` でカードに渡すデータを v15 標準の構造化文字列（パイプ区切り）に変更する。
    - 武器選択リストのカードが、他のリスト画面と同様に正しく 2 段構成で表示されること。

### REQ-033: アイコンデザインの全体的な見直し (Icon Design Review)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Surface**: "アイコンデザインの見直し"
- **Problem**: 現在導入されているアイコンアセットについて、視認性、統一感、およびゲーム（MHW）の世界観との整合性を再評価する必要がある。一部のアイコンで解像度不足やスタイルの不一致が見られる。
- **Requirement**: 全アイコンアセットのデザインをレビューし、必要に応じてリデザインまたは高品質な素材への差し替えを行う。
- **Acceptance Criteria**:
    - 全ての主要アイコン（武器種、属性、スキル等）のデザインガイドラインへの適合性を確認済みであること。
    - 視認性の低いアイコンが特定され、改善案が提示されていること。

### REQ-034: アイコンの SVG 形式への完全移行と実装方式の最適化 (SVG Conversion Support)
- **Type**: enhancement
- **Status**: new
- **Priority**: mid
- **Surface**: "svg化対応"
- **Problem**: 現在、多くのアイコンが PNG などのビットマップ形式で保持されており、スケール時の劣化やファイルサイズの増大、CSS による動的な色変更が困難といった課題がある。
- **Requirement**: アイコンを SVG 形式に変換（ベクター化）し、CSS による色制御やスプライト化等、実装方式の最適化を行う。
- **Acceptance Criteria**:
    - 主要なアイコンアセット（武器・属性・スキル・スロット）が SVG 形式で用意されていること。
    - `vtracer` 等を用いた変換フローが確立されていること。
    - CSS `mask-image` またはインライン SVG 方式を採用し、動的なカラーリング（HUD配色への追従）が可能になっていること。
