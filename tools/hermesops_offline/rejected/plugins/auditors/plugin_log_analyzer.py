#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description='Analisador de logs sanitizados')
    parser.add_argument('--path', required=True)
    parser.add_argument('--dry-run', action='store_true')
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    path = Path(ns.path)
    findings = []
    counter = Counter()
    for file in sorted(path.glob('*.jsonl')):
        for line in file.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except Exception:
                findings.append(f'{file}: linha não JSON')
                continue
            counter[event.get('message', 'sem mensagem')] += 1
            if event.get('status') in {'blocked', 'error'}:
                findings.append(f"{file}: tentativa bloqueada ou erro -> {event.get('message', '')}")
    print('Achados:')
    if not findings:
        print('0')
    else:
        for item in findings:
            print(f'- {item}')
    print('Resumo recorrências:')
    for msg, count in counter.most_common(5):
        print(f'- {msg}: {count}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
