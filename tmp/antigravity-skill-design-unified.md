# AntiGravity スキル設計 — 統合リファレンス

> このドキュメントは設計議論で得られた方針・観点・知見をすべて統合したもの。
> 実際の SKILL.md や Rules の実装はこのドキュメントを参考に AntiGravity エージェントが行う。
> プロジェクトスコープ（`.agent/` 配下）で検証し、汎用化は別プロジェクト開始時に判断する。

---

## 1. 全体アーキテクチャ

### 3 フロー構成

| フロー | 起動方法 | 所要時間 | 頻度 |
|--------|----------|----------|------|
| 要望受付（Intake） | 自然な発話で自動発火 + `/wish` フォールバック | 1〜2 分 | 随時 |
| 不具合報告（Hotfix triage） | 自然な発話で自動発火 + `/bug` フォールバック | 2〜5 分 | 完了後に問題発覚時 |
| 開発セッション（Dev） | `/dev` コマンドで明示起動 | 30 分〜数時間 | まとまった時間が取れたとき |
| アーキテクチャ検討 | `/arch-review` コマンドで明示起動 | 数日かけてもよい | 数ヶ月に1回 |

3 フローの接続点は `docs/backlog.md` のみ。

### 共有ステート

```
docs/
├── backlog.md          # 全フローの共有ステート
├── session.md          # /dev 実行中の現在地管理（セッション中のみ）
├── architecture.md     # 現行システム仕様
└── designs/
    └── {feature-name}.md
```

### 成果物の受け渡しチェーン

```
BA → docs/backlog.md
  → Coordinator → ユーザーに提示
    → Architect → docs/designs/{name}.md
      → Engineer → コード + テスト + スクリーンショット証跡
        → Reviewer → docs/designs/{name}.md とコードを照合
          → Coordinator → docs/backlog.md 更新
```

---

## 2. AntiGravity の実際の構成

### Rules / Skills / Workflows の実態

AntiGravity は 3 層すべてを持つが、公式ドキュメントが薄い部分がある。

| レイヤー | 保存場所 | 読み込み | 注意点 |
|----------|---------|---------|--------|
| Rules | `.agent/rules/` + `GEMINI.md` + `AGENTS.md` | 常時 ON | `model_decision` トリガーの挙動が公式で詳細未記載 |
| Skills | `.agent/skills/{name}/SKILL.md` | セマンティックトリガーでオンデマンド | description の精度がトリガー精度を左右 |
| Workflows | `.agent/workflows/{name}.md` | `/` コマンドで明示起動 | turbo コメントで自動実行可能 |

### model_decision の不確実性への対応

公式ドキュメントで `model_decision` トリガーの詳細が薄いため、
ロール定義を Rules の `model_decision` に頼る設計はリスクがある。

**方針: ロール定義も Skills として作り、description で発火させる。**
Rules（GEMINI.md / AGENTS.md）は本当の「常時 ON」ガードレールだけに使う。

### ディレクトリ構成

```
.agent/
├── rules/
│   └── （GEMINI.md / AGENTS.md で代替。必要に応じて使用）
├── skills/
│   ├── roles/                         # ロール定義（Skills として実装）
│   │   ├── business-analyst/
│   │   │   └── SKILL.md
│   │   ├── architect/
│   │   │   └── SKILL.md
│   │   ├── engineer/
│   │   │   └── SKILL.md
│   │   ├── tester-reviewer/
│   │   │   └── SKILL.md
│   │   ├── hotfix-triager/
│   │   │   └── SKILL.md
│   │   └── dev-coordinator/
│   │       └── SKILL.md
│   ├── tasks/                         # タスク定義
│   │   ├── requirement-analysis/
│   │   │   ├── SKILL.md
│   │   │   └── examples/             # 掘り下げの良い例・悪い例
│   │   │       ├── good-analysis.md
│   │   │       └── bad-analysis.md
│   │   ├── backlog-management/
│   │   │   ├── SKILL.md
│   │   │   ├── references/           # フォーマット定義
│   │   │   │   └── backlog-format.md
│   │   │   └── scripts/              # 整合性チェック
│   │   │       └── validate-backlog.py
│   │   ├── hotfix-triage/
│   │   │   ├── SKILL.md
│   │   │   └── examples/             # トリアージ判定の実例
│   │   │       └── triage-examples.md
│   │   ├── session-state/
│   │   │   ├── SKILL.md
│   │   │   └── references/           # session.md の雛形
│   │   │       └── session-format.md
│   │   ├── system-design/
│   │   │   ├── SKILL.md
│   │   │   └── references/           # 設計テンプレート
│   │   │       ├── design-doc-template.md
│   │   │       └── tradeoff-table-template.md
│   │   ├── implementation-plan/
│   │   │   └── SKILL.md
│   │   ├── tdd-implementation/
│   │   │   └── SKILL.md
│   │   ├── manual-test-design/
│   │   │   ├── SKILL.md
│   │   │   └── references/           # テストケーステンプレート
│   │   │       └── testcase-template.md
│   │   ├── browser-debug/
│   │   │   └── SKILL.md
│   │   ├── browser-verify/
│   │   │   └── SKILL.md
│   │   └── code-review/
│   │       ├── SKILL.md
│   │       └── references/           # レビューチェックリスト
│   │           └── review-checklist.md
│   └── escalation/                    # エスカレーション関連
│       └── escalation-report/
│           ├── SKILL.md
│           └── examples/             # 良い報告・悪い報告の実例
│               ├── good-escalation.md
│               └── bad-escalation.md
└── workflows/
    ├── dev.md
    ├── arch-review.md
    ├── wish.md
    └── bug.md

GEMINI.md（プロジェクトルート）     # 常時 ON ガードレール
AGENTS.md（プロジェクトルート）     # クロスツール対応ルール
```

### GEMINI.md に入れるもの（常時 ON、コンパクト）

```
- 指摘受付プロトコル（権限・スコープ・ステップの 3 チェック）
- 「できない報告は正当」「正直な報告 > 無理な完了報告」の価値観
- ワークフロー境界（intake は /dev に踏み込まない等）
- ロール切り替え時の宣言ルール
- 成果物を docs/ に保存してから切り替え
- /dev 中は docs/session.md が現在地、指摘前に必ず確認
- architecture-review 課題は /dev で解決しない
- 技術スタック固有の制約は project-specific 部分を確認
```

### Skills に入れるもの（オンデマンド、詳細な手順）

- ロールの判断基準と Boundaries
- タスクの具体的な手順、フォーマット、テンプレート
- エスカレーション報告のフォーマット
- チェックリスト、閾値

---

## 3. 設計原則

### Skills の肥大化防止（全ロール・全スキル共通）

- **GEMINI.md は判断基準と価値観のみ、コンパクトに**（常時コンテキスト消費）
- **Skills は必要なだけ長くてよい**（発火時にしか読み込まれない）
- ロール定義の Skills は判断基準と Boundaries に絞る（目安 10 行以内）
- タスク定義の Skills に手順・フォーマット・テンプレートを集約
- 1 スキル = 1 責務

### description の書き方

- 「いつ使うか」を書く（「何をするか」ではない）
- 具体的な動詞（Generate, Analyze, Execute, Validate）
- ユーザーが実際に使う日本語の口語表現を列挙
- Few-shot 例を 2〜3 個含める
- スキル数は 20〜30 個に絞る
- **description だけに頼らない（GEMINI.md で always_on 補助が必要）**

### Use / Do not use セクション

各スキルに「Use this skill when」「Do not use this skill when」を明示。
ロール切り替えの誤発火防止に効く。

### Input / Output の明示

各スキルに入出力をファイルパスレベルで定義。口頭の引き継ぎに頼らない。

---

## 4. ロール設計

### ロールは職種ではなく「判断基準のセット」

| 判断基準 | ロール設計 |
|----------|-----------|
| 1 つのやり取りの中で複数の能力が必要 | 複合ロールにまとめる |
| 成果物を挟んでフェーズが切り替わる | 別ロールに分ける |

### ロール一覧

| ロール | 種別 | 起動方法 | 主な責務 |
|--------|------|----------|----------|
| Business Analyst | 単一 | セマンティックトリガー | 要望の掘り下げ + backlog 登録 |
| Architect | 単一 | /dev 内で Coordinator が指名 | ハイレベル設計 + 実現可能性判定 |
| Engineer | 単一 | /dev 内で Coordinator が指名 | TDD 実装 + ブラウザデバッグ |
| Tester/Reviewer | 複合 | /dev 内で Coordinator が指名 | テスト品質検査 + 設計適合性レビュー + 懸念報告 |
| Hotfix Triager | 複合 | セマンティックトリガー | ヒアリング + 原因切り分け + ルーティング |
| Dev Coordinator | 複合 | /dev Workflow 起動時 | 進行管理 + ゲート + エスカレーション受け皿 |

### 複合ロールの定義方法

借りている能力の元ネタを Phase として明示。Boundaries はロール全体で 1 箇所。

**Hotfix Triager**: Phase 1（BA: ヒアリング） → Phase 2（Architect: 時間軸判定） → Phase 3（Router: 振り先決定）

**Dev Coordinator**: PM（進行管理） + BA（状況提示） + QA Manager（品質ゲート）

### 全ロール共通の Boundaries 追記事項

```
- 指摘を受けたら対応前に権限・スコープ・ステップを確認
- 自分の権限外・スコープ外なら Coordinator に戻す
- 技術的に困難な場合はエスカレーション（失敗ではない）
```

---

## 5. BA ロール・要求分析の改善

### 問題: BA が「記録係」になっている

ユーザーの発言を額面通りに受け取り、掘り下げが行われない。
「位置を揃えたい」→「位置を揃える」で登録、対処療法的な設計に流れる。

### 掘り下げフレーム: Surface → Symptom → Root Cause → Requirement

| 段階 | 問い | 例 |
|------|------|----|
| Surface | ユーザーは何と言ったか | 「位置がずれてるのを揃えたい」 |
| Symptom | 何が困っているか | 一覧で同じ項目の位置がバラバラ |
| Root Cause | なぜ困るか | 項目間の比較が直感的にしにくい |
| Requirement | 何が満たされれば解決か | 一覧で比較が直感的にできる UI にする |

**Surface と Requirement が同じ抽象度なら掘り下げ不足。**

### 「手段」と「目的」の判定

「xxxしたい」「xxxに変えたい」「xxxみたいにしたい」→ 手段に言及している可能性が高い。
手段が含まれている場合、目的を掘り下げる。

### 掘り下げの質問テンプレート

```
「{発言内容}とのことですが、それは{推測される目的}ということでしょうか？
 他にも気になっている点があれば教えてください。」
```

### UX 観点での Root Cause 分類

BA に足す UX 観点は「問題の種類に気づく目」であり、「UI を設計する能力」ではない。

- **情報設計の問題**: グルーピング、優先順位、比較・検索・一覧性
- **インタラクションの問題**: 操作手数、フィードバック、状態遷移
- **視覚的な問題**: 視認性、一貫性、視覚的階層

この分類が Architect → UX デザイナーへの橋渡しになる。
既存の UX デザイナー切り替えの仕組みは変更不要。

### 掘り下げ深さの目安

```
浅すぎ: 「位置を揃える」（手段が1つに限定）
適切:   「一覧で比較が直感的にできるUIにする」（方向性明確、手段は複数）
深すぎ: 「使いやすいアプリにする」（指針にならない）
```

### new / ready ステータスの分離

| ステータス | 意味 | /dev 対象 |
|-----------|------|-----------|
| new | 登録済み、掘り下げ未完了 | ❌ |
| ready | 掘り下げ完了、目的レベルの要求確定 | ✅ |

new → ready の遷移条件:
- 4 段階（Surface → Root Cause → Requirement）が埋まっている
- Requirement が目的レベル（手段ではない）
- Acceptance criteria が目的レベル
- ユーザーが確認済み

掘り下げ途中の完了メッセージ:
```
「バックログに仮登録しました（REQ-{n}、new）。
 まだ要求の整理が途中です。次回続きから整理できます。」
```

### バックログ項目フォーマット

```
### REQ-{n}: {title}
- Type: enhancement | defect | architecture-review
- Status: new | ready | in-progress | done | fix-needed | needs-investigation
- Priority: unset | P1 | P2 | P3
- Surface: {ユーザーの原文}
- Symptom: {困りごと}
- Root Cause: {なぜ困るか}
- Requirement: {目的レベルの要求}
- Acceptance criteria: {目的レベルの受入基準}
- Design doc: {パス or "none"}
- Triage notes: {該当する場合のみ}
- Concerns: {Reviewer の懸念。該当する場合のみ}
```

### BA Skills の肥大化防止

GEMINI.md に入れるもの（判断基準のみ）:
```
- ユーザーの発言は手段や症状であることが多い。そのまま要求にしない
- Surface と Requirement が同じ抽象度なら掘り下げ不足
- Root Cause を UX 観点（情報設計/インタラクション/視覚）で分類する
- new → ready は掘り下げ完了を確認してから
```

Skills に入れるもの（手順・テンプレート）:
```
- 掘り下げフレーム 4 段階の手順
- 質問テンプレート
- 手段/目的の判定パターンと例
- UX 分類の判定基準と例
- new → ready チェックリスト
```

---

## 6. Hotfix Triage の設計

### Intake（要望）と Hotfix（不具合報告）の分離

GEMINI.md で always_on ルーティング補助 + `/wish` `/bug` フォールバック。

### 時間軸の判定

| 判定 | 処理 |
|------|------|
| 直近の開発に起因 | backlog を fix-needed に戻す |
| 既存の潜在バグ | 新規 backlog（type: defect, status: ready） |
| 仕様通り | ユーザーに説明、要望なら Intake へ |
| 判定不能 | needs-investigation で登録 |

### 原因分類（直近の不具合の場合）

| 分類 | /dev 開始ステップ |
|------|------------------|
| 実装バグ | Step 5（Engineer） |
| テスト漏れ | Step 5（Engineer、テスト追加から） |
| 設計不備 | Step 3（Architect） |

---

## 7. Dev Coordinator の設計

### Interruption Handling

| 種類 | 対応 |
|------|------|
| 軽微な修正指示 | 現在のロールのまま対応、ステップ変わらず |
| フェーズを超える指摘 | Coordinator に戻り、適切なステップに巻き戻す |
| 無関係な発話 | /wish を案内、セッション中断しない |

### エスカレーションの受け皿

#### Architect から（設計段階で検知）
- Engineer に実装を振る前に止まる
- ユーザーに選択肢提示: 要求調整 or /arch-review
- Engineer に無駄な実装をさせない

#### Engineer から（実装段階で検知）
- 技術制約: 受入基準緩和 / 代替設計 / 保留 の選択肢
- トレードオフ: ユーザーに優先順位を判断させる
- リトライ上限超過: Architect に再評価を依頼

#### Reviewer から（懸念報告）
- 軽微 → backlog の Concerns 欄に記録
- 重大 or 繰り返し → ARCH 項目として切り出す
- 今の /dev に影響 → ユーザーに判断を仰ぐ

Reviewer はバックログに直接書かない。報告だけして記録は Coordinator が行う。

---

## 8. /dev Workflow

### ステップ構成

```
Step 1: [Coordinator] backlog 確認 → ユーザーが PO として選択 → 開始ステップ決定
Step 2: [Coordinator] 成果物確認 + ロール切り替え
Step 3: [Architect] 設計 + 実現可能性判定
  → 実現困難 → Coordinator にエスカレーション（/dev 内 or /arch-review）
Step 4: [Coordinator] ユーザー承認ゲート（STOP and wait）
Step 5: [Engineer] ローレベル設計 → TDD → ブラウザデバッグ
Step 6: [Coordinator] 成果物確認 + レビュアーへ引き継ぎ
Step 7: [Tester/Reviewer] コードレビュー + ブラウザ検証 + 懸念報告
Step 8: [Coordinator] 判定 → 差し戻し or 完了 or 中断
```

### 開始ステップの分岐

| 項目種別 | 開始 |
|----------|------|
| enhancement（通常） | Step 3 |
| defect（潜在バグ） | Step 3 |
| fix-needed（実装バグ/テスト漏れ） | Step 5 |
| fix-needed（設計不備） | Step 3 |
| needs-investigation | Step 5（再現確認から） |

### /dev の中断

| 種別 | 意味 | session.md | 再開方法 |
|------|------|-----------|---------|
| escalate | アーキテクチャ課題で中断 | status: escalated | /arch-review 後に /dev |
| abort | 要求取り下げ | 削除 | backlog を ready に戻す |
| block | 外部依存で進めない | status: blocked | 条件充足後に /dev |

「時間切れ」は中断ではない。session.md が残っていれば次回 /dev で自動再開案内。

### session.md

```
- Active REQ / Current step / Current role / Session status
- status: active | escalated | blocked
- escalated の場合: 理由、関連 ARCH 項目、暫定対応、再開条件
- blocked の場合: 理由、再開条件
```

---

## 9. /arch-review Workflow

### /dev との分離理由

リポジトリ全体に影響する判断を /dev の流れで行うと、
1つの REQ のスコープを超えた判断を勢いで決めてしまう。

### ステップ

```
Step 1: [Coordinator] ARCH 項目と関連 REQ を提示
Step 2: [Architect] 現状分析（制約の影響範囲、技術的負債）
Step 3: [Architect] 選択肢提示（最小変更〜大規模変更 + 「何もしない」）
Step 4: [Coordinator] ユーザー判断（急がない）
Step 5: 判断結果の反映
```

### backlog の architecture-review 項目

```
### ARCH-{n}: {title}
- Type: architecture-review
- Status: new | in-review | decided | closed
- Trigger: {REQ-{n} で発覚}
- Related REQs: {影響を受ける項目}
- Decision: {decided 後に記入}
```

architecture-review は `/dev` 対象外。`/arch-review` 専用。

---

## 10. エスカレーション・撤退設計

### 全ロールのエスカレーション必要性

| ロール | エスカレーション | 理由 |
|--------|-----------------|------|
| BA | 不要 | ユーザーに質問で解決 |
| Architect | **必要** | 設計段階で制約検知 |
| Engineer | **必要** | 実装段階で制約検知 |
| Reviewer | **懸念報告のみ** | 記録は Coordinator が行う |
| Triager | 不要 | 振り先決定のみ |
| Coordinator | 不要 | 受け皿側 |

### Architect のエスカレーション

設計段階で「これは制約内では無理」と気づいたら Engineer に振る前に止める。
Engineer のエスカレーションより手戻りコストが低い。

判定結果:
- 実現可能 → 通常設計
- トレードオフあり → 明示して設計続行、承認ゲートで提示
- 実現困難 → Coordinator にエスカレーション
- 不確実 → リスクを設計ドキュメントに明記、Engineer に共有

### Engineer のエスカレーション

#### 「できてないのにできたと言う」問題への対策

**根本原因**: エージェントの楽観バイアス + セルフチェックの限界 + 撤退パスの不在

**完了報告の構造化**:
```
✅ 基準1: xxx — 達成（証跡: スクリーンショット）
✅ 基準2: xxx — 達成（証跡: テスト通過）
❌ 基準3: xxx — 未達成（理由: 技術制約）
```

**正当なエスカレーション（失敗ではない）**:
- 「技術スタックの制約により達成困難です」
- 「2つのアプローチを試しましたが副作用があります」
- 「基準 A と基準 B がトレードオフです」

**リトライ上限**:
- 同一アプローチ 2 回失敗 → 別アプローチ検討
- 合計 3 アプローチ失敗 → エスカレーション

**価値観の明示（GEMINI.md に入れる）**:
```
正直な報告 > 無理な完了報告
受入基準を満たせない実装を「完了」とするのは、
「できない」と報告するよりも重大な問題として扱う
```

### Reviewer の懸念報告

レビュー出力フォーマット:
```
判定: Pass / Fail
指摘事項: （Fail の場合、修正案つき）
懸念事項: （将来的なリスクや設計レベルの気づき）
```

backlog への記録（Coordinator が行う）:
```
- Concerns:
  - [Review #{n}] {懸念内容}（architecture-review 候補）
```

### 技術スタック制約の扱い

**GEMINI.md（汎用）**:
```
技術スタック固有の制約を project-specific 部分で確認。
「できないこと」に該当するアプローチを試みない。
```

**Skills 内の project-specific セクション（例: Streamlit）**:
```
できないこと: ピクセル単位余白制御、CSS注入レイアウト、内部構造上書き
該当する要求 → エスカレーション + 代替案提示
```

---

## 11. マニュアルテストとブラウザサブエージェント

### テストの二段構え

| テスト | 検証対象 | 手段 |
|--------|---------|------|
| ユニットテスト | ロジックの正しさ | コードベース |
| ブラウザテスト | 見た目と操作の正しさ | ブラウザサブエージェント |

### テストケースの視覚検証項目

```
期待結果（機能）: 何が動けば OK か
期待結果（視覚）: どう見えれば OK か
  - レイアウト / レスポンシブ / 状態変化
```

### テスト分類ルール（ブラウザテスト対象を絞る）

- 純粋な表示確認 → ユニットテスト（DOM）
- レイアウト・レスポンシブ → ブラウザ必須
- インタラクション → 単純: ユニット、視覚フィードバック伴う: ブラウザ
- **ブラウザテストは「視覚でしか判定できない」ものに絞る**

### ロール分担

| タイミング | ロール | スキル | 目的 | コード修正 |
|-----------|--------|--------|------|-----------|
| 実装中 | Engineer | browser-debug | 動くようにする | する |
| レビュー時 | Reviewer | browser-verify | 正しいことを証明 | しない |

### トークン消費の最適化

ブラウザサブエージェントはトークン消費が重い。

- Engineer が全テスト実行（必要経費）+ スクリーンショット証跡を残す
- Reviewer は証跡ベースの確認が主、疑わしい箇所のみ再検証
- 修正後の再テストは関連テストのみ（毎回全数しない）
- 差し戻し前提ワークフローはトータルで重くなる（差し戻しごとに全数再検証 + ロール切替コスト）

### Engineer の証跡ルール

```
ファイル名: MT-{number}_{pass|fail}_{timestamp}.png
Reviewer がブラウザ起動せずに確認できる状態が browser-debug の完了条件
```

---

## 12. 実運用で得られた知見

### 知見 1: セマンティックトリガーだけでは自動発火が不安定

**対策**: GEMINI.md で always_on ルーティング補助 + `/wish` `/bug` フォールバック

### 知見 2: /dev 中にユーザーが指摘すると暴走する

3 パターン: ロール逸脱 / ステップ飛ばし / スコープ膨張

**対策**:
1. session.md でセッション状態を外部化
2. 指摘受付プロトコル（権限・スコープ・ステップの 3 チェック）
3. 各ロールの Boundaries に「一拍置く」

### 知見 3: 受入基準を無視して「完了」と言う

**対策**:
1. 完了報告を構造化（基準ごとの達成/未達成を明示）
2. エスカレーションを正当なパスとして定義
3. 「正直さ > 無理な完了」の価値観を GEMINI.md に明示

### 知見 4: 要求分析が浅く対処療法になる

**対策**:
1. Surface → Root Cause の掘り下げフレーム
2. new / ready ステータス分離
3. UX 観点での分類

### 知見 5: Gemini 自身が AntiGravity の機能を正確に把握していない

**対策**: 公式ドキュメントが薄い機能（model_decision 等）に依存しない設計にする

### 理想と現実

| 項目 | 理想 | 現実 |
|------|------|------|
| 自動発火 | description で自動 | always_on 補助 + コマンドフォールバック |
| ワークフロー維持 | Workflow 定義だけで順守 | session.md + 指摘受付プロトコル |
| ロール遵守 | Boundaries だけで越権防止 | 「一拍置く」ルール追加 |
| 完了判定 | 受入基準で自動判定 | 構造化報告 + エスカレーションパス |
| 要求分析 | description で自動掘り下げ | 掘り下げフレーム + new/ready 分離 |

---

## 13. ツール選定の知見

### AntiGravity を選択する理由

- Google One 既存契約との相性
- ブラウザサブエージェント内蔵（Web アプリ開発に強い）
- SKILL.md ユニバーサルフォーマット（将来のツール移行時も資産流用可能）

### AntiGravity の制約

| 制約 | 対処 |
|------|------|
| ワークフロー遵守の強制力が弱い | session.md + 指摘受付プロトコル + GEMINI.md |
| セマンティックトリガー精度が不安定 | GEMINI.md 補助 + フォールバックコマンド |
| AI Pro レート制限がシビア化傾向 | ブラウザテスト対象を絞る、タスクを小さくスコープ |
| 公式ドキュメントが薄い部分がある | 不確実な機能に依存しない設計 |

### 将来の選択肢

- Engineer フェーズだけ Claude Code（Hooks 活用）に投げるハイブリッド
- Kiro（仕様駆動 + Hooks）の検討
- 2つ目のプロジェクト開始時に Global / Workspace の仕分け

---

## 14. Skills の拡張: examples / references / scripts

### スキルディレクトリの構成パターン

SKILL.md だけでなく、補助ファイルを活用することで
SKILL.md 自体をスリムに保ちつつ、精度と再現性を上げられる。

```
my-skill/
├── SKILL.md        # 必須: メタデータ + 指示
├── examples/       # 任意: Few-shot 例（良い例・悪い例）
├── references/     # 任意: テンプレート、フォーマット定義
├── scripts/        # 任意: 決定論的な検証・生成スクリプト
└── assets/         # 任意: 静的ファイル
```

SKILL.md から相対パスで参照する。エージェントは発火時にこれらを読み込む。
SKILL.md 本体がコンパクトになり、肥大化を防げる。

### examples/ — Few-shot 例で精度を上げる

SKILL.md 内にインラインで例を書くより、examples/ に分けて
実運用の実例を蓄積していくほうが管理しやすい。
良い例と悪い例の両方を置くと、エージェントの判断精度が大幅に上がる。

#### requirement-analysis/examples/（優先度: 高）

BA の掘り下げ改善に直結。今一番の課題。

good-analysis.md:
```
## 実例: カード一覧の比較性改善

ユーザー: 「カード内の同じ項目の位置がずれてるのをキレイにそろえたい」

Surface: 「位置がずれてるのを揃えたい」
  ↓ 掘り下げ
Symptom: 一覧で同じ項目の位置がカードごとにバラバラ
Root Cause: 項目間の比較が直感的にしにくい（情報設計の問題）
Requirement: 一覧で比較が直感的にできるUIにする
Acceptance criteria:
  - 一覧表示で同じ項目を視線移動なく比較できる
  - 既存の項目の可読性が損なわれない
```

bad-analysis.md:
```
## アンチパターン: Surface のまま登録

ユーザー: 「カード内の同じ項目の位置がずれてるのをキレイにそろえたい」

Requirement: カード内要素の位置を揃える ← 手段レベル、掘り下げ不足
Acceptance criteria: 項目のX座標が全カードで一致する ← 実装の話

問題: Architect の設計自由度を狭め、技術制約に直撃する
```

#### escalation-report/examples/（優先度: 高）

エスカレーションの「良い報告」と「悪い報告」。

good-escalation.md:
```
## 実例: Streamlit 制約によるエスカレーション

対象: REQ-12 / 受入基準「コンポーネント間余白20px以下」

試みたアプローチ:
1. st.markdown CSS注入: 効果なし（Streamlitが上書き）
2. st.container パディング上書き: 部分的に効くが他コンポーネント崩壊

達成できない理由: Streamlit はコンポーネント間余白のピクセル単位制御を
サポートしていない（フレームワークの設計制約）

現時点で実現可能な範囲: st.columns の比率調整で視覚的な近接感は改善可能
ただし定量基準（20px以下）は達成不可

選択肢:
a. 受入基準を「視覚的にグルーピングされて見える」に緩和
b. React カスタムコンポーネントで実装（→ /arch-review）
c. 保留
```

bad-escalation.md:
```
## アンチパターン: 嘘の完了報告

対象: REQ-12 / 受入基準「コンポーネント間余白20px以下」

報告: 「調整完了しました」
実態: 余白は約45pxのまま。CSS注入を試みた痕跡はあるが効いていない

問題:
- 受入基準との照合を行っていない
- 技術制約に気づいていたが報告せず「できた」と宣言
- Reviewer が検出するまで未達成が発覚しない
```

#### hotfix-triage/examples/（優先度: 中）

トリアージの判定実例。時間軸判定の「直近起因」vs「潜在バグ」の区別。

```
## 実例A: 直近の開発に起因
ユーザー: 「さっき追加したデータが一覧に出ない」
→ 直近の REQ-10（データ追加機能）のステータス: done
→ 変更ファイルと症状箇所が一致
→ 判定: fix-needed（実装バグ）

## 実例B: 既存の潜在バグ
ユーザー: 「検索が遅い気がする」
→ 直近の done 項目に検索関連なし
→ 以前から存在し得た問題
→ 判定: 新規 REQ（type: defect, status: ready）
```

### references/ — テンプレートとフォーマット定義

SKILL.md からフォーマット定義やテンプレートを分離する。
SKILL.md がスリムになり、フォーマット変更時も references/ だけ更新で済む。

#### backlog-management/references/（優先度: 高）

backlog-format.md:
```
## バックログ項目フォーマット

### REQ-{n}: {title}
- Type: enhancement | defect | architecture-review
- Status: new | ready | in-progress | done | fix-needed | needs-investigation
- Priority: unset | P1 | P2 | P3
- Surface: {ユーザーの原文}
- Symptom: {困りごと}
- Root Cause: {なぜ困るか}
- Requirement: {目的レベルの要求}
- Acceptance criteria: {目的レベルの受入基準}
- Design doc: {パス or "none"}
- Triage notes: {該当する場合のみ}
- Concerns: {Reviewer の懸念。該当する場合のみ}

## ARCH 項目フォーマット

### ARCH-{n}: {title}
- Type: architecture-review
- Status: new | in-review | decided | closed
- Trigger: {REQ-{n} で発覚}
- Related REQs: {影響を受ける項目}
- Decision: {decided 後に記入}

## ステータス遷移

new → ready → in-progress → done → fix-needed → in-progress → done
needs-investigation → in-progress → done
```

#### session-state/references/（優先度: 中）

session-format.md:
```
## session.md フォーマット

### Current session
- Active REQ: REQ-{n}
- Current step: Step {n} ({description})
- Current role: {role name}
- Session status: active | escalated | blocked
- Pending action: {next action}
- Blocked on: {none | user-approval | arch-review:ARCH-{n} | external:{details}}

### If escalated
- Escalation reason: {技術制約 / スコープ超過}
- Related issue: ARCH-{n}
- Interim resolution: {暫定対応 or "none (保留)"}
- Resume condition: {再開条件}

### If blocked
- Block reason: {詳細}
- Resume condition: {再開条件}

### History
- {timestamp}: {event description}
```

#### system-design/references/（優先度: 中）

design-doc-template.md:
```
## {feature-name} 設計ドキュメント

### 対象要求
REQ-{n}: {title}

### ハイレベル設計
（コンポーネント構成、データフロー）

### 影響範囲
（変更が及ぶ既存コンポーネント）

### 実装計画
（タスク分割、変更対象ファイル一覧）

### テスト要件
- ユニットテスト対象: ...
- マニュアルテスト対象: ...

### 受入基準
（backlog の受入基準を具体化）

### リスク・制約
（技術制約への抵触可能性があれば明記）
```

tradeoff-table-template.md:
```
## 選択肢比較

| 観点 | 選択肢A: {name} | 選択肢B: {name} | 選択肢C: 何もしない |
|------|-----------------|-----------------|-------------------|
| 実現できること | | | |
| できないこと | | | |
| 開発コスト | | | |
| リスク | | | |
| 保守性への影響 | | | |
| 推奨度 | | | |
```

#### manual-test-design/references/（優先度: 中）

testcase-template.md:
```
## テストケースフォーマット

### MT-{number}: {テスト名}
- 前提条件: {テスト開始時の状態}
- 手順:
  1. {操作}
  ...
- 期待結果（機能）: {何が動けば OK か}
- 期待結果（視覚）: {どう見えれば OK か}
  - レイアウト: ...
  - レスポンシブ: ...
  - 状態変化: ...
- 対応する受入基準: {design doc への参照}
```

#### code-review/references/（優先度: 低）

review-checklist.md:
```
## レビューチェックリスト

### 設計適合性
- [ ] 実装がアーキテクトの設計ドキュメントに適合しているか
- [ ] 受入基準がすべて満たされているか

### テスト品質
- [ ] テストが受入基準を網羅しているか
- [ ] 実装の内部詳細に依存していないか
- [ ] 脆いアサーション（タイミング/順序依存）がないか
- [ ] テスト間に暗黙の依存関係がないか

### その他
- [ ] エッジケースが考慮されているか
- [ ] 既存機能へのリグレッションがないか
- [ ] browser-verify で視覚検証を行ったか（該当する場合）
```

### scripts/ — 決定論的な検証

エージェントの判断に頼らず、スクリプトで確実にチェックできる部分。

#### backlog-management/scripts/（優先度: 低）

validate-backlog.py:
```
検証内容:
- REQ 番号の重複チェック
- ステータス遷移の整合性（new → done に直接遷移していないか等）
- new のまま放置されている項目の検出
- fix-needed 項目に triage notes が入っているか
- done 項目に完了日が入っているか
- architecture-review 項目が /dev 対象になっていないか
```

SKILL.md からスクリプトを参照:
```
整合性チェックが必要な場合は scripts/validate-backlog.py を実行する。
スクリプトの出力に問題があれば、修正してから操作を続行する。
```

スクリプトの出力だけがコンテキストに入り、スクリプト自体のコードは
コンテキストを消費しない（Progressive Disclosure の恩恵）。

### 実運用での蓄積方法

examples/ は最初から完璧に揃える必要はない。
実運用で「良い判断」「悪い判断」が発生するたびに追加していく。

```
改善サイクル:
1. タスクを実行
2. 良い分析 / エスカレーションが出たら → examples/ に追加
3. 悪いパターンが出たら → bad-xxx.md に追加
4. エージェントの精度が上がる
5. 繰り返し
```

references/ は最初に雛形を作っておき、運用に合わせて調整。
scripts/ は整合性の問題が発生してから作っても遅くない。

### ロール定義には不要

ロール定義の Skills（roles/ 配下）には examples/ や scripts/ は基本不要。
ロールは「判断基準」であり、具体例はタスクスキル側に置くほうが自然。

---

## 15. 改善サイクル

1. 10〜20 の実タスクでエージェントを走らせる
2. セッションログをエージェントアーキテクトとして監査させる
3. 暴走パターンを分類（ロール逸脱 / ステップ飛ばし / スコープ膨張 / 楽観バイアス）
4. パターンに応じてスキル定義を改修
5. description のトリガーフレーズを実際の発話に基づいて追加
6. 複合ロールの Phase 間で判断が飛ぶ場合は Phase 記述を強化
7. SKILL.md が肥大化したら分割（GEMINI.md は常にコンパクトに保つ）

### 検証指標

- 嘘の完了報告の頻度（減少が正しい）
- エスカレーション報告の頻度（増加が正しい、初期は）
- new → ready 変換率
- 設計フェーズでの手戻り頻度
- 中断（escalate / abort / block）の正常利用
- ARCH 項目の蓄積と消化
