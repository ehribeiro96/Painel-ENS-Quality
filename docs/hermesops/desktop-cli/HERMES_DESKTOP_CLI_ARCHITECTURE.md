# Hermes Desktop CLI Architecture

## Overview
Hermes Desktop is treated as the interactive shell UI. The actual execution backend remains the WSL Ubuntu Hermes installation. The wrapper layer standardizes cwd, logging, project selection, and rollback behavior without modifying the installed binary.

## Flow
1. User launches Desktop in Windows.
2. Desktop resolves Hermes in WSL.
3. Wrapper validates cwd and project root.
4. Wrapper enters `/home/ribeiro/Build_Mod/HermesOps`.
5. Hermes runs there and writes logs to `reports/desktop_cli/runtime_logs/`.

## Safety constraints
- Never start in `System32`.
- Never edit Program Files or the installed app.
- Never expose `.env` or credential files.
- Keep rollback artifacts in the repo, not in the app install.
