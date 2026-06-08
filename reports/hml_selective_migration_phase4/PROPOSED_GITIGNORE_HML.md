# Proposed HML `.gitignore`

> Proposal only. Do not apply automatically in this phase.

```gitignore
# Secrets
.env
.env.*
!.env.example
!.env.hml.example
secrets/
tokens/
credentials/
*.pem
*.key
*.pfx
*.p12
*.crt
*.cer
*.der

# Python
__pycache__/
*.py[cod]
.venv/
venv/
env/
.pytest_cache/

# Node
node_modules/
dist/
build/
release/
out/
.vite/
.turbo/
*.tsbuildinfo

# Logs/runtime
*.log
*.jsonl
runtime_logs/
audit_logs/
sanitized_logs/
change_proposals/

# Local exports/staging
exports/
*_staging/
*_release/

# Recovery
_recovery/
```

## Application guidance
- Apply only after a human confirms whether this workspace will become a tracked Git baseline.
- Do not overwrite any existing `.gitignore` without review.
