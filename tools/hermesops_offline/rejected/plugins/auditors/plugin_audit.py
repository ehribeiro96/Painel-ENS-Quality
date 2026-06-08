#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plugins.plugin_registry import load_registry


def main(argv=None):
    parser = argparse.ArgumentParser(description='Auditoria offline de plugins')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--path', default=str(ROOT / 'plugins' / 'plugin_registry.yaml'))
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    registry = load_registry(Path(ns.path))
    issues = []
    for p in registry.get('plugins', []):
        for key in ('policy_path', 'logging_policy_path', 'audit_policy_path'):
            if not p.get(key):
                issues.append(f"{p.get('id')}: campo ausente {key}")
    if issues:
        print('\n'.join(issues))
        return 2
    print('Auditoria de plugins concluída com sucesso.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
