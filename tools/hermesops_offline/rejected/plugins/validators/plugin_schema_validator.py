#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validador de schemas JSON')
    parser.add_argument('--path', default=str(Path(__file__).resolve().parents[2] / 'plugins' / 'schemas'))
    parser.add_argument('--dry-run', action='store_true')
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    path = Path(ns.path)
    issues = []
    for file in sorted(path.glob('*.json')):
        try:
            data = json.loads(file.read_text(encoding='utf-8'))
            if data.get('type') != 'object':
                issues.append(f'{file}: type deve ser object')
        except Exception as exc:
            issues.append(f'{file}: JSON inválido -> {exc}')
    if issues:
        print('\n'.join(issues))
        return 2
    print('Schemas JSON validados com sucesso.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
