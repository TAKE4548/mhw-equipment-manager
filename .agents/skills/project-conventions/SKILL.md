---
name: project-conventions
description: "Project specific technology stack and design standards manual."
---

# Project Conventions (Manual)

This document defines project-specific technology stacks, design standards, and operational details. For top-level behavioral codes, refer to `.agents/rules/standard.md` and `GEMINI.md`.

## 1. /dev Workflow Execution

- **Milestone Enforcement:** Use official step names from `dev.md` directly in `task.md`.
- **SSoT Integrity:** Upon implementation completion, synchronize `docs/*.md` (specifications) with the latest implementation state before marking the backlog item as `done`.

## 2. Language Policy (STRICT)

- **External (User-facing)**: 
  - **All communication with the USER (chat) and artifacts (Plans, Walkthroughs) MUST be in Japanese.**
  - (ユーザーとのコミュニケーションおよびプラン類は、常に日本語で行うこと。)
- **Internal (Agent-facing)**: 
  - **All instruction files in `.agents/` (Skills, Workflows, Rules) MUST be in English.**
  - **Description** fields in frontmatter must be English.
- **Exceptions**: App-specific domain terms (e.g., 護石, 復元強化) and natural language trigger patterns remain in Japanese.

## 3. Technology Stack

1. **Core**: HTML for structure, Javascript for logic.
2. **Styling**: Vanilla CSS. No TailwindCSS unless explicitly requested and version-confirmed.
3. **Frameworks**: Next.js or Vite only if "Web App" is explicitly requested.
4. **Local Dev**: Use `npm run dev`. Build only for validation or on request.

## 4. Premium Design Aesthetics

1. **Rich Aesthetics**: Vibrant colors, sleek dark modes, glassmorphism, dynamic animations.
2. **Visual Excellence**:
   - Curated, harmonious color palettes (HSL).
   - Modern typography (Inter, Roboto, Outfit).
   - Smooth gradients and micro-animations.
3. **Dynamic Design**: Hover effects and interactive elements to make the UI feel alive.
4. **No Placeholders**: Use `generate_image` for demonstration assets.

## 5. Monster Hunter Domain Knowledge

- **Terminology**: Rarity (Ⅰ-Ⅷ), Slots (Lv1-4), Talismans, Augmentation, Skill Lottery.
- **Visuals**: Use established MHW icons/colors for elements (Fire: Red, Ice: Light Blue, etc.).

## 6. Context Optimization (Defrag Rule)

- If similar instructions exist in multiple files, the definition in `project-conventions` is the Source of Truth.
- The Architect must proactively delete or consolidate redundant instructions to maintain the "density and execution power" of directives.
