---
name: project-conventions
description: "Project specific technology stack and design standards manual."
---

# Project Conventions (Manual)

このドキュメントは、プロジェクト固有の技術スタック、デザイン基準、および運用上の細則を定義するマニュアルです。最上位の行動規範については `.agents/rules/standard.md` および `GEMINI.md` を参照してください。

## 1. /dev Workflow 実務

- **Milestone Enforcement:** `task.md` には `dev.md` の公式ステップ名をそのまま使用する。
- **SSoT Integrity:** 実装が完了したら、必ず `docs/*.md`（仕様書）を最新の実装状態と同期させた上で、バックログを `done` にする。

## 2. 言語ルール

- **LANGUAGE POLICY (MANDATORY):**
  - **All communication with the USER (chat responses) and Implementation Plans MUST be in Japanese.**
  - **(ユーザーとのコミュニケーションおよび実装プランは、常に日本語で行うこと。)**
- **Internal Docs:** `docs/designs/*.md` や `docs/ui_spec.md` は、技術的正確性を期すため、指示がない限り英語で記述して良い。

2. **Styling**: Vanilla CSS. No TailwindCSS unless explicitly requested and version-confirmed.
3. **Frameworks**: Next.js or Vite only if "Web App" is explicitly requested.
4. **Local Dev**: Use `npm run dev`. Build only for validation or on request.

### 5-2. Premium Design Aesthetics
1. **Rich Aesthetics**: Vibrant colors, sleek dark modes, glassmorphism, dynamic animations.
2. **Visual Excellence**:
   - Curated, harmonious color palettes (HSL).
   - Modern typography (Inter, Roboto, Outfit).
   - Smooth gradients and micro-animations.
3. **Dynamic Design**: Hover effects and interactive elements to make the UI feel alive.
4. **No Placeholders**: Use `generate_image` for demonstration assets.

### 5-3. Monster Hunter Domain Knowledge
- **Terminology**: Rarity (Ⅰ-Ⅷ), Slots (Lv1-4), Talismans, Augmentation, Skill Lottery.
- **Visuals**: Use established MHW icons/colors for elements (Fire: Red, Ice: Light Blue, etc.).

## 6. Context Optimization (Defrag Rule)
- 複数のファイルに似た指示がある場合、常にこの `project-conventions` の定義を正とする。
- アーキテクトは、冗長な指示を積極的に削除・統合し、指示の「密度と実行力」を維持しなければならない。
