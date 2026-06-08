#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports' / 'composio_plugin' / 'change_proposals'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Cria proposta de mudança a partir de finding')
    parser.add_argument('--finding', required=False, default='finding genérico')
    parser.add_argument('--area', default='plugins')
    parser.add_argument('--dry-run', action='store_true')
    ns = parser.parse_args(argv)
    proposal = {
        'proposal_id': f"proposal-{uuid.uuid4().hex[:8]}",
        'source_log_ids': [],
        'created_at': datetime.now(timezone.utc).isoformat(),
        'area': ns.area,
        'problem': ns.finding,
        'evidence': [],
        'proposed_change': 'Revisar política e documentação, sem auto-apply.',
        'files_affected': [],
        'risk_level': 'medium',
        'validation_plan': ['dry-run', 'review humana'],
        'rollback_plan': ['reverter proposta não aprovada'],
        'human_review_required': True,
        'status': 'candidate',
    }
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{proposal['proposal_id']}.json"
    path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(path)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
