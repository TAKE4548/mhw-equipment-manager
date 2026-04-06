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
- [x] T038 [Engineer] 仕様変更に伴う再実装：スキル抽選実施時の武器データ更新ロジック
- [x] T039 [Engineer] 仕様変更に伴う再実装：復元厳選の自動削除ロジック追加
- [x] T040 [Engineer] 全画面（所持武器・抽選・復元）への一貫したUndo/Redoの実装
- [x] T041 Final consistency check: Variable naming vs Documentation terminology

## Phase 10: Appraised Talismans (鑑定護石管理) [Completed]
- [x] T042 [Architect/Engineer] Create `src/data/talisman_master.json` holding Skill Groups (A-J) and Rarity Patterns (5-8).
- [x] T043 [Engineer] Expand `StorageManager` to handle `Talismans` table.
- [x] T044 [Engineer] Create `src/logic/talismans.py` for registration, search, and logic validation using master data.
- [x] T045 [Engineer] Create `pages/5_talismans.py` integrating the slim UI and `st.dialog` skill picker.
- [x] T046 [Engineer] Implement Favorite (⭐) toggling and trash functions for Melding target management.
- [x] T047 [Engineer] Implement unit tests for `src/logic/talismans.py` based on `docs/workflow/test_scenarios.md`.

## Phase 11: Reinforcement Tracker Refactoring (強化厳選リファクタ) [Completed]
- [x] T048 [Engineer] Refactor `build_comp_mini` to use the fixed-width Visual Band UI (no icons).
- [x] T049 [Engineer] Update weapon selection cards in `pages/reinforcement_registration.py` to show Group Skill and Production Bonuses.
- [x] T050 [Engineer] Implement filtering and sorting UI (toolbar) for the active tracker list in `pages/reinforcement_registration.py`.
- [x] T051 [Engineer] Ensure all visual changes adhere to `docs/design_system.md` standards.

## Phase 12: Performance Optimization (パフォーマンス最適化) [Completed]
- [x] T052 [Engineer] Apply `@st.cache_data` to `get_master_data()`, `load_equipment()`, and `load_trackers()`.
- [x] T053 [Engineer] Apply `functools.lru_cache` to `get_abbr_item()` and other core utility logic.
- [x] T054 [Engineer] Refactor `pages/` (especially `reinforcement_registration.py` and `0_skill_lottery.py`) to isolate list rendering in `st.fragment`.
- [x] T055 [Engineer] Move DataFrame merges and normalization outside of rendering loops to ensure O(1) or O(N) instead of O(N^2) complexity.

## Phase 13: Multi-User Data Isolation & Cache Stabilization [Completed]
- [x] T056 [Engineer] Partition logic loaders (`load_equipment`, etc.) using `user_id` as cache key.
- [x] T057 [Engineer] Propagate `user_id` context through all UI components (`tables.py`) and logic calls.
- [x] T058 [Engineer] Implement mandatory `undo_stack` and `redo_stack` cleanup on auth change.

## Phase 14: Persistent Cloud Deletion & Integrity Repair [Completed]
- [x] T059 [Engineer] Implement ID-based full synchronization in `_save_to_cloud` to handle deletions.
- [x] T060 [Engineer] Implement cascading deletions (weapon -> tracker) to maintain FK consistency.
- [x] T061 [Engineer] Add self-healing orphan pruning to the cloud sync process.

## Phase 15: Session Security & Sync Hardening [Completed]
- [x] T062 [Engineer] Implement `logging_out` guard to prevent race conditions in session restoration.
- [x] T063 [Engineer] Implement proactive `pull_cloud_to_local()` on login to prevent sync-on-login data loss.
- [x] T064 [Engineer] Correct cookie expiration policy (max-age=0) for reliable logout.

## Phase 16: UI Responsiveness & Skill Picker Optimization [Completed]
- [x] T065 [Engineer] Optimize skill picker render loop by batching favorite lookups in O(1) set.
- [x] T066 [Engineer] Implement user-scoped caching for favorites logic with proactive invalidation.
- [x] T067 [Engineer] Resolve TypeError in favorites query logic for multi-user environments.

## Phase 17: Talisman Filter & Sort UX Improvement [Completed]
- [x] T068 [Architect] Define filtering/sorting requirements (REQ-069) and UX logic for responsiveness (REQ-070).
- [x] T069 [Engineer] Implement `filter_and_sort_talismans` in `src/logic/talismans.py` with comprehensive unit tests.
- [x] T070 [Engineer] Integrate filter/sort UI in `pages/5_talismans.py` using `st.fragment` and `key` binding for 1-click response.

## Phase 18: Deployed Environment Import & Schema Fix (REQ-071) [Completed]
- [x] T072 [Engineer] Synchronize `columns_map` in `src/database/storage_manager.py` with `docs/data_model.md` and logic layers.
- [x] T073 [Engineer] Align `talismans` and `favorites` column names (underscores) to fix data corruption on cloud sync.
- [x] T074 [Engineer] Harden `sys.path` injection in `app.py` for Streamlit Cloud robustness.
- [x] T075 [Engineer] Verify fix with automated schema consistency tests in `tests/unit/test_storage_schema.py`.

## Phase 19: Expanded Weapon Search Filters (REQ-072) [Completed]
- [x] T076 [Architect/UX] Define 3-column filter layout and AND-matching logic for restoration bonuses (REQ-072).
- [x] T077 [Engineer] Expand `filter_equipment` in `src/logic/equipment_box.py` with level-specific AND logic.
- [x] T078 [Engineer] Update `pages/reinforcement_registration.py` with the new filter UI and master-data integration.
- [x] T079 [Engineer] Verify filter logic with unit tests in `tests/unit/test_filter_logic.py`.
- [x] T080 [Architect] Update all SSoT documents (`requirements.md`, `ui_spec.md`, `ux_logic.md`).

