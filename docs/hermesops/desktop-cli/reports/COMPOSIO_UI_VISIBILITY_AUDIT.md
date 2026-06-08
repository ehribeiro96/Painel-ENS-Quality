# Composio UI Visibility Audit

## Scope

- Desktop source: `/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops`
- App path: `/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop`
- Target files:
  - [`src/app/settings/index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L89)
  - [`src/app/settings/hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L133)

## Answers

- The component exists? Yes. `HermesOpsSettings` exists in [`hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L133).
- Is it imported? Yes. `SettingsView` imports `HermesOpsSettings` in [`index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L17).
- Is it rendered? Yes. The `activeView === 'hermesops'` branch renders `<HermesOpsSettings />` in [`index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L236).
- Is there a clickable UI item? Yes. A top sidebar callout button opens HermesOps in [`index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L93), and the sidebar also has a `HermesOps` nav item in [`index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L152).
- Does the text `Composio` appear in rendered code? Yes. It appears in the sidebar callout, the sidebar nav, the `Composio` tab, and the panel content in [`hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L203) and [`hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L316).
- Is it hidden by a condition? No. The sidebar callout is always rendered, and the `HermesOps` nav item is always present.
- Is it behind a feature flag? No feature flag was added or detected in the new integration path.
- Is it missing a route? No. The panel is reachable through the existing overlay settings `tab` parameter and the `hermesops` view branch.
- Is it in an inaccessible tab? No. `HermesOps` is visible in the sidebar, and the sidebar callout gives an additional direct entry point.

## Conclusion

The panel was connected before, but the visibility issue was real enough that a stronger, always-visible sidebar callout was necessary. The patch now makes `HermesOps` and `Composio` visible without devtools.

