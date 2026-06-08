#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROPOSALS = ROOT / 'reports' / 'composio_plugin' / 'change_proposals'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Revisão de proposals de mudança')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('proposal_id', nargs='?')
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    items = sorted(PROPOSALS.glob('*.json'))
    if ns.proposal_id:
        items = [p for p in items if ns.proposal_id in p.stem]
    for item in items:
        data = json.loads(item.read_text(encoding='utf-8'))
        print(f"{data.get('proposal_id')} | {data.get('status')} | {data.get('problem')}")
    if not items:
        print('Nenhuma proposta encontrada.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
