# Bugfix Workflow

## When to use
Use this playbook when the task matches `bugfix_workflow`.

## Expected input
- Objective
- Minimal context
- Allowed files
- Forbidden files
- Risk level

## Steps
1. Inspect only relevant files.
2. Create a minimal plan.
3. Apply the smallest safe change.
4. Validate offline.
5. Prepare rollback notes.
6. Capture candidate memory.

## Validation
- Syntax checks
- Allowed tests
- Dry-run output

## Rollback
- Revert the patch.
- Restore prior known-good behavior.

## Risks
- Over-broad edits
- Hidden dependency drift
- Security regressions

## Evidence
- Commands run
- Files changed
- Validation output

## Candidate memory
- Save the problem, cause, fix, validation, rollback, stack, risk, and commit.
