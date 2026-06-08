# Phase 4 Git Provenance Repair Plan

## Scenario A - HML is functional Git
- Apply `.gitignore`.
- Add docs, tools, scripts, and reports selectively.
- Commit a baseline.
- Tag the baseline.
- Keep the backup snapshot as an external recovery point.

## Scenario B - HML is not Git but should become Git
- Require human approval first.
- Keep the backup snapshot.
- Run `git init` only after approval.
- Apply `.gitignore`.
- Create the first baseline commit.
- Add a remote only after the baseline is stable.

## Scenario C - HML is inside another repo
- Do not initialize a new Git repository here.
- Align provenance with the parent repository.
- Treat this workspace as a nested operational subtree until the owner decides.

## Scenario D - Git is corrupted
- Preserve `.git`.
- Back up before trying any repair.
- Repair in a copy.
- Never run `reset --hard` directly on the operational workspace.

## Recommended scenario
- Scenario B.
- The audit shows Git is absent here, so the right move is a deliberate repository creation decision, not an automatic repair.
