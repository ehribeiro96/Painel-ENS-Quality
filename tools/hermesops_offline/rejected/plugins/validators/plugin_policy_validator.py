#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plugins.plugin_registry import load_registry

ALLOWED_STATUS = {'disabled', 'available', 'configured', 'authenticated', 'hml_ready', 'enabled', 'blocked', 'error'}
ALLOWED_RISK = {'low', 'medium', 'high'}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validador de políticas de plugins')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--path', default=str(ROOT / 'plugins' / 'plugin_registry.yaml'))
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    registry = load_registry(Path(ns.path))
    issues = []
    for p in registry.get('plugins', []):
        if p.get('status') not in ALLOWED_STATUS:
            issues.append(f"{p.get('id')}: status inválido")
        if p.get('risk_level') not in ALLOWED_RISK:
            issues.append(f"{p.get('id')}: risk_level inválido")
        if p.get('type') == 'external_connector' and p.get('environment') == 'test' and p.get('status') == 'enabled':
            issues.append(f"{p.get('id')}: plugin externo não pode ficar enabled em test")
    if issues:
        print('\n'.join(issues))
        return 2
    print('Política de plugins validada com sucesso.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
