# Implementation Tasks: MHWs Equipment Manager

## Phase 1: Setup (Project Initialization)
- [x] T001 Initialize project directory structure (`src/logic`, `src/components`, `src/database`, `pages/`, `tests/unit/`)
- [x] T002 Set up project dependencies (Streamlit, Pandas, Pytest) in `requirements.txt`
- [x] T003 Create MVP entry point and navigation structure in `app.py`

## Phase 2: Foundational (Blocking Prerequisites)
- [x] T004 Implement `StorageManager` for Cookie (zlib/base64) & Supabase sync in `src/database/storage_manager.py`
- [x] T005 Implement `st.session_state` initialization for Undo/Redo history stacks in `app.py`

## Phase 3: User Story 1 - Register Skill Upgrades [US1]
- [x] T006 [P] [US1] Implement `register_upgrade` and `get_active_upgrades` logic in `src/logic/equipment.py`
- [x] T007 [P] [US1] Create unit tests for registration and query logic in `tests/unit/test_equipment.py`
- [x] T008 [US1] Implement registration form UI with session state validation in `pages/1_register.py`
- [x] T009 [US1] Implement active upgrades dashboard rendering in `app.py`

## Phase 4: User Story 2 - Execute Skill Upgrades [US2]
- [x] T010 [P] [US2] Implement `execute_upgrade` logic in `src/logic/equipment.py` (decrement count logic)
- [x] T011 [P] [US2] Create unit tests for execution logic in `tests/unit/test_equipment.py`
- [x] T012 [US2] Add interactive "Execute (-1)" action button to the active upgrades table in `app.py`

## Phase 5: User Story 3 - Auto-remove Completed Upgrades [US3]
- [x] T013 [P] [US3] Implement logic to handle records reaching count <= 0 during execution in `src/logic/equipment.py`
- [x] T014 [P] [US3] Create unit tests verifying auto-removal boundary conditions in `tests/unit/test_equipment.py`
- [x] T015 [US3] Verify dashboard table gracefully handles empty lists in `app.py`

## Phase 6: User Story 4 - Undo/Redo Actions [US4]
- [x] T016 [P] [US4] Implement pure logic `undo_last_action` and `redo_last_action` functions in `src/logic/history.py`
- [x] T017 [P] [US4] Create unit tests for history stack management in `tests/unit/test_history.py`
- [x] T018 [US4] Wire registration and execution UI actions to push to the history stack in `app.py` and `pages/1_register.py`
- [x] T019 [US4] Add "Undo" and "Redo" buttons to the dashboard toolbar in `app.py`


## Phase 7: Polish & Cross-Cutting Concerns
- [x] T020 Refactor duplicate Streamlit grid/table rendering code into `src/components/tables.py`
- [x] T021 Apply Streamlit `@st.cache_data` or appropriate session state caching for query performance
- [x] T022 Run full end-to-end manual verification using scenarios outlined in `docs/setup/quickstart.md`

## Phase 8: Additional User Requests (Post-MVP)
- [x] T023 Topページから登録画面へ遷移できるようにする
- [x] T024 Executeアクションを全レコード共通の進行（残り回数の一括マイナス）に変更する
- [x] T025 シリーズスキル・グループスキルを選択式（Enum/Selectbox）にする
- [x] T026 ツールバーレイアウトを改善（左にUndo/Redo、右に新規登録）し、テーブル行と縦のラインを揃える
- [x] T027 テーブルを残り回数の少ない順（昇順）でソートする
- [x] T028 テーブル列を固定幅化し、グループスキルを独立カラムにして位置ズレを防ぐ
- [x] T029 MHWをMHWs（モンスターハンターワイルズ）という略称に統一する
- [x] T030 【UX】スキルピッカーを st.dialog 形式に刷新し、選択時の自動クローズを実現
- [x] T031 【UX】ピッカー内の ⭐ 登録を st.fragment 化し、メニューを維持したままの連続操作を可能にする
- [x] T032 【UI】シリーズ/グループスキルのピッカーをレスポンシブな横並び（2カラム）レイアウトに変更
- [x] T033 【UI】全ページのカードデザインを所有武器一覧のスタイル（超スリム）に統一
- [x] T034 【UI】ナビゲーション名を整理し、順序を最適化（Homeを左端へ移動）

## Phase 9: Maintenance & Continuous Quality
- [x] T035 [Architect] Sync all documentation with current implementation (zlib-Cookie, Supabase)
- [x] T036 **[完了]** 不要ファイルの削除（`gsheets_manager_old.py` 等のクリーンアップ）
- [x] T037 [Engineer] `docs/workflow/test_scenarios.md` に基づく単体テストの実装
- [ ] T038 [Engineer] 仕様変更に伴う再実装：スキル抽選実施時の武器データ更新ロジック
- [ ] T039 [Engineer] 仕様変更に伴う再実装：復元厳選の自動削除ロジック追加
- [ ] T040 [Engineer] 全画面（所持武器・抽選・復元）への一貫したUndo/Redoの実装
- [ ] T041 Final consistency check: Variable naming vs Documentation terminology

