# Dark Mode Fix Report

## What changed

- Added dark-mode token overrides in `apps/desktop/src/styles.css`.
- Tightened `--ui-bg-card`, `--ui-bg-input`, and related surface tokens in `:root.dark`.
- Kept the existing light theme path intact.

## Why this helps

- The desktop shell already used dark enough chrome in parts of the window, but cards and inputs could still drift too light.
- Re-tuning the surface tokens keeps the main area, cards, and inputs closer to the active dark palette.
- The change is token-level, so it applies consistently to existing components instead of patching each one individually.

## Validation

- `npm run type-check` passed.
- Targeted ESLint on the new settings panel files passed.
- Full repo lint still has unrelated pre-existing errors outside this patch.

